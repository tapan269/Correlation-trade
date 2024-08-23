from collections import OrderedDict
import pandas
import datetime
import pandas.tseries.offsets as pdo

def WDayRollBack(date):
    '''returns the latest week day in the calendar year '''
    return pdo.BDay().rollback(date).date()

def firstCalDayOfMonth(date):
    ''' returs the first of the month '''
    return datetime.date(date.year, date.month, 1)

def lastCalDayOfPrevMonth(date):
    ''' returns the last calendar day of the month '''
    return firstCalDayOfMonth(date) - datetime.timedelta(days=1)

def lastWDayofPrevMonth(date):
    ''' retuens the last WDay of prev Month '''
    return WDayRollBack(lastCalDayOfPrevMonth(date))


class timeSeries(object):

    def __init__(self, dictOfDateAndValue, **kwargs):
        self._rawTS = dictOfDateAndValue
        self._dates = sorted(self.getDates())
        self.ts = OrderedDict({date: self._rawTS[date] for date in self._dates})

    def items(self):
        ''' returns the iter items on time series '''
        return self.ts.items()

    def __len__(self):
        ''' returns the lenght of timeSeries '''
        return len(self._dates)

    def lastDate(self):
        ''' returns the last date of the curve'''
        return self._dates[-1]

    def firstDate(self):
        '''returns the first date on the curve '''
        return self._dates[0]

    def lastValue(self):
        ''' returns the last available value on the curve '''
        return self.ts[self.lastDate()]

    def firstValue(self):
        ''' returns the first available value on the curve '''
        return self.ts[self.firstDate()]

    def toPandasSeries(self):
        return pandas.Series(self.ts)

    def getDates(self):
        return list(set(self._rawTS.keys()))

    def Range(self,startDate,endDate):
        ''' returns the data within a range '''
        curveRange = {date: value for date, value in self.ts.items() if startDate <= date <= endDate}
        return timeSeries(dictOfDateAndValue=curveRange)


if __name__ == '__main__':
    import datetime as dt
    data = {dt.date(2020,1,1): 1,dt.date(2020,1,6): 5}
    ts = timeSeries(data)
    print(len(ts))
    for k,v in ts.items():
        print(k,v)