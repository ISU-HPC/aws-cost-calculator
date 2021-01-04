#!/bin/bash

script_dir=/home/$USER/aws-cost-calculator

# Import jobs, for last 3 days
$script_dir/01-import-job-info.py -d 3

# Fetch current AWS pricing
$script_dir/fetch-aws-pricing.py

# Calculate AWS costs for newly-imported jobs
$script_dir/02-calculate-job-costs.py

