#!/bin/env python3
import os
import datetime
import pymysql
from datetime import date, timezone, datetime
import calendar
import time
from os.path import expanduser

home = expanduser("~")
defaults_file = home + "/.my.cnf.slurm-aws"
defaults_file_slurm = home + "/.my.cnf.slurmdb"

dbcost = pymysql.connect(read_default_file=defaults_file)
dbslurm = pymysql.connect(read_default_file=defaults_file_slurm)

# TODO: Make this 'rebuild' flag a command-line argument, along with allowing an arbitrary time window
# in which to parse job data.
REBUILD=True

cursorslurm = dbslurm.cursor()
if REBUILD == True:
    sql = "SELECT id_job,time_start,time_end,tres_alloc,gres_alloc FROM nova_job_table WHERE tres_alloc <> '' AND time_start <> 0 AND time_end <> 0"
else:
    sql = "SELECT id_job,time_start,time_end,tres_alloc,gres_alloc FROM nova_job_table WHERE tres_alloc <> '' AND time_start > " + str(round (time.time() - (90 * 86400))) + " AND time_end <>0"
cursorslurm.execute(sql)
cursorcost = dbcost.cursor()
while True:
    try:
        data=cursorslurm.fetchone()
        jobid = data[0]
        runtime = data[2]-data[1]
        enddate = date.fromtimestamp(data[2]).strftime("%Y-%m-%d")
        gpus = 0
        tres=dict(s.split('=',1) for s in data[3].split(","))
        gres=dict(s.split(':',1) for s in data[4].split(","))

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

        sql = "REPLACE INTO jobinfo (jobid, runtime, enddate, cores, mem, nodes, gpus) VALUES (" + str(jobid) + "," + str(runtime) + ",'" + enddate + "'," + str(cores) + "," + str(mem) + "," + str(nodes) + "," + str(gpus) + ")"
        cursorcost.execute(sql)
        dbcost.commit()
    except:
        break

dbslurm.close()
dbcost.close()
