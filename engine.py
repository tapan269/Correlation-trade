#This is base engine to be used in all the rule code
from log import log
from collections import defaultdict
import pandas as pd
from schedules import IndexSchedule
from DataFetcher import timeSeries
import datetime as dt

def setState(func):
    """ update in state the value of signal at t for the index"""
    def wrapper(self, date, **kwargs):
        output = func(self, date)
        self.state.setValue(func.__name__, date, output)
        return output
    return wrapper


class IndexState(object):
    """ container to hold the state of the index """
    def __init__(self):
        self._state = defaultdict(dict)

    def setValue(self, signal, date, value):
        self._state[signal][date] = value

    def getValue(self, signal, date):
        return self._state[signal][date]

    def SignaltimeSeries(self,signal,start=dt.date(1970,1,1), end=dt.date(2300,1,1)):
        ''' get series data from state for a particular signal '''
        signalTs = self._state[signal]
        tsdata = {date: signalTs[date] for date in signalTs if start <= date <= end}
        return timeSeries(tsdata)

class BaseRules(object):

    def __init__(self,config,**kwargs):
        ''' base init '''
        self.config = config
        self.setup()

    def schedule(self):
        ''' Base function where schedules can be masde'''
        raise NotImplementedError('No schedule is defined. Please check')

    def setup(self):
        """ setup basic variable required for index """
        # Setup Logging
        self.logger = log.setupLogger()
        self.config['logger'] = self.logger

        # setup Observable
        self.observable = self.config['OBSERVABLES']

        # Setup Schedules
        self.baseDate = self.config['BaseDate']
        self.scheduler = IndexSchedule()
        self.schedule() #setup any custom schedule required by the strategy
        self.config['scheduler'] = self.scheduler


        # Setup State
        self.state = IndexState()
        self.config['state'] = self.state  # add the variable in config to be passed onto various modules via config

    def value(self, signal,date,fieldToObserve='Close'):
        """ returns the value of the given signal as of given date"""
        if signal in self.observable:
            return self.observable[signal].value(fieldToObserve,date)
        return self.state.getValue(signal, date)

    def series(self,signal,startDateOrCalendarOffset,endDate,fieldToObserve='Close'):
        ''' return the series of market observable or grid '''
        if signal in self.observable:
            return self.observable[signal].series(fieldToObserve, startDateOrCalendarOffset,endDate)
        return self.state.SignaltimeSeries(signal, startDateOrCalendarOffset,endDate).toPandasSeries()

    def run(self, date):
        """ runs the index from base date till date"""
        dateList = self.scheduler.dateList('calculation', self.baseDate, date)
        for d in dateList:
            level = self.index_level(d)
        self.logger.info("Calculated Index level from date %s to date %s with resulting index level of %s", dateList[0],
                         dateList[-1], level)
        return
