#!/bin/bash

# Import jobs, for last 3 days
./01-import-job-info.py -d 3

# Fetch current AWS pricing
./fetch-aws-pricing.py

# Calculate AWS costs for newly-imported jobs
./02-calculate-job-costs.py

