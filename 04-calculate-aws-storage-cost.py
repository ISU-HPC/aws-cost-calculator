#!/bin/python3

import argparse
import subprocess

# Create an ArgumentParser object to easily handle command-line options and
# auto-generate helpful CLI help when -h/--help flags are used.
parser = argparse.ArgumentParser(description='Estimate AWS storage costs')

parser.add_argument('-t', '--fstype',
                    dest='fstype',
                    type=str,
                    help='Grab all filesystems of specified type.')
parser.add_argument('-d', '--dirs',
                    dest='dirs',
                    type=str,
                    help='Directories to consider in the anlysis.  Space-separated list within quotes.')
parser.add_argument('-v', '--verbose',
                    dest='verbose',
                    action='store_true',
                    help='Output extra messages.')


# Parse the arguments provided by the user
args, leftovers = parser.parse_known_args()


# Define the storage paths to be considered.  Use CLI arguments if present.
# Otherwise, prompt for user input.
defaultpaths = "/home /work"
storagepaths = defaultpaths
if args.dirs is not None:
    storagepaths = args.dirs
    pass
else:
    if args.fstype is None:
        # Only prompt if filesystem type wasn't specified on CLI
        storagepaths = input("Provide space-separated list of paths to include [/home /work]: ")
        pass
    if not storagepaths:
        storagepaths = defaultpaths
        pass
    pass

# Add paths defined by filesystem type, if defined on the CLI
if args.fstype is not None:
    cmd = "df -T | grep " + args.fstype + " | awk '{ print $NF }' | tr '\n' ' '"
    extradirs = subprocess.check_output(cmd, shell=True).decode("utf-8").rstrip()
    storagepaths += " " + extradirs
    pass

# Print the combined filesystem list
if args.verbose is True:
    print("Directories included in this analysis:")
    print(storagepaths)

# Get the sizes of the specified filesystems
cmd = "df -BG " + storagepaths + " | tail -n+2 | awk '{ print $3 }' | tr -d 'G' | paste -sd+ | bc"
gb_used = float(subprocess.check_output(cmd, shell=True).decode("utf-8").rstrip())

cmd = "df -BG " + storagepaths + " | tail -n+2 | awk '{ print $2 }' | tr -d 'G' | paste -sd+ | bc"
gb_max = float(subprocess.check_output(cmd, shell=True).decode("utf-8").rstrip())

# Calculate storage costs
aws_price_0_50 = 0.023
aws_price_50_450 = 0.022
aws_price_500 = 0.021

aws_price_glacier = 0.004
aws_price_deep_glacier = 0.00099

used_s3 = 0.0
if gb_used < 50.0:
    used_s3 += aws_price_0_50 * gb_used
elif gb_used < 500:
    used_s3 += 50.0 * aws_price_0_50 + (gb_used - 50.0) * aws_price_50_450
else:
    used_s3 += 50.0 * aws_price_0_50 + 450.0 * aws_price_50_450 + (gb_used - 500.0) * aws_price_500
used_s3_cost = "${:,.2f}".format(used_s3)

used_glacier = gb_used * aws_price_glacier
used_glacier_cost = "${:,.2f}".format(used_glacier)

used_deep_glacier = gb_used * aws_price_deep_glacier
used_deep_glacier_cost = "${:,.2f}".format(used_deep_glacier)

max_s3 = 0.0
if gb_max < 50.0:
    max_s3 += aws_price_0_50 * gb_max
elif gb_max < 500:
    max_s3 += 50.0 * aws_price_0_50 + (gb_max - 50.0) * aws_price_50_450
else:
    max_s3 += 50.0 * aws_price_0_50 + 450.0 * aws_price_50_450 + (gb_max - 500.0) * aws_price_500
max_s3_cost = "${:,.2f}".format(max_s3)

max_glacier = gb_max * aws_price_glacier
max_glacier_cost = "${:,.2f}".format(max_glacier)

max_deep_glacier = gb_max * aws_price_deep_glacier
max_deep_glacier_cost = "${:,.2f}".format(max_deep_glacier)

# Calculate egress costs
used_s3_to_internet = 0.0
if gb_used < 10.0 * 1024.0:
    used_s3_to_internet = (gb_used - 1.0) * 0.09
elif gb_used < 50.0 * 1024:
    used_s3_to_internet = 9.999 * 1024.0 * 0.09 + (gb_used - 10.0 * 1024.0) * 0.085
