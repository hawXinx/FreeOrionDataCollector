"""
This file is supposed to create a csv-file which contains file-result-pairs.
Therefore, it climbs down the tree of the Log-directory, opens every file contained there,
reads out the last line, and stores the name of the file as well as the result of analysing
the last line in a file called DataResults.csv
WARNING: This script should NOT be used on files created by pruning. This is because the script does NOT
measure by pruning but by the real end result (one side lost all planets)!
"""

import os
import sys
import FreeOrionSharedFunctionality

RESULT = "result.csv"

result = FreeOrionSharedFunctionality.get_results()

if result is None:
    sys.exit(1)

f2 = None
if os.path.isfile(RESULT):
    f2 = open(RESULT, mode="wt")
else:
    f2 = open(RESULT, mode="xt")

# Write the first line of the document
f2.write("File;Result\n")

for file_name in result:
    # Write it to the csv file
    # Only print the race and the game file
    win_loose = result[str(file_name)]
    split = file_name.split("/")
    small_file_name = split[len(split) - 3] + "/" + split[len(split) - 2] + "/" + split[len(split) - 1]
    f2.write("" + str(small_file_name) + ";" + str(win_loose) + "\n")

f2.close()
