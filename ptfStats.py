import math
import numpy as np
import datetime

import pandas
import pandas as pd

import utils

def logReturns(timeSeries):
    ''' returns the log Returns of the timeSeries'''
    priceTs = timeSeries.toPandasSeries()
    return np.log(priceTs/priceTs.shift(1)).dropna()

def pointsPerYear(timeSeries):
    ''' returns the number of points per year '''
    days = (timeSeries.lastDate() - timeSeries.firstDate()).days
    years = days/365
    return int(len(timeSeries)/years)

def periodReturn(timeSeries):
    ''' returns the return between the start and end period '''

    return timeSeries.lastValue()/timeSeries.firstValue() -1.

def annualReturn(timeSeries):
    ''' returns the non log annual return of timeseries '''

    netReturn = conditionalAnnualReturn(timeSeries)
    days = (timeSeries.lastDate()-timeSeries.firstDate()).days
    annualReturn = (1+netReturn)**(365./days)-1
    return annualReturn

def conditionalAnnualReturn(timeSeries):
    ''' return annual return if longer than 1 Yr else period return '''
    days = (timeSeries.lastDate()-timeSeries.firstDate()).days
    if days>366.:
        return annualReturn(timeSeries)
    else:
        return periodReturn(timeSeries)

def stdFromReturns(returns):
    ''' returns the standard devaitions of timeSeries '''
    return np.std(returns)


def annualVolatility(timeSeries):
    ''' return annual volatility of timeseries'''
    returns = logReturns(timeSeries)
    dailyVol = stdFromReturns(returns)
    annFactor = pointsPerYear(timeSeries)
    return math.sqrt(annFactor) * dailyVol

def sharpe(timeSeries):
    '''returns the sharpe ratio '''
    return annualReturn(timeSeries)/annualVolatility(timeSeries)

def maxDrawdown(timeSeries):
    ''''returns the max drow down on a given timeSeries '''

    drawdowns = []
    maxValue = None

    for _, value in timeSeries.items():
        if maxValue is None:
            maxValue = value
        else:
            maxValue = max(maxValue, value)
            drawdown = -(value/maxValue-1)
            drawdowns.append(drawdown)
    return max(drawdowns)


def interPretPeriod(period,startDate,endDate):
    '''' interpret the period to be used for name '''

    if isinstance(period, tuple):
        periodName = period[0]
        period = period[1]
    else:
        periodName = None
    if isinstance(period, int): #years 2021 etc
        year = period
        periodRange = [utils.WDayRollBack(datetime.date(year-1, 12, 31)), min(endDate, utils.WDayRollBack(datetime.date(year,12, 31)))]
    elif period == 'YTD':
        year = endDate.year
        periodRange = [utils.WDayRollBack(datetime.date(year-1, 12, 31)), endDate]
    elif period == 'MTD':
        periodRange = [utils.lastWDayofPrevMonth(endDate), endDate]
    elif period in ['All']:
        periodRange = [startDate, endDate]
    elif isinstance(period, list):
        assert len(period) == 2,'Please input start and end date'
        periodRange = [min(period[0], period[1]), max(period[0], period[1])]
    else:
        raise NotImplementedError('Period Range not defined')

    if periodName is None:
        if isinstance(period, list):
            periodName = '{}_{}'.format(period[0],period[1])
        else:
            periodName = str(period)
    return periodName, periodRange



formatPercentTwoDp = lambda v: '{:.2f}%'.format(v*100)
formatTwoDp = lambda v: '{:.2f}'.format(v)

MetricFunc = {  'Return': lambda timeSeries : conditionalAnnualReturn(timeSeries),
                'AnnualVolatility': lambda timeSeries : annualVolatility(timeSeries),
                'Sharpe': lambda timeSeries : sharpe(timeSeries),
                'MaxDrawDown': lambda timeSeries : maxDrawdown(timeSeries)
}

MetricFormatter = {
    'Return': formatPercentTwoDp,
    'AnnualVolatility':formatPercentTwoDp,
    'Sharpe': formatTwoDp,
    'MaxDrawDown':formatPercentTwoDp,
}

metrics = ['Return', 'AnnualVolatility', 'Sharpe', 'MaxDrawDown']


def perfStats(dictOfTimeSeries, periods, metrics=metrics):
    ''' calculates the performance stats of given timeSeries
        tupleOfTimeSeries in the format (name, startDate, end Date) '''
    assert isinstance(periods,list), 'Periods should be passed as a list'

    uniqueFirstDate = np.unique([timeSeries.firstDate() for timeSeries in dictOfTimeSeries.values()])
    uniqueLastDate = np.unique([timeSeries.lastDate() for timeSeries in dictOfTimeSeries.values()])

    if len(uniqueFirstDate) > 1:
        firstDate = max(uniqueFirstDate)
        print('There are different dates for timeSeries. Using common date %s'.format(firstDate))

    if len(uniqueLastDate) > 1:
        lastDate = max(uniqueLastDate)
        print('There are different dates for timeSeries. Using common date %s'.format(lastDate))

    metric2 = []

    for metric in metrics:
        metricName = metric
        metricFunc = MetricFunc[metric]
        metricFormatter = MetricFormatter[metric]
        metric2.append((metricName,metricFunc,metricFormatter))

    tableData = []

    for curveName, timeSeries in dictOfTimeSeries.items():
        # accumulate the relevant data for different periods
        periodNames = []
        for period in periods:
            periodName, periodRange = interPretPeriod(period,timeSeries.firstDate(),timeSeries.lastDate())
            periodNames.append(periodName)
            periodRangeTs = timeSeries.Range(*periodRange)

            #now calculate the different metrics
            for metricName, metricFunc, metricFormatter in metric2:
                metricResult = metricFunc(periodRangeTs)
                formattedResult = metricFormatter(metricResult)
                tableData.append([ metricName, curveName, periodName, formattedResult])

    table = pandas.DataFrame(tableData, columns = ['metricName', 'curveName', 'period', 'value'])
    table = table.set_index(['metricName', 'curveName', 'period']).unstack()

    table.columns = table.columns.droplevel(0)
    table.columns.name = None
    metricNames = [metricName for metricName, _ , _ in metric2]
    curveNames = list(dictOfTimeSeries)
    indices = pandas.MultiIndex.from_product([metricNames, curveNames])
    table = table.reindex(index=indices, columns=periodNames)

    return table



if __name__ == '__main__':
    import datetime as dt

    from DataFetcher import OBSERVABLES, SYMBOLS
    OBSERVABLES.addObservable(SYMBOLS.SPX,symbolicName='SPX')
    clazz = OBSERVABLES.getObservable('SPX')
    priceTs = clazz.timeseries('Close',dt.date(2019,1,5), dt.date(2022, 7, 8))
   # print(annualVolatility(priceTs))
    #print(sharpe(priceTs))
    table = perfStats({'SPX' : priceTs}, [2020, 2021,2022])