elif gb_used < 100.0 * 1024:
    used_s3_to_internet = 9.999 * 1024.0 * 0.09 + 40.0 * 1024.0 * 0.085 + (gb_used - 50.0 * 1024.0) * 0.07
else:
    used_s3_to_internet = 9.999 * 1024.0 * 0.09 + 40.0 * 1024.0 * 0.085 + 100.0 * 1024 * 0.07 + (gb_used - 150.0 * 1024.0) * 0.05
used_s3_to_internet_cost = "${:,.2f}".format(used_s3_to_internet)

max_s3_to_internet = 0.0
if gb_used < 10.0 * 1024.0:
    max_s3_to_internet = (gb_max - 1.0) * 0.09
elif gb_used < 50.0 * 1024:
    max_s3_to_internet = 9.999 * 1024.0 * 0.09 + (gb_max - 10.0 * 1024.0) * 0.085
elif gb_used < 100.0 * 1024:
    max_s3_to_internet = 9.999 * 1024.0 * 0.09 + 40.0 * 1024.0 * 0.085 + (gb_max - 50.0 * 1024.0) * 0.07
else:
    max_s3_to_internet = 9.999 * 1024.0 * 0.09 + 40.0 * 1024.0 * 0.085 + 100.0 * 1024 * 0.07 + (gb_max - 150.0 * 1024.0) * 0.05
max_s3_to_internet_cost = "${:,.2f}".format(max_s3_to_internet)


used_glacier_retrieve_cost = "${:,.2f}".format(gb_used * 0.01)
used_deep_glacier_retrieve_cost = "${:,.2f}".format(gb_used * 0.02)

max_glacier_retrieve_cost = "${:,.2f}".format(gb_max * 0.01)
max_deep_glacier_retrieve_cost = "${:,.2f}".format(gb_max * 0.02)

used_xfer_hrs_gigabit = gb_used * 8.0 / 3600.0
max_xfer_hrs_gigabit = gb_max * 8.0 / 3600.0

print("")
print("MONTHLY Storage Costs")
print("  Currently-Used:        %8.0f GB" % gb_used)
print("    S3 Standard:   %12s" % used_s3_cost)
print("    Glacier:       %12s" % used_glacier_cost)
print("    Deep Glacier:  %12s" % used_deep_glacier_cost)
print("  Filesystem-Maximum:    %8.0f GB" % gb_max)
print("    S3 Standard:   %12s" % max_s3_cost)
print("    Glacier:       %12s" % max_glacier_cost)
print("    Deep Glacier:  %12s" % max_deep_glacier_cost)
print("")
print("Egress / Retrieval Costs (Standard Rates)")
print("  Currently-Used:        %8.0f GB" % gb_used)
print("    S3 Standard:   %12s" % used_s3_to_internet_cost)
print("    Glacier:       %12s" % used_glacier_retrieve_cost)
print("    Deep Glacier:  %12s" % used_deep_glacier_retrieve_cost)
print("  Filesystem-Maximum:    %8.0f GB" % gb_max)
print("    S3 Standard:   %12s" % max_s3_to_internet_cost)
print("    Glacier:       %12s" % max_glacier_retrieve_cost)
print("    Deep Glacier:  %12s" % max_deep_glacier_retrieve_cost)
print("")
print("Data Transfer Time")
print("  Currently-Used:        %8.0f GB" % gb_used)
print("    10 Mb/s:   % 11.2f [hrs]" % (used_xfer_hrs_gigabit * 100.0))
print("    100 Mb/s:  % 11.2f [hrs]" % (used_xfer_hrs_gigabit * 10.0))
print("    1 Gb/s:    % 11.2f [hrs]" % (used_xfer_hrs_gigabit))
print("    10 Gb/s:   % 11.2f [hrs]" % (used_xfer_hrs_gigabit / 10.0))
print("  Filesystem-Maximum:    %8.0f GB" % gb_max)
print("    10 Mb/s:   % 11.2f [hrs]" % (max_xfer_hrs_gigabit * 100.0))
print("    100 Mb/s:  % 11.2f [hrs]" % (max_xfer_hrs_gigabit * 10.0))
print("    1 Gb/s:    % 11.2f [hrs]" % (max_xfer_hrs_gigabit))
print("    10 Gb/s:   % 11.2f [hrs]" % (max_xfer_hrs_gigabit / 10.0))
print("")
