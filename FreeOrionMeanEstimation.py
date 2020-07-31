"""
This file implements simple statistic analysis of winning and loosing for each species-combination used.
The following analysis are done:
1, Mean
2, Mean (normalized)
3, Variance
4, Variance (normalized)
5, Estimated sample size based on Mean (normalized), Variance (normalized), Lenght L (normalized, given in code) and
alpha (given in code) --> Used when estimating binary/binomial results (not statistically sound but used because
in an ideal world only one side would win and 0-values would not exist).
6, Estimated sample size based on Mean, Variance, Length L and alpha --> Used when estimating mean with samples
of different values (statistically sound but result is more variable).
"""

# Imports
import math
import sys
import scipy.stats
import os
import FreeOrionSharedFunctionality

# Variables
# Normalized Length of the confidence intervall
# L alone will be calculated based on L_NORM as L = L_NORM * 2 (based on the range of the results between -1 and 1)
L_NORM = 0.2
# Security of the given results. We can be 1-alpha percent secure that a random sample is within mean +- L
ALPHA = 0.1

if ALPHA <= 0 or ALPHA >= 1:
    print("Alpha was set out of range.")
    sys.exit(1)

# From https://stackoverflow.com/questions/20626994/how-to-calculate-the-inverse-of-the-normal-cumulative-distribution-function-in-p
# Normal Distribution of Alpha
Z_ALPHA = scipy.stats.norm.ppf(1 - ALPHA / 2.0)
# For samples with less than 30 entries using the not-normed values, we will need the T-distribution,
# but we will have to calculate that one on the fly depending on the number of entries.

OUTPUT = "meanAndEstimation.csv"

mean = dict()
mean_norm = dict()
var = dict()
var_norm = dict()
# Amount of entries of one sample
entries = dict()
# Estimated sample sizes
est_sample_binom = dict()
est_sample = dict()

# Get the results
results = FreeOrionSharedFunctionality.get_results()


def crop_file_string(file3):
    """
    Crop to only use the head of the file name instead of all of it
    :return The file name at the end of the string (BASED ON LINUX!!)
    """
    split_in_crop = file3.split("/")
    file3_pruned = file3.replace(split_in_crop[len(split_in_crop) - 1], "")
    return file3_pruned


# Start calculating the results.
# First the mean
for file2 in results:
    file = crop_file_string(file2)
    win_loose = int(results[file2])

    if file in mean:
        mean[file] = mean[file] + win_loose
        # As the results are within -1 and 1, it's hard coded here (and in the later occurences too).
        mean_norm[file] = mean_norm[file] + (win_loose + 1.0) / 2.0
        entries[file] = entries[file] + 1
    else:
        mean[file] = win_loose
        mean_norm[file] = (win_loose + 1.0) / 2.0
        entries[file] = 1

# Finish the mean
for file in mean:
    if entries[file] >= 1:
        mean[file] = mean[file] / (entries[file])
        mean_norm[file] = mean_norm[file] / (entries[file])
    else:
        mean[file] = 0
        mean_norm[file] = 0

# Now for the variance
for file2 in results:
    file = crop_file_string(file2)
    win_loose = int(results[file2])
    if file in var:
        var[file] = var[file] + math.pow(win_loose - mean[file], 2)
        var_norm[file] = var_norm[file] + math.pow((win_loose + 1.0) / 2.0 - mean_norm[file], 2)
    else:
        var[file] = math.pow(win_loose - mean[file], 2)
        var_norm[file] = math.pow((win_loose + 1.0) / 2.0 - mean_norm[file], 2)

# Finish off the variances
for file in var:
    if entries[file] > 1:
        var[file] = var[file] / (entries[file] - 1)
        var_norm[file] = var_norm[file] / (entries[file] - 1)
    else:
        var[file] = 0
        var_norm[file] = 0

# Good, now calculate the estimated sample size
for file in var:
    # Calculation based on binomial values is always the same.
    est_sample_binom[file] = 4 * math.pow(Z_ALPHA, 2) * mean_norm[file] * (1 - mean_norm[file]) / math.pow(L_NORM, 2)

    # For the calculation on the mean-estimator, we have to test if we need t-distribution
    # (if the degree of freedom is above 30, the results of T and Normal are getting
    # so close to each other that we can take the fixed Normal).
    used_distribution_value = Z_ALPHA
    if int(entries[file]) <= 30:
        degree_freedom = int(entries[file]) - 1
        used_distribution_value = scipy.stats.t.ppf(1 - ALPHA / 2, degree_freedom)
    # with this estimation we are expecting an estimation error, so that we don't have the length of the confidence intervall is two times the error (and therefore, we use the normalized value)
    estimation_error = L_NORM
    est_sample[file] = math.pow(used_distribution_value, 2) * var[file] / math.pow(estimation_error, 2)

# Now that we've got all that, store it
f = None
if os.path.isfile(OUTPUT):
    f = open(OUTPUT, "wt")
else:
    f = open(OUTPUT, "xt")

f.write("File;Entries;Mean;Mean_normalized;Variance;Variance_normalized;Sample_Estimation;Sample_Estimation_binomial\n")

for file in est_sample:
    split = file.split("/")
    file_1 = split[len(split) - 3] + "/" + split[len(split) - 2]
    f.write(str(file_1) + ";" + str(entries[file]) + ";" + str(mean[file]) + ";" + str(mean_norm[file]) +
            ";" + str(var[file]) + ";" + str(var_norm[file]) + ";" + str(est_sample[file]) +
            ";" + str(est_sample_binom[file]) + "\n")
