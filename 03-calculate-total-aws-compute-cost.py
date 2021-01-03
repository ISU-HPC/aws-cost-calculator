#!/bin/env python3
import os
import datetime
import pymysql
from datetime import date, datetime, timedelta
import calendar
import time
from os.path import expanduser
import argparse 

# Create an ArgumentParser object to easily handle command-line options and
# auto-generate helpful CLI help when -h/--help flags are used.
parser = argparse.ArgumentParser(description='Calculate and report aggregate AWS costs for slurm computational jobs')

parser.add_argument('--defaults-analysis',
                    dest='defaults_analysis',
                    type=str,
                    help='MySQL connection file for analysis database')
parser.add_argument('--start',
                    dest='start',
                    type=str,
                    help='Start date for cost calculation (default: 30 days ago) (ignored if --days is used)')
parser.add_argument('--end',
                    dest='end',
                    type=str,
                    help='End date for cost calculation (default: 1 day ago) (ignored if --days is used)')
parser.add_argument('--monthly',
                    dest='monthly',
                    action='store_true',
                    help='If specified with --start and/or --end, calculate per-month costs within specified date range (ignored otherwise)')
parser.add_argument('--weekly',
                    dest='weekly',
                    action='store_true',
                    help='If specified with --start and/or --end, calculate per-week costs within specified date range (ignored otherwise)')
parser.add_argument('--daily',
                    dest='daily',
                    action='store_true',
                    help='If specified with --start and/or --end, calculate per-day costs within specified date range (ignored otherwise)')
parser.add_argument('-d', '--days',
                    dest='days',
                    metavar='N',
                    type=int,
                    help='Calculate costs for past N days')
parser.add_argument('--partition',
                    dest='partition',
                    type=str,
                    help='Limit analysis to jobs in the specified slurm partition')
parser.add_argument('-p', '--parsable',
                    dest='parsable',
                    action='store_true',
                    help='Output parsable CSV list for use by other applications (e.g., plotting)')
parser.add_argument('--with-headers',
                    dest='headers',
                    action='store_true',
                    help='Include header row.  Applies to both parsable and tabular output.')


# Parse the arguments provided by the user
args, leftovers = parser.parse_known_args()

home = expanduser("~")
defaults_file = home + "/.my.cnf.slurm-aws"
if args.defaults_analysis is not None:
    defaults_file = args.defaults_analysis
    pass

ndays = 30
if args.days is not None:
    ndays = args.days
    pass


dbcost = pymysql.connect(read_default_file=defaults_file)

cursorcost = dbcost.cursor()


# Generate output based on the CLI flags.  This is admittedly rough.

