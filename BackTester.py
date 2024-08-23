#python Modules
import datetime as dt
#This is a test
# index modules
import math
from engine import BaseRules, setState


class BackTester(BaseRules):

    def __init__(self, config):
        super(BackTester,self).__init__(config)

    def schedule(self):
        ''' create the schedule to be used '''

        spx = self.observable['SPX']
        spxBusinessDays = spx.dates('Close',dt.date(2006,1,1),dt.date.today())
        self.scheduler.createSchedule('calculation_infinite', spxBusinessDays)
        self.scheduler.createSchedule('calculation', self.scheduler.cropSchedule('calculation_infinite',self.config['BaseDate']))
        self.scheduler.createSchedule('rebalance', self.scheduler.cropSchedule('calculation_infinite',self.config['BaseDate'],include_start=False)) #rebalance starts a day later


    @setState
    def AssetVol(self, date):
        """ creates asset vol base on correlation lag period  """
        assetVol = {}
        end_date = self.scheduler.offset('calculation_infinite', date, self.config['correlationLag'])
        start_date = self.scheduler.offset('calculation_infinite', date, self.config['volLookBack'])

        for underlying in self.config['Underlyings']:
            underlyingTs = self.series(underlying,start_date,end_date)
            returnsTs = underlyingTs/underlyingTs.shift(1).dropna()
            annualVol = math.sqrt(returnsTs.std()*252)
            assetVol[underlying] = annualVol

        return assetVol

    @setState
    def AssertCorrelation(self,date):
        """ get the correlation of assets """

        returnSeries = []
        end_date = self.scheduler.offset('calculation_infinite', date, self.config['correlationLag'])
        start_date = self.scheduler.offset('calculation_infinite', date, self.config['volLookBack'])

        for underlying in self.config['Underlyings']:
            underlyingTs = self.series(underlying,start_date,end_date)
            returnsTs = (underlyingTs/underlyingTs.shift(1) - 1).dropna()
            returnSeries.append(returnsTs)

        correlation = returnSeries[0].corr(returnSeries[1])
        return correlation

    @setState
    def AssetReturn(self,date):
        ''' compute the return of asset '''
        AssetReturns = {}
        prevT = self.scheduler.offset('calculation_infinite', date,-1)
        for underlying in self.config['Underlyings']:
            levelT = self.value(underlying,date)
            levelPrevT = self.value(underlying,prevT)
            AssetReturns[underlying] = levelT/levelPrevT -1.
        return AssetReturns

    @setState
    def TargetLeverage(self,date):
        ''' determine the leverage of the index '''

        if date == self.baseDate:
            return [0.,0.]

        #calculate target leverage for consituets ##
        assetReturns = self.AssetReturn(date)
        underlying_1,underlying_2 = self.config['Underlyings']
        correlation = self.AssertCorrelation(date)
        assetVol = self.AssetVol(date)

        #here we calculate beta and then find difference between expected return and realized return of 2 the underlying
        leverage_1 = self.config['DailyLeverage'] * (correlation*\
                     (assetVol[underlying_2]/assetVol[underlying_1])*\
                     assetReturns[underlying_1]-\
                     assetReturns[underlying_2])

        leverage_2 = self.config['DailyLeverage'] * (correlation * \
                                                     (assetVol[underlying_1] / assetVol[underlying_2]) * \
                                                     assetReturns[underlying_2] - \
                                                     assetReturns[underlying_1])
        return [leverage_1,leverage_2]

    @setState
    def TargetUnits(self,date):
        ''' calculate the total units to be held in the portfolio '''
        if date == self.baseDate:
            return [0.,0.]
        TargetUnits = []
        prevT = self.scheduler.offset('calculation_infinite',date,-1)
        indexlevelPrevT = self.value('index_level',prevT)
        TargetLeverage = self.TargetLeverage(date)
        for i, underlying in enumerate(self.config['Underlyings']):
            UnderlyingTargetUnits = indexlevelPrevT*min(self.config['MaxLeverage'], max(-self.config['MaxLeverage'],TargetLeverage[i]))/ self.value(underlying,date)
            TargetUnits.append(UnderlyingTargetUnits)
        return TargetUnits

    @setState
    def fee(self,date):
        ''' returns the total fee on the index '''
        return 0.0

    @setState
    def index_level(self,date):
        """ returns index level for the strategy """


        if date <= self.baseDate:
            return self.config['InitialIndexLevel']


        prevT = self.scheduler.offset('calculation_infinite',date,-1)
        indexlevelPrevT = self.value('index_level',prevT)
        TargetUnits = self.TargetUnits(prevT)
        fee = self.fee(date)
        ret = 0.0
        for i,underlying in enumerate(self.config['Underlyings']):
            levelT = self.value(underlying,date)
            levelPrevT = self.value(underlying,prevT)
            ret += TargetUnits[i] * (levelT-levelPrevT)

        indexlevel = indexlevelPrevT + ret - fee
        self.logger.info("Calculated Index level as of date %s is %s", date, indexlevel)
        return indexlevel



if __name__ == '__main__':

    from SPX_TLT_Spread import CONFIG
    import datetime
    index = BackTester(CONFIG)
    endDate = datetime.date(2022,7,6)
    index.run(endDate)
    level = index.series('index_level', CONFIG['BaseDate'],endDate)
    level.plot()

