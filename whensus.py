#!/usr/bin/env python3


import argparse
from datetime import timedelta, datetime
from glob import glob
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

    print('{0:5}\t{1:25}\t{2:10}\t{3:20}'.format('Index', 'Time',
                                                 'Percentage', 'State'))
    if len(Time) == len(Battery) and len(Time) == len(State):
        for index, (a, b, c) in enumerate(zip(Time, Battery, State)):
            print('{0:5}\t{1:25}\t{2:10}\t{3:20}'.format(index, a, b, c))


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

        print('{0:5}\t{1:30}\t{2:30}\t{3:10}'.format('Index', 'Suspend time',
              'Resume time', 'Duration'))

        for index, (suspend, resume, duration) in enumerate(
                zip(SuspendTime, ResumeTime, SuspendDuration)):
            print('{0:5}\t{1:30}\t{2:30}\t{3:10}'.format(index, suspend,
                                                         resume,
                                                         str(duration)))
    else:
        print("The length of SuspendTime and ResumeTime lists differs!")


def DoIt():
    """
    Set up the available program options
    Call the proper functions with proper parameters depending on user
    input
    """
    parser = argparse.ArgumentParser()

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

    if args.Output == 'console' and args.PmSuspendFile:
        PrintConsole(args.PmSuspendFile)

    if args.Battery:
        try:
            BatteryInfoFile = glob('/var/lib/upower/history-charge-*.dat')
        except IOError as e:
            print("Got IOError, '{0}: {1}'".format(e.errno, e.strerror))
        else:
            PrintBatteryConsole(BatteryInfoFile[0])


if __name__ == "__main__":
    DoIt()