#
# First, consider when no CLI flags are given.  Output a table of costs for common times-of-interest.
#
if (args.start is None) and (args.end is None) and (args.days is None):
    # If no date info was specified, generate a table of common time intervals

    # Last 1 day pricing
    sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (dbid) WHERE jobinfo.enddate >= '" + (datetime.now()).strftime("%Y-%m-%d") + "' AND jobinfo.enddate <= '" + (datetime.now()).strftime("%Y-%m-%d")  + "'"
    if args.partition is not None:
        sql += " AND jobinfo.part = '" + args.partition + "'"
    cursorcost.execute(sql)
    data=cursorcost.fetchone()
    spot1 = "$0"
    reserved1 = "$0"
    if data[0]:
        reserved1=str('${:,.0f}'.format(data[0]/100))
    if data[1]:
        spot1=str('${:,.0f}'.format(data[1]/100))

    # Last 7 days pricing
    sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (dbid) WHERE jobinfo.enddate >= '" + (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d") + "' AND jobinfo.enddate <= '" + (datetime.now()).strftime("%Y-%m-%d")  + "'"
    if args.partition is not None:
        sql += " AND jobinfo.part = '" + args.partition + "'"
    cursorcost.execute(sql)
    data=cursorcost.fetchone()
    spot7 = "$0"
    reserved7 = "$0"
    if data[0]:
        reserved7=str('${:,.0f}'.format(data[0]/100))
    if data[1]:
        spot7=str('${:,.0f}'.format(data[1]/100))

    # Last 14 days pricing
    sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (dbid) WHERE jobinfo.enddate >= '" + (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d") + "' AND jobinfo.enddate <= '" + (datetime.now()).strftime("%Y-%m-%d")  + "'"
    if args.partition is not None:
        sql += " AND jobinfo.part = '" + args.partition + "'"
    cursorcost.execute(sql)
    data=cursorcost.fetchone()
    spot14 = "$0"
    reserved14 = "$0"
    if data[0]:
        reserved14=str('${:,.0f}'.format(data[0]/100))
    if data[1]:
        spot14=str('${:,.0f}'.format(data[1]/100))

    # Last 30 days pricing
    sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (dbid) WHERE jobinfo.enddate >= '" + (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d") + "' AND jobinfo.enddate <= '" + (datetime.now()).strftime("%Y-%m-%d")  + "'"
    if args.partition is not None:
        sql += " AND jobinfo.part = '" + args.partition + "'"
    cursorcost.execute(sql)
    data=cursorcost.fetchone()
    spot30 = "$0"
    reserved30 = "$0"
    if data[0]:
        reserved30=str('${:,.0f}'.format(data[0]/100))
    if data[1]:
        spot30=str('${:,.0f}'.format(data[1]/100))

    # Last 60 days pricing
    sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (dbid) WHERE jobinfo.enddate >= '" + (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d") + "' AND jobinfo.enddate <= '" + (datetime.now()).strftime("%Y-%m-%d")  + "'"
    if args.partition is not None:
        sql += " AND jobinfo.part = '" + args.partition + "'"
    cursorcost.execute(sql)
    data=cursorcost.fetchone()
    spot60 = "$0"
    reserved60 = "$0"
    if data[0]:
        reserved60=str('${:,.0f}'.format(data[0]/100))
    if data[1]:
        spot60=str('${:,.0f}'.format(data[1]/100))

    # Last 90 days pricing
    sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (dbid) WHERE jobinfo.enddate >= '" + (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d") + "' AND jobinfo.enddate <= '" + (datetime.now()).strftime("%Y-%m-%d")  + "'"
    if args.partition is not None:
        sql += " AND jobinfo.part = '" + args.partition + "'"
    cursorcost.execute(sql)
    data=cursorcost.fetchone()
    spot90 = "$0"
    reserved90 = "$0"
    if data[0]:
        reserved90=str('${:,.0f}'.format(data[0]/100))
    if data[1]:
        spot90=str('${:,.0f}'.format(data[1]/100))

    # Last 365 days pricing
    sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (dbid) WHERE jobinfo.enddate >= '" + (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d") + "' AND jobinfo.enddate <= '" + (datetime.now()).strftime("%Y-%m-%d")  + "'"
    if args.partition is not None:
        sql += " AND jobinfo.part = '" + args.partition + "'"
    cursorcost.execute(sql)
    data=cursorcost.fetchone()
    spot365 = "$0"
    reserved365 = "$0"
    if data[0]:
        reserved365=str('${:,.0f}'.format(data[0]/100))
    if data[1]:
        spot365=str('${:,.0f}'.format(data[1]/100))


    # All-time pricing
    sql = "SELECT SUM(origreservedcost),SUM(origspotcost) FROM Amazonjobcost"
    if args.partition is not None:
        sql += " INNER JOIN jobinfo USING (dbid) WHERE jobinfo.part = '" + args.partition + "'"
    cursorcost.execute(sql)
    data=cursorcost.fetchone()
    reservedall = "$0"
    spotall = "$0"
    if data[0]:
        reservedall=str('${:,.0f}'.format(data[0]/100))
    if data[1]:
        spotall=str('${:,.0f}'.format(data[1]/100))


    print("AWS Compute-Only Cost    Spot-Pricing           Reserved")
    print("--------------------------------------------------------")
    print("Today:                   %12s       %12s" % (spot1,reserved1))
    print("Last   7 days:           %12s       %12s" % (spot7,reserved7))
    print("Last  14 days:           %12s       %12s" % (spot14,reserved14))
    print("Last  30 days:           %12s       %12s" % (spot30,reserved30))
    print("Last  60 days:           %12s       %12s" % (spot60,reserved60))
    print("Last  90 days:           %12s       %12s" % (spot90,reserved90))
    print("Last 365 days:           %12s       %12s" % (spot365,reserved365))
    print("All time:                %12s       %12s" % (spotall,reservedall))

    pass


#
# Next, consider when start/end dates are given and we are NOT calculating the monthly 
# summaries in that interval.
#
if (args.days is None) and (not (args.monthly or args.weekly or args.daily))  and (args.start is not None) and (args.end is not None):
    # If here, start and/or end dates are specified, so use them
    startdate = (datetime.now() - timedelta(days=ndays)).strftime("%Y-%m-%d")
    enddate = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if args.start is not None:
        startdate = args.start
        pass 
    if args.end is not None:
        enddate = args.end
    sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (dbid) WHERE jobinfo.enddate >= '" + startdate + "' AND jobinfo.enddate <= '" + enddate  + "'"
    if args.partition is not None:
        sql += " AND jobinfo.part = '" + args.partition + "'"
    cursorcost.execute(sql)
    data=cursorcost.fetchone()
    spot1 = "0"
    reserved1 = "0"
    if not args.parsable:
        spot1 = "$0"
        reserved1 = "$0"
        if data[0]:
            reserved1=str('${:,.0f}'.format(data[0]/100))
        if data[1]:
            spot1=str('${:,.0f}'.format(data[1]/100))
    else:
        if data[0]:
            reserved1=str(data[0]/100)
        if data[1]:
            spot1=str(data[1]/100)

    if args.parsable:
        if args.headers:
            print("Start,End,Spot,Reserved")
            pass
        print("%s|%s|%s|%s" % (startdate,enddate,spot1,reserved1))
        pass
    else:
        if args.headers:
            print("AWS Compute-Only Cost      Spot-Pricing           Reserved")
            print("----------------------------------------------------------")
            pass
        print("%s - %s:   %12s       %12s" % (startdate,enddate,spot1,reserved1))
        pass    


