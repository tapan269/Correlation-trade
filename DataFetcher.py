# This file contains the data fetcher function to retrieve raw data using pandas web reader #
import enum
import pandas
import pandas_datareader
import datetime as dt
from utils import timeSeries

class SYMBOLS(enum.Enum):
    ''' here I have the ticker Name used for the source'''
    # Index
    SPX = '^GSPC'
    # Bonds
    TLT = 'TLT'


class DATA_SOURCE(enum.Enum):
    YAHOO = 'yahoo'


class MarketDataObject(object):

    def __init__(self, ticker, source, name=''):
        self.ticker = ticker
        self.source = source
        self.name = name

    def getSource(self):
        '''returns the source value'''
        return self.source.value

    def getTicker(self):
        '''return the name of the ticker'''
        return self.ticker.value


SYMBOLS_MAPPING = {
    SYMBOLS.SPX: lambda: MarketDataObject(ticker=SYMBOLS.SPX, source=DATA_SOURCE.YAHOO),
    SYMBOLS.TLT: lambda: MarketDataObject(ticker=SYMBOLS.TLT, source=DATA_SOURCE.YAHOO)

}


class WebReaderAPI(object):

    def __init__(self):
        self.connection = None

    def getAPIConnection(self):
        ''' reuturns the varios connections required'''
        return pandas_datareader.data

    def processData(self, data):
        '''processes the data in { signal : { date : value }} format so its easier to manipulate later'''
        data.index = data.index.map(lambda x: x.date())  # convert to datetime for later usage
        data = data.to_dict()
        return data

    def getData(self, ticker, start_date, end_date, **kwargs):
        ''' returns the data for time series '''
        connection = self.connection if self.connection else self.getAPIConnection()
        data = connection.DataReader(name=ticker.getTicker(), data_source=ticker.getSource(), start=start_date,
                                     end=end_date)
        return self.processData(data)


class MarketDataProcessor(object):

    def __init__(self, ticker, connection, **kwargs):
        self.ticker = SYMBOLS_MAPPING[ticker]()
        self.connection = connection
        self.setupCache()

    def setupCache(self):
        ''' setups cache for usage '''
        # here we can also use cache from local, skipping this for now
        self._cache = self.getMarketData(self.ticker, dt.date(1970, 1, 1), dt.date.today())

    def value(self, signal, date):
        ''' returns the value on a particular date '''

        assert signal in self._cache, "Market data not available for  signal {0} as of date {1}".format(signal, date)
        assert date in self._cache[signal], "Market data not available for  signal {0} as of date {1}".format(signal,
                                                                                                              date)
        return self._cache[signal][date]

    def timeseries(self, signal, startOrCalendarOffset, end, **kwargs):
        ''' get the series of signal for a particular date
        Note- it has equality so we include end and start '''

        assert isinstance(startOrCalendarOffset,
                          (int, dt.date)), 'Incorrect Start date entry. Please use datetime or (-)ve int'
        assert signal in self._cache, "Market data not available for  signal {0}".format(signal)

        if isinstance(startOrCalendarOffset, int):
            start = end + dt.timedelta(days=startOrCalendarOffset)
        else:
            start = startOrCalendarOffset

        rawData = self._cache[signal]
        tsdata = {date: rawData[date] for date in rawData if start <= date <= end}
        return timeSeries(tsdata)

    def series(self, signal, startOrCalendarOffset, end, **kwargs):
        ts = self.timeseries(signal, startOrCalendarOffset, end, **kwargs)
        return ts.toPandasSeries()

    def dates(self, signal, startOrCalendarOffset, end, **kwargs):
        ts = self.timeseries(signal, startOrCalendarOffset, end, **kwargs)
        return ts.getDates()

    def getMarketData(self, ticker, start_date, end_date, **kwargs):
        '''get the market data using the pandas api '''
        return self.connection.getData(ticker, start_date, end_date, **kwargs)

class createObservables(object):

    def __init__(self,connection):
        self.connection = connection
        self._observables = {}

    def OBSERVABLES(self):
        return self._observables

    def addObservable(self,symbol,symbolicName=None):
        ''' adds the market data observable '''
        MarketObservableName = symbolicName if symbolicName else symbol.name
        assert MarketObservableName not in self._observables, 'Signal name {0} already present in Observables'.format(MarketObservableName)
        MarketObservable = MarketDataProcessor(symbol,connection=self.connection)
        self._observables.update({MarketObservableName:MarketObservable})

    def getObservable(self,symbolicName):
        '''returns a specific observable '''
        return self._observables.get(symbolicName, None)

OBSERVABLES = createObservables(connection=WebReaderAPI())

if __name__ == '__main__':
    # OBSERVABLES = []
    # symbol = SYMBOLS_MAPPING[SYMBOLS.SPX]
    # clazz = MarketDataProcessor(symbol(), WebReaderAPI())
    # print(clazz.series('Close', -5, dt.date(2022, 7, 8)))
    OBSERVABLES.addObservable(SYMBOLS.SPX,symbolicName='SPX')
    OBSERVABLES.addObservable(SYMBOLS.TLT,symbolicName='TLT')
    results=OBSERVABLES.OBSERVABLES()
    clazz = results['SPX']
    print(clazz.series('Close', -5, dt.date(2022, 7, 8)))
    print(clazz.dates('Close', -5, dt.date(2022, 7, 8)))
    print(clazz.value('Close', dt.date(2022, 7, 8)))