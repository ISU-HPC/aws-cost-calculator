#!/bin/env python3

import json
import requests
import pymysql
from os.path import expanduser

home = expanduser("~")
defaults_file = home + "/.my.cnf.slurm-aws"

dbcost = pymysql.connect(read_default_file=defaults_file)
cursorcost = dbcost.cursor()

url = 'https://ec2.shop?filter=m5.,x1.,x1e.,p3'
data = ''
headers = { 'accept': 'json' }
pricing_info = requests.get(url, headers)
pricing_dict = json.loads(pricing_info.text)

for instance in pricing_dict['Prices']:
    # {'InstanceType': 'x1e.16xlarge', 'Memory': '1952 GiB', 'VCPUS': 64, 'Storage': '1 x 1920 SSD', 'Network': '10 Gigabit', 'Cost': 13.344, 'MonthlyPrice': 9741.119999999999, 'SpotPrice': '4.0032'}
    typename = instance['InstanceType']
    memory = int(instance['Memory'].split(' ')[0])
    cpus = instance['VCPUS']
    gpus = 0
    if typename == 'p3.2xlarge':
        gpus = 1
    if typename == 'p3.8xlarge':
        gpus = 4
    if typename == 'p3.16xlarge':
        gpus = 8
    if typename == 'p3dn.24xlarge':
        gpus = 8 
    cost = int(float(instance['Cost']) * 10000.0)
    spot = int(float(instance['SpotPrice']) * 10000.0)

    sql = "REPLACE INTO Amazon (instancetype, cores, mem, gpus, latestreservedcost, latestspotcost) VALUES ('" + typename + "','" + str(cpus) + "','" + str(memory) + "','" + str(gpus) + "','" + str(cost) + "','" + str(spot) + "')"
    cursorcost.execute(sql)
    dbcost.commit()

dbcost.close()

