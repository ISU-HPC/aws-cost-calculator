#!/bin/bash

# This script creates the 'slurm-aws' user in MySQL, creates the 'slurm-aws-analysis' 
# database, and grants permissions to the 'slurm-aws' user.  It requires administrator
# access to the MySQL server.

# Get the admin password
read -p "Please provide the 'root' user password: " -s rootpw
echo ""

# Get username & password for the unprivileged MySQL user
read -p "Please provide the 'slurm-aws' username [slurm-aws]: " analysisuser
analysisuser=${analysisuser:-slurm-aws}
read -p "Please provide the $analysisuser password: " -s analysispw
echo ""

# Get name of database for the analysis info
read -p "Please provide the 'slurm_aws_analysis' database name [slurm_aws_analysis]: " analysisdb
analysisdb=${analysisdb:-slurm_aws_analysis}

# Create the connection settings file using the admin password
conn_file_admin="$HOME/.my.cnf.admin"
touch $conn_file_admin
chmod 0600 $conn_file_admin
cat << EOF > $conn_file_admin
[client]
user=root
password=$rootpw
EOF


# Create the connection settings file for the unprivileged user
conn_file_user="$HOME/.my.cnf.$analysisuser"
touch $conn_file_user
chmod 0600 $conn_file_user
cat << EOF > $conn_file_user
[client]
user=$analysisuser
password=$analysispw
host=127.0.0.1
database=$analysisdb
EOF

conn_file_slurm="$HOME/.my.cnf.slurmdb"
touch $conn_file_slurm
chmod 0600 $conn_file_slurm
cat << EOF > $conn_file_slurm
[client]
user=$analysisuser
password=$analysispw
host=127.0.0.1
database=slurm_acct_db
EOF


# Create the database
mysql --defaults-file=$conn_file_admin -e "create database if not exists $analysisdb;"

# Grant access to databases.  User will be created if necessary.
mysql --defaults-file=$conn_file_admin -e "grant all on $analysisdb.* to '$analysisuser'@'localhost' identified by '$analysispw';"
mysql --defaults-file=$conn_file_admin -e "grant select,show view on slurm_acct_db.* to '$analysisuser'@'localhost' identified by '$analysispw';"
mysql --defaults-file=$conn_file_admin -e "flush privileges;"

# Cleanup.  Delete the admin connection settings file.
rm -f $conn_file_admin


# Create tables in the analysis database
mysql --defaults-file=$conn_file_user $analysisdb -e "create table if not exists Amazon(instancetype varchar(50) not null default '-', cores int(11) default NULL, mem int(11) default NULL, gpus int(11) not null default '0', latestreservedcost int(11) default NULL, latestspotcost int(11) default NULL, primary key(instancetype));"

mysql --defaults-file=$conn_file_user $analysisdb -e "create table if not exists jobinfo(jobid bigint(20) not null default -1, runtime int(11) not null default 0, enddate date not null default '2000-01-01', cores int(11) not null default 0, mem int(11) not null default 0, gpus int(11) not null default 0, nodes int(11) not null default 0, primary key(jobid));"

mysql --defaults-file=$conn_file_user $analysisdb -e "create table if not exists Amazonjobcost(jobid bigint(20) not null default -1, instancetype varchar(50) not null default '-', origreservedcost int(11) not null default 0, origspotcost int(11) not null default 0, latestreservedcost int(11) not null default 0, latestspotcost int(11) not null default 0, primary key(jobid), index(instancetype));"
