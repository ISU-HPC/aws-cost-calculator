#!/bin/env python3
import os
import datetime
import pymysql
from datetime import date, timezone, datetime
import calendar
import time
from os.path import expanduser
import subprocess
import argparse

# Create an ArgumentParser object to easily handle command-line options and
# auto-generate helpful CLI help when -h/--help flags are used.
parser = argparse.ArgumentParser(description='Import slurm job info into analysis database')

parser.add_argument('-d', '--days',
                    dest='days',
                    metavar='N',
                    type=int,
                    help='Import last N days of slurm jobs (default: 30).  Ignored if --start and/or --end are used.')
parser.add_argument('--defaults-analysis',
                    dest='defaults_analysis',
                    type=str,
                    help='MySQL connection file for analysis database')
parser.add_argument('--defaults-slurm',
                    dest='defaults_slurm',
                    type=str,
                    help='MySQL connection file for slurm database')
parser.add_argument('--slurm-job-table',
                    dest='slurm_job_table',
                    type=str,
                    help='Name of slurm job-info table (default: ${clustername}_job_table)')
parser.add_argument('--start',
                    dest='start',
                    metavar='YYYY-MM-DD',
                    type=str,
                    help='Start date for job import (default: 30 days before today)')
parser.add_argument('--end',
                    dest='end',
                    metavar='YYYY-MM-DD',
                    type=str,
                    help='End date for job import (default: now)')
parser.add_argument('-v', '--verbose',
                    dest='verbose',
                    action='store_true',
                    help='Output extra messages.')


# Parse the arguments provided by the user
args, leftovers = parser.parse_known_args()

# Initialize variable and update based on CLI arguments
home = expanduser("~")
defaults_file = home + "/.my.cnf.slurm-aws"
defaults_file_slurm = home + "/.my.cnf.slurmdb"
days = 30

if args.defaults_analysis is not None:
    defaults_file = args.defaults_analysis
    pass

if args.defaults_slurm is not None:
    defaults_file_slurm = args.defaults_slurm
    pass

if args.days is not None:
    days = args.days
    pass


# Get cluster name from slurm.conf.  Assume that lower-case form is used in database table names.
job_table = "cluster_job_table"
if args.slurm_job_table is not None:
    job_table = args.slurm_job_table
    pass
else:
    cmd="/usr/bin/grep ClusterName /etc/slurm/slurm.conf | cut -f 2 -d '='"
    clustername = subprocess.check_output(cmd, shell=True).decode("utf-8").lower().rstrip()
    job_table = clustername + "_job_table"
    pass

# Determine query dates
startdate = str(round(time.time() - (days * 86400)))   # Initialize to N days before now
enddate = str(round(time.time()))                      # Initialize to now

if args.start is not None:
    startdate = datetime.strptime(args.start, '%Y-%m-%d').timestamp()
    pass
if args.end is not None:
    enddate = datetime.strptime(args.end, '%Y-%m-%d').timestamp()  # Timestamp of 12:00:00am (i.e., start of the day)
    enddate += 86400       # Use *end* of the day to be inclusive.
    pass




dbcost = pymysql.connect(read_default_file=defaults_file)
dbslurm = pymysql.connect(read_default_file=defaults_file_slurm)

cursorslurm = dbslurm.cursor()

# Build SQL query.  Note back-ticks for cases with non-standard characters in the job table name.
sql = "SELECT job_db_inx,id_job,time_start,time_end,tres_alloc,gres_alloc,`partition` FROM `" + job_table + "` WHERE tres_alloc <> '' AND time_start > " + str(startdate) + " AND time_end < " + str(enddate) + " AND time_end <>0"


cursorslurm.execute(sql)
cursorcost = dbcost.cursor()
count = 0
total_count = cursorslurm.rowcount
while True:
    try:
        data=cursorslurm.fetchone()
        dbid = data[0]
        jobid = data[1]
        runtime = data[3]-data[2]
        enddate = date.fromtimestamp(data[3]).strftime("%Y-%m-%d")
        gpus = 0
        gres = {}
        tres=dict(s.split('=',1) for s in data[4].split(","))
        if data[5] != '':
            gres = dict(s.split(':',1) for s in data[5].split(",")) 
            pass 
        part = data[6]

        # NOTE: Your trackables resources may be different than mine. I'm not positive how things change site-to-site.
        # Separate out the tres
        if '1' in tres.keys():
            cores=int(tres['1'])
        if '2' in tres.keys():
            mem=((int(tres['2'])-1)//1024)+1 # Round up to a whole number
        if '4' in tres.keys():
            nodes=int(tres['4'])
        if '1001' in tres.keys():
            gpus=tres['1001']

        # Check for 'gpu' in gres info
        if 'gpu' in gres.keys():
            gpus=gres['gpu']

        # Insert data into analysis job info table.  REPLACE is used so that re-processing slurm jobs will update values as necessary.
        sql2 = "REPLACE INTO jobinfo (dbid, jobid, runtime, enddate, cores, mem, nodes, gpus, part) VALUES (" + str(dbid) + "," + str(jobid) + "," + str(runtime) + ",'" + enddate + "'," + str(cores) + "," + str(mem) + "," + str(nodes) + "," + str(gpus) + ",'" + str(part) + "')"
        cursorcost.execute(sql2)
        dbcost.commit()
    
        count += 1
        if count % 1000 == 0:
            if args.verbose:
                print("Imported record % 12d of % 12d" % (count,total_count))
                pass
            pass
    except:
        break

if args.verbose:
    print("Imported %d records" % count)
    pass


dbslurm.close()
dbcost.close()
