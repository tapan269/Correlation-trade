# create a schedule for various dates
import bisect
import pandas as pd
import datetime as dt

class IndexSchedule(object):

    def __init__(self):
        self.schedules = dict()

    def getSchedule(self, schedule):
        """ return the schedule object for a given schedule"""
        return self.schedules[schedule]

    def _getIndex(self,t,schedule):
        ''' return the index of the t in schedule where shcedule is a list '''
        isDateInSchedule = t in schedule
        idx = bisect.bisect_right(schedule, t)
        idx = idx-2 if isDateInSchedule else idx-1
        return idx

    def Before(self, t, schedule):
        """returns a date which is before the given date """
        idx = self._getIndex(t,schedule)
        return schedule[idx]

    def OnOrBefore(self, t, schedule):
        """ Get the date which is on or Before on a given schedule """
        if t in schedule : return t
        return self.Before(t, schedule)

    def offset(self,schedule,t,offset):
        '''offset the day on a given signal and t '''
        scheduleObject = self.schedules[schedule]
        idx = self._getIndex(t,scheduleObject)
        idxOfOffest = idx + offset + 1
        assert idxOfOffest >=0, 'offset is before the schedule {0} start date'.format(schedule)
        assert idxOfOffest < len(scheduleObject), 'Offset is post shhedule {0}'.format(schedule)
        return scheduleObject[idxOfOffest]

    def createSchedule(self, name, dates):
        """ generates the schedule(generator) for various dates"""
        schedule = [date for date in dates] #TODO: Find a better way. This will consume memory
        assert len(set(schedule)) == len(schedule), "Duplicate dates found in Calendar." \
                                                    "Please check "
        schedule.sort()
        self.schedules[name] = schedule

    def cropSchedule(self,schedule,start_date=None,end_date=dt.date(2023,1,1),include_start=True):
        ''' crops the schedule within dates '''
        scheduleObject = self.schedules[schedule]
        start_date_idx = self._getIndex(start_date,scheduleObject) + (1 if include_start else 2 )
        end_date_idx = self._getIndex(end_date,scheduleObject) + 2
        return scheduleObject[start_date_idx:end_date_idx]

    def inSchedule(self, schedule, t):
        """ checks whether a date is in a particular schedule or not """
        scheduleObject = self.schedules.get(schedule, None)
        assert scheduleObject, "Schedule not Found. Please check"
        return t in scheduleObject

    def nearestDate(self, schedule, t, convention):
        """ returns the nearest date for t based of an offset """
        scheduleObject = self.schedules[schedule]
        return convention(t, scheduleObject)

    def dateList(self, schedule, startdate, endDate):
        """ return the date list between the start and end date"""
        scheduleObject = self.getSchedule(schedule)
        return [date for date in scheduleObject if startdate <= date <= endDate]

if __name__ == '__main__':
    import datetime as dt
    dates = pd.date_range(dt.date(2022,1,1),dt.date(2022,7,30)).date
    scheduler = IndexSchedule()
    scheduler.createSchedule('calculation',dates)
    scheduler.createSchedule('rebalance',[dt.date(2021,1,1),dt.date(2022,1,1),dt.date(2023,1,1)])
    # print(scheduler.offset('calculation',dt.date(2022,7,5),-1))
    # print(scheduler.offset('calculation',dt.date(2022,7,5),1))
    # print(scheduler.nearestDate('rebalance', dt.date(2021,1,5), scheduler.OnOrBefore ))
    print(scheduler.cropSchedule('rebalance', dt.date(2021,1,1),dt.date(2022,1,10),True))