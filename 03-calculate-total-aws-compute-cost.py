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

# Last 7 days pricing
sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (jobid) WHERE jobinfo.enddate >= '" + (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d") + "' AND jobinfo.enddate <= '" + (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  + "'"
cursorslurm.execute(sql)
data=cursorslurm.fetchone()
spot7 = "$0"
reserved7 = "$0"
if data[0]:
    reserved7=str('${:,.0f}'.format(data[0]/100))
if data[1]:
    spot7=str('${:,.0f}'.format(data[1]/100))

# Last 14 days pricing
sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (jobid) WHERE jobinfo.enddate >= '" + (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d") + "' AND jobinfo.enddate <= '" + (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  + "'"
cursorslurm.execute(sql)
data=cursorslurm.fetchone()
spot14 = "$0"
reserved14 = "$0"
if data[0]:
    reserved14=str('${:,.0f}'.format(data[0]/100))
if data[1]:
    spot14=str('${:,.0f}'.format(data[1]/100))

# Last 30 days pricing
sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (jobid) WHERE jobinfo.enddate >= '" + (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d") + "' AND jobinfo.enddate <= '" + (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  + "'"
cursorslurm.execute(sql)
data=cursorslurm.fetchone()
spot30 = "$0"
reserved30 = "$0"
if data[0]:
    reserved30=str('${:,.0f}'.format(data[0]/100))
if data[1]:
    spot30=str('${:,.0f}'.format(data[1]/100))

# Last 60 days pricing
sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (jobid) WHERE jobinfo.enddate >= '" + (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d") + "' AND jobinfo.enddate <= '" + (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  + "'"
cursorslurm.execute(sql)
data=cursorslurm.fetchone()
spot60 = "$0"
reserved60 = "$0"
if data[0]:
    reserved60=str('${:,.0f}'.format(data[0]/100))
if data[1]:
    spot60=str('${:,.0f}'.format(data[1]/100))

# Last 90 days pricing
sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (jobid) WHERE jobinfo.enddate >= '" + (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d") + "' AND jobinfo.enddate <= '" + (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  + "'"
cursorslurm.execute(sql)
data=cursorslurm.fetchone()
spot90 = "$0"
reserved90 = "$0"
if data[0]:
    reserved90=str('${:,.0f}'.format(data[0]/100))
if data[1]:
    spot90=str('${:,.0f}'.format(data[1]/100))

# Last 365 days pricing
sql = "SELECT SUM(Amazonjobcost.origreservedcost),SUM(Amazonjobcost.origspotcost) FROM Amazonjobcost INNER JOIN jobinfo USING (jobid) WHERE jobinfo.enddate >= '" + (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d") + "' AND jobinfo.enddate <= '" + (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  + "'"
cursorslurm.execute(sql)
data=cursorslurm.fetchone()
spot365 = "$0"
reserved365 = "$0"
if data[0]:
    reserved365=str('${:,.0f}'.format(data[0]/100))
if data[1]:
    spot365=str('${:,.0f}'.format(data[1]/100))


# All-time pricing
sql = "SELECT SUM(origreservedcost),SUM(origspotcost) FROM Amazonjobcost"
cursorslurm.execute(sql)
data=cursorslurm.fetchone()
reservedall=str('${:,.0f}'.format(data[0]/100))
spotall=str('${:,.0f}'.format(data[1]/100))
dbslurm.close()

print("AWS Cost          Spot-Pricing           Reserved")
print("-------------------------------------------------")
print("Last   7 days:    %12s       %12s" % (spot7,reserved7))
print("Last  14 days:    %12s       %12s" % (spot14,reserved14))
print("Last  30 days:    %12s       %12s" % (spot30,reserved30))
print("Last  60 days:    %12s       %12s" % (spot60,reserved60))
print("Last  90 days:    %12s       %12s" % (spot90,reserved90))
print("Last 365 days:    %12s       %12s" % (spot365,reserved365))
print("All time:         %12s       %12s" % (spotall,reservedall))