#
# Next, consider start/end dates WITH periodic summaries in that date range
#
if (args.days is None) and (args.monthly or args.weekly or args.daily)  and (args.start is not None) and (args.end is not None):
    startdate = args.start
    enddate = args.start

    final_end_date = datetime.strptime(args.end, '%Y-%m-%d').date()
    current_start_date = datetime.strptime(args.start, '%Y-%m-%d').date()
    current_end_date = current_start_date

    if args.parsable:
       if args.headers:
           print("Start,End,Spot,Reserved")
           pass
    else:
        if args.headers:
            print("AWS Compute-Only Cost      Spot-Pricing           Reserved")
            print("----------------------------------------------------------")
            pass
        pass


    while current_end_date < final_end_date:

        # Update the ending date to the end of the month.  Limit to the user-specified final end date.
        # https://stackoverflow.com/a/43106671
        d = current_start_date
        if args.monthly:
            current_end_date = date(d.year, d.month, calendar.monthrange(d.year, d.month)[-1]) 
        if args.weekly:
            current_end_date = current_start_date + timedelta(days=+6)   # +6 because start date is inclusive
        if args.daily:
            current_end_date = current_start_date
        current_end_date = min(current_end_date, final_end_date)

        startdate = current_start_date.strftime("%Y-%m-%d")
        enddate = current_end_date.strftime("%Y-%m-%d")

        sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (dbid) WHERE jobinfo.enddate >= '" + startdate + "' AND jobinfo.enddate <= '" + enddate  + "'"
        if args.partition is not None:
            sql += " AND jobinfo.part = '" + args.partition + "'"
        cursorcost.execute(sql)
        data=cursorcost.fetchone()
        spot1 = "0"
        reserved1 = "0"
        if not args.parsable:    
            spot1 = "$0"
            reserved1 = "$0"
            if data[0]:
                reserved1=str('${:,.0f}'.format(data[0]/100))
            if data[1]:
                spot1=str('${:,.0f}'.format(data[1]/100))
        else:
            if data[0]:
                reserved1=str(data[0]/100)
            if data[1]:
                spot1=str(data[1]/100)

        if args.parsable:
            print("%s|%s|%s|%s" % (startdate,enddate,spot1,reserved1))
            pass
        else:
            print("%s - %s:   %12s       %12s" % (startdate,enddate,spot1,reserved1))
            pass

        # Increment start date to the next month
        current_start_date = current_end_date + timedelta(days=+1)

        pass
    pass


# 
# Next, consider when "last N days" has been requested
#
if (args.days is not None):  
    # Get calculation for last N days
    startdate = (datetime.now() - timedelta(days=ndays)).strftime("%Y-%m-%d")
    enddate = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (dbid) WHERE jobinfo.enddate >= '" + startdate + "' AND jobinfo.enddate <= '" + enddate  + "'"
    if args.partition is not None:
        sql += " AND jobinfo.part = '" + args.partition + "'"
    cursorcost.execute(sql)
    data=cursorcost.fetchone()
    spot1 = "0"
    reserved1 = "0"
    if not args.parsable:
        spot1 = "$0"
        reserved1 = "$0"
        if data[0]:
            reserved1=str('${:,.0f}'.format(data[0]/100))
        if data[1]:
            spot1=str('${:,.0f}'.format(data[1]/100))
    else:
        if data[0]:
            reserved1=str(data[0]/100)
        if data[1]:
            spot1=str(data[1]/100)
   

    if args.parsable:
        if args.headers:
            print("Start,End,Spot,Reserved")
            pass
        print("%s|%s|%s|%s" % (startdate,enddate,spot1,reserved1))
        pass
    else:
        if args.headers:
            print("AWS Compute-Only Cost      Spot-Pricing           Reserved")
            print("----------------------------------------------------------")
            pass
        print("Last % 4d days:            %12s       %12s" % (ndays,spot1,reserved1))
        pass 

    pass

dbcost.close()
