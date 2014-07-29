#!/usr/bin/env python3


import argparse
from datetime import timedelta, datetime
from glob import glob
from matplotlib import pyplot
from time import strptime, mktime


def OpenFile(InputFile):
    """Try to open the data file, raise an error if opening fails"""
    try:
        InputData = open(InputFile)
    except IOError as e:
        print("Got IOError, '{0}: {1}'".format(e.errno, e.strerror))
    else:
        return(InputData)


def GetTime(TimeType, PmSuspendFile):
    """Return a list of timestamps that the computer was suspended or resumed
    on. If the TimeType parameter is 'suspend', search for suspend string,
    if it is 'resume' search for resume string, cut the lines at
    DateFieldLength value
    """
    DataFile = OpenFile(PmSuspendFile)
    Time = list()

    for line in DataFile:
        if TimeType == 'suspend':
            if 'Running hooks for suspend' in line:
                Time.append(line[:DateFieldLength])
        elif TimeType == 'resume':
            if 'Running hooks for resume' in line:
                Time.append(line[:DateFieldLength])

    return(Time)


def GetBatteryData(BatteryChargeFile):
    """Read the available battery charging/discharging data from the system,
    this relies on the file format by upowerd, located in
    /var/lib/upower/history-charge*.dat file
    """
    ChargeFile = OpenFile(BatteryChargeFile)
    TimeBatteryCharge = list()

    for line in ChargeFile:
        a, b, c = line.split()
        a = datetime.fromtimestamp(int(a)).strftime('%d.%m.%Y %H:%M:%S')
        TimeBatteryCharge.append([a, b, c])

    return(TimeBatteryCharge)


def PrintBatteryConsole(BatteryChargeFile):
    """Print out the gathered battery charging/discharging information"""
    ChargeInfo = GetBatteryData(BatteryChargeFile)
    Time = list()
    Battery = list()
    State = list()

    for elem in ChargeInfo:
        Time.append(elem[0])
        Battery.append(elem[1])
        State.append(elem[2])

    print('{0:5}\t{1:20}\t{2:10}\t{3:20}'.format('Index', 'Time',
                                                 'Percentage', 'State'))
    if len(Time) == len(Battery) and len(Time) == len(State):
        for index, (a, b, c) in enumerate(zip(Time, Battery, State)):
            print('{0:5}\t{1:20}\t{2:10}\t{3:20}'.format(index, a, b, c))


def GetDuration(PmSuspendFile):
    """Calculate the time the computer spent in suspend, returns Duration,
    SuspendTime and TimeDelta
    """
    Duration = list()
    SuspendTime = GetTime('suspend', PmSuspendFile)
    ResumeTime = GetTime('resume', PmSuspendFile)

    for index, (a, b) in enumerate(zip(SuspendTime, ResumeTime)):
        elema = mktime(strptime(a, DateFormat))
        elemb = mktime(strptime(b, DateFormat))
        elemc = timedelta(seconds=elemb - elema)
        Duration.append(elemc)
        """Reformat the dates so they match those we use for battery
        information display"""
        SuspendTime[index] = datetime.fromtimestamp(int(elema)).strftime(
            '%d.%m.%Y %H:%M:%S')
        ResumeTime[index] = datetime.fromtimestamp(int(elemb)).strftime(
            '%d.%m.%Y %H:%M:%S')

    return(Duration, SuspendTime, ResumeTime)


def PrintConsole(PmSuspendFile):
    """Print the gathered info out to console"""
    SuspendDuration, SuspendTime, ResumeTime = GetDuration(PmSuspendFile)

    if len(SuspendTime) == len(ResumeTime):

        print('{0:5}\t{1:20}\t{2:20}\t{3:10}'.format('Index', 'Suspend time',
              'Resume time', 'Duration'))

        for index, (suspend, resume, duration) in enumerate(
                zip(SuspendTime, ResumeTime, SuspendDuration)):
            print('{0:5}\t{1:20}\t{2:20}\t{3:10}'.format(index, suspend,
                                                         resume,
                                                         str(duration)))
    else:
        print("The length of SuspendTime and ResumeTime lists differs!")


def DrawGraph(PmSuspendFile):
    """Draw a suspend graph using matplotlib"""
    SuspendDuration, SuspendTime, ResumeTime = GetDuration(PmSuspendFile)
    NewDuration = list()
    NewSuspendTime = list()

    for (elema, elemb, elemc) in zip(SuspendDuration, SuspendTime, ResumeTime):
        """y is NewDuration, x is NewSuspendTime
        insert the values for y twice in a row in order to get the same data
        points for suspend and resume x point
        """
        NewDuration.append(datetime.strptime(str(elema), '%H:%M:%S'))
        NewDuration.append(datetime.strptime(str(elema), '%H:%M:%S'))
        NewSuspendTime.append(datetime.strptime(elemb, '%d.%m.%Y %H:%M:%S'))
        NewSuspendTime.append(datetime.strptime(elemc, '%d.%m.%Y %H:%M:%S'))

    pyplot.plot(NewSuspendTime, NewDuration)
    pyplot.show()


