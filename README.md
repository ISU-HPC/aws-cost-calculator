# Amazon Cost Calculator

This is based on "Amazon Cost Comparison" from Kansas State: https://gitlab.beocat.ksu.edu/Admin-Public/amazon-cost-comparison

## Prerequisites

- python3
- pip3 modules
    - pymysql
    - setuptools
    - wheel
    - requests

Note that this makes no assumptions about how you make python3 and its modules available.  You are free to use
virtual environments, environment modules, host-installed, etc.

All of the python scripts accept CLI arguments.  Pass the `-h` flag to them to get a list of available arguments for each script.

## Getting Started

1. Begin by running `00-prepare-mysql-onetime.sh`.  This will prompt for mysql usernames and passwords in order to setup the database environment.  You need to know the MYSQL admin password for this step.
2. Next, import current AWS prices using `fetch-aws-pricing.py`.  This script may be run at any time to update AWS pricing information to be used in cost calculations.  To display the current pricing values, run `print-aws-pricing-data.sh`.
3. Next, import slurm job data into a the cost analysis database using `01-import-job-info.py`.  This script must be run in order for more-recent jobs to be imported into the database. 
    - This step can take quite a while to run if you have a lot of job history.  You can reduce the runtime by limiting the time period in which you search for jobs (e.g., only import jobs from the last N days).  You can get a status output as it progresses by using the `--verbose` flag.
4. Next, calculate per-job resource requirements and per-job costs using `02-calculate-job-costs.py`.
    - This step is much faster than the job-import step, but may still take a long time for large job-counts.
5. Finally, calculate the cumulative AWS costs with `03-calculate-total-aws-compute-cost.py`.

Separate from the AWS computation cost, you can get rough storage cost estimates using `04-calculate-aws-storage-cost.py`.  This script simply shows
AWS storage costs for various storage services (EBS, S3, Glacier) for several filesystems, both for the currently-used storage quantity as well as 
the fileystems' maximum capacity.

Information about the MySQL database tables can be found in mysql-prereqs.txt.
