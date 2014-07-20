#!/usr/bin/env python3


from time import strptime, mktime
from datetime import timedelta
import argparse


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


def GetDuration(PmSuspendFile):
    """Calculate the time the computer spent in suspend, returns Duration,
    SuspendTime and TimeDelta
    """
    Duration = list()
    SuspendTime = GetTime('suspend', PmSuspendFile)
    ResumeTime = GetTime('resume', PmSuspendFile)

    for (a, b) in zip(SuspendTime, ResumeTime):
        elema = mktime(strptime(a, DateFormat))
        elemb = mktime(strptime(b, DateFormat))
        elemc = timedelta(seconds=elemb - elema)
        Duration.append(elemc)

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

if __name__ == "__main__":
    DoIt()
