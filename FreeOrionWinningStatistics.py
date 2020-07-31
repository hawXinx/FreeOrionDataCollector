"""
File to print the mean winning & loosing of a specific race
"""

# Imports
import FreeOrionSharedFunctionality
import os.path
import math

# Static variables
OUTPUT_SPECIES_RESULTS = "speciesMeanWinning.csv"

mean = dict()
mean_normalized = dict()
var = dict()
var_normalized = dict()
results = FreeOrionSharedFunctionality.get_results()
samples = dict()

# Start calculating the means
for i in results:
    # Analyse the string and get the races
    split = i.split("/")
    # print(split[len(split) - 2] + ", " + split[len(split) - 3])
    pos_1 = len(split) - 2
    pos_2 = len(split) - 3
    species_1 = split[pos_1]
    species_2 = split[pos_2]

    if species_1 in mean:
        # Multiplyed by -1 as those have been player 2
        mean[species_1] = mean[species_1] + (results[i] * -1)
        samples[species_1] = samples[species_1] + 1
    else:
        mean[species_1] = (results[i] * -1)
        samples[species_1] = 1

    if species_2 in mean:
        # Multiplyed by -1 as those have been player 2
        mean[species_2] = mean[species_2] + results[i]
        samples[species_2] = samples[species_2] + 1
    else:
        mean[species_2] = results[i]
        samples[species_2] = 1

# Mean everything out
for i in mean:
    mean[i] = mean[i] / float(samples[i])
    mean_normalized[i] = (mean[i] + 1) / 2.0

# Calculate the variance
for i in results:
    split = i.split("/")
    # print(split[len(split) - 2] + ", " + split[len(split) - 3])
    pos_1 = len(split) - 2
    pos_2 = len(split) - 3
    species_1 = split[pos_1]
    species_2 = split[pos_2]
    if species_1 in var:
        var[species_1] = var[species_1] + math.pow((results[i] * -1) - mean[species_1], 2)
        results_normalized = ((results[i] * -1) + 1) / 2.0
        var_normalized[species_1] = var_normalized[species_1] + \
                                    math.pow(results_normalized - mean_normalized[species_1], 2)
    else:
        var[species_1] = math.pow((results[i] * -1) - mean[species_1], 2)
        results_normalized = ((results[i] * -1) + 1) / 2.0
        var_normalized[species_1] = math.pow(results_normalized - mean_normalized[species_1], 2)

    if species_2 in var:
        var[species_2] = var[species_2] + math.pow(results[i] - mean[species_2], 2)
        results_normalized = (results[i] + 1) / 2.0
        var_normalized[species_2] = var_normalized[species_2] + \
                                    math.pow(results_normalized - mean_normalized[species_2], 2)
    else:
        var[species_2] = math.pow(results[i] - mean[species_2], 2)
        results_normalized = (results[i] + 1) / 2.0
        var_normalized[species_2] = math.pow(results_normalized - mean_normalized[species_2], 2)

for i in var:
    var[i] = var[i] / (samples[i] - 1)
    var_normalized[i] = var_normalized[i] / (samples[i] - 1)

# Store everything in an CSV
if os.path.isfile(OUTPUT_SPECIES_RESULTS):
    f = open(OUTPUT_SPECIES_RESULTS, "wt")
else:
    f = open(OUTPUT_SPECIES_RESULTS, "xt")

# Header
f.write("Species;Entries;Mean;Mean_normalized;Variance;Variance_normalized;\n")
for i in var:
    f.write(str(i) + ";" + str(samples[i]) + ";" + str(mean[i]) + ";" + str(mean_normalized[i]) + ";" +
            str(var[i]) + ";" + str(var_normalized[i]) + ";" + "\n")