def DrawBatteryGraph(BatteryChargeFile):
    """Draw a battery graph using matplotlib"""
    ChargeInfo = GetBatteryData(BatteryChargeFile)
    Time = list()
    Battery = list()

    for elem in ChargeInfo:
        Time.append(datetime.strptime(elem[0], '%d.%m.%Y %H:%M:%S'))
        Battery.append(elem[1])

    pyplot.plot(Time, Battery)
    pyplot.show()


def DrawAllGraphs(BatteryChargeFile, PmSuspendFile):
    """Draw both the battery charge and the suspend graph"""
    ChargeInfo = GetBatteryData(BatteryChargeFile)
    Time = list()
    Battery = list()
    TimeCompare = list()

    for elem in ChargeInfo:
        Time.append(datetime.strptime(elem[0], '%d.%m.%Y %H:%M:%S'))
        TimeCompare.append(datetime.strptime(elem[0][:10], '%d.%m.%Y'))
        Battery.append(elem[1])

    pyplot.subplot(2, 1, 1)
    pyplot.plot(Time, Battery)

    SuspendDuration, SuspendTime, ResumeTime = GetDuration(PmSuspendFile)
    NewDuration = list()
    NewSuspendTime = list()

    for index, (elema, elemb, elemc) in enumerate(zip(SuspendDuration,
                                                  SuspendTime, ResumeTime)):

        vala = datetime.strptime(elemb[:10], '%d.%m.%Y')
        valb = datetime.strptime(elemc[:10], '%d.%m.%Y')

        if vala in TimeCompare:
            NewSuspendTime.append(datetime.strptime(elemb,
                                                    '%d.%m.%Y %H:%M:%S'))
            NewDuration.append(datetime.strptime(str(elema), '%H:%M:%S'))

        if valb in TimeCompare:
            NewSuspendTime.append(datetime.strptime(elemc,
                                                    '%d.%m.%Y %H:%M:%S'))
            NewDuration.append(datetime.strptime(str(elema), '%H:%M:%S'))

    pyplot.subplot(2, 1, 2)
    pyplot.plot(NewSuspendTime, NewDuration)
    pyplot.show()


def DoIt():
    """
    Set up the available program options
    Call the proper functions with proper parameters depending on user
    input
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--all', dest='All', help='Draw both the '
                        'battery and suspend graph', action='store_true')
    parser.add_argument('-b', '--battery', dest='Battery', help='Show the '
                        'battery charging/discharging information',
                        action='store_true')
    parser.add_argument('-d', '--date', dest='DateFormat', help='Specify '
                        'the date format', default='%a %b %d %H:%M:%S %Z %Y',
                        type=str, action='store')
    parser.add_argument('-f', '--file', dest='PmSuspendFile', help='Specify '
                        'which file name to parse',
                        default='/var/log/pm-suspend.log', type=str,
                        action='store')
    parser.add_argument('-l', '--length', dest='DateFieldLength',
                        help='Specify the length of the date field in the '
                        'file', default=29, type=int, action='store')
    parser.add_argument('-o', '--output', dest='Output', help='Specify the '
                        'output destination', default='console', type=str,
                        action='store')

    args = parser.parse_args()

    if not args.DateFormat:
        parser.print_help()
    else:
        global DateFormat
        DateFormat = args.DateFormat

    if not args.DateFieldLength:
        parser.print_help()
    else:
        global DateFieldLength
        DateFieldLength = args.DateFieldLength

    if args.All:
        if args.Output == 'graph':
            BatteryInfoFile = glob('/var/lib/upower/history-charge-*.dat')
            DrawAllGraphs(BatteryInfoFile[0], args.PmSuspendFile)
        elif args.Output == 'console':
            BatteryInfoFile = glob('/var/lib/upower/history-charge-*.dat')
            PrintConsole(args.PmSuspendFile)
            PrintBatteryConsole(BatteryInfoFile[0])
    else:
        if args.Battery:
            try:
                BatteryInfoFile = glob('/var/lib/upower/history-charge-*.dat')
            except IOError as e:
                print("Got IOError, '{0}: {1}'".format(e.errno, e.strerror))
            else:
                if args.Output == 'console':
                    PrintBatteryConsole(BatteryInfoFile[0])
                elif args.Output == 'graph':
                    DrawBatteryGraph(BatteryInfoFile[0])
        else:
            if args.Output == 'console':
                PrintConsole(args.PmSuspendFile)
            elif args.Output == 'graph':
                DrawGraph(args.PmSuspendFile)


if __name__ == "__main__":
    DoIt()
