"""
This script takes all log files and their data and stores it including it's results in one file. Also, the
data is cut down so that doubles within one log file are stored only once (but doubles over several files
are stored several times).
This script produces a csv with the mentioned data to analyse it in other programs.
"""

# Imports
import os
import FreeOrionSharedFunctionality

# Static variables
OUTPUT_CATEGORICAL = "pruningDataCategorical.csv"
OUTPUT_REGRESSION = "pruningDataRegression.csv"

# Here we prune away all zeros as those can make some nasty results (Turning this decision into binary gives
# many advantages)
result = FreeOrionSharedFunctionality.get_results(prune_zero=True)
# Stores all values for regression comparison
all_values = dict()
all_values_count = dict()

# The categorical values are written into the file immediately
if os.path.isfile(OUTPUT_CATEGORICAL):
    f = open(OUTPUT_CATEGORICAL, "wt")
else:
    f = open(OUTPUT_CATEGORICAL, "xt")

# Header
f.write("Category;Turn;Planet_count_KI_1;Research_KI_1;Industry_KI_1;Ships_KI_1;Population_KI_1;Planet_count_KI_6;" +
        "Research_KI_6;Industry_KI_6;Ships_KI_6;Population_KI_6;\n")

for i in result:
    # Open that file and read every line
    if not os.path.isfile(i):
        # A bit odd, print it but keep on going
        print("File " + i + " not found. Ignored.")
        continue
    f2 = open(i, "rt")
    # Be aware of doubles within the same file
    double_dict = list()

    for line in f2:
        if double_dict.__contains__(line):
            # Ignore this line as this file has added one of these already.
            continue
        # Ignore the line if it's the first line (contains Key-words)
        if line.__contains__("Turn") or line.__contains__("KI") or line.__contains__("_"):
            continue

        f.writelines(str(result[i]) + ";" + line)

        # Calculate for regression
        if all_values.__contains__(line):
            all_values[line] = all_values[line] + result[i]
            all_values_count[line] = all_values_count[line] + 1
        else:
            all_values[line] = result[i]
            all_values_count[line] = 1
        double_dict.append(line)

f.close()

# Now write the Regression values
if os.path.isfile(OUTPUT_REGRESSION):
    f = open(OUTPUT_REGRESSION, "wt")
else:
    f = open(OUTPUT_REGRESSION, "xt")

# Header
f.write("Regression;Turn;Planet_count_KI_1;Research_KI_1;Industry_KI_1;Ships_KI_1;Population_KI_1;Planet_count_KI_6;" +
        "Research_KI_6;Industry_KI_6;Ships_KI_6;Population_KI_6;\n")

for i in all_values:
    val = all_values[i] / all_values_count[i]
    f.writelines(str(val) + ";" + i)

f.close()
