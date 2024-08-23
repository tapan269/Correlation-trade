import datetime as dt
from DataFetcher import SYMBOLS, OBSERVABLES
''' Below is the config for spread dispersion between spx and bond 
The hypothesis being the current correlation spread break will eventually 
converge to long term correlation i.e Mean Reversion is at PLAY'''

#TODO: Create a base strategy object with rule class and run feature so that later i can directly initiale the stratey and call run from top level. Skipping for now
# class BaseStrategy(object):
#
#     def __init__(self):
#         self.initialise()
#
#
#     def initialise(self):
#         raise NotImplementedError


CONFIG = {}
CONFIG['BaseDate'] = dt.date(2007,1,5)
CONFIG['RebalanceDate'] = []
CONFIG['Underlyings'] = ['SPX', 'TLT']
CONFIG['InitialIndexLevel'] = 100.
CONFIG['correlationLag'] = -1
CONFIG['volLookBack'] = -252
CONFIG['MaxLeverage'] = 2.
CONFIG['DailyLeverage'] = -10.
# Add Market data observables to be used later
OBSERVABLES.addObservable(SYMBOLS.SPX,symbolicName='SPX')
OBSERVABLES.addObservable(SYMBOLS.TLT,symbolicName='TLT')
CONFIG['OBSERVABLES']=OBSERVABLES.OBSERVABLES()





