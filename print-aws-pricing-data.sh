#!/bin/bash

echo ""
echo "Current AWS pricing info in the database"
echo ""
echo "Pricing is per-hour and is in 1/100 of a cent.  10,000 = \$1"

mysql --defaults-file=~/.my.cnf.slurm-aws -e "select * from Amazon;"

echo ""
echo "To fetch current prices, run ./fetch-aws-pricing.py"
echo ""
