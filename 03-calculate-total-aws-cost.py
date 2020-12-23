#!/bin/env python3
import os
import datetime
import pymysql
from datetime import date, datetime, timedelta
import time
from os.path import expanduser

home = expanduser("~")
defaults_file = home + "/.my.cnf.slurm-aws"

dbslurm = pymysql.connect(read_default_file=defaults_file)

cursorslurm = dbslurm.cursor()
sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (jobid) WHERE jobinfo.enddate >= '" + (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d") + "' AND jobinfo.enddate <= '" + (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  + "'"
print(sql)
cursorslurm.execute(sql)
data=cursorslurm.fetchone()
print(data)
reserved30=str('${:,.0f}'.format(data[0]/100))
spot30=str('${:,.0f}'.format(data[1]/100))
sql = "SELECT SUM(origreservedcost),SUM(origspotcost) FROM Amazonjobcost"
cursorslurm.execute(sql)
data=cursorslurm.fetchone()
reservedall=str('${:,.0f}'.format(data[0]/100))
spotall=str('${:,.0f}'.format(data[1]/100))
dbslurm.close()

print("Last 30 days: %s    %s" % (spot30,reserved30))
print("All time:     %s    %s" % (spotall,reservedall))


