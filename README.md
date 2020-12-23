# Amazon Cost Calculator

This is based on "Amazon Cost Comparison" from Kansas State: https://gitlab.beocat.ksu.edu/Admin-Public/amazon-cost-comparison

## Prerequisites

- python3
- pip3 modules
    - pymysql
    - setuptools
    - wheel
    - requests

## Getting Started

1. Begin by running `00-prepare-mysql-onetime.sh`.  This will prompt for mysql usernames and passwords in order to setup the database environment.  You need to know the MYSQL admin password for this step.
2. Next, import current AWS prices using `fetch-aws-pricing.py`.  This script may be run at any time to update AWS pricing information to be used in cost calculations.  To display the current pricing values, run `print-aws-pricing-data.sh`.
3. Next, import slurm job data into a the cost analysis database using `01-import-job-info.py`.  This script must be run in order for more-recent jobs to be imported into the database.
4. Next, calculate per-job resource requirements and per-job costs using `02-calculate-job-costs.py`.
5. Finally, calculate the cumulative AWS costs with `03-calculate-total-aws-cost.py`.

Information about the MySQL database tables can be found in mysql-prereqs.txt.
