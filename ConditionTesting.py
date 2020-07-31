"""Test the pruning stategy implemented in FreeOrionSharedFunctionality by
running it on all currently stored logs in the log directory."""

# Imports
import FreeOrionSharedFunctionality

# Variables

# The true game results on which the pruning strategy will be tested on.
# All results with 0 are pruned to either 1 or -1 so that the pruning mechanism gives back better results.
results = FreeOrionSharedFunctionality.get_results(True)
amount_games = len(results)
# Misclassified entries.
misclassified_list = list()
correctly_classified = 0
total_lines_in_files = 0
# The amount of lines that didn't needed to be calculated. This value is flawed as the computation
# is stopped when it takes too long (see FreeOrionSharedFunctionality for more details).
lines_pruned = 0

# Start testing all currently known log files
for i in results:
    # Get the file.
    file_name = i
    if results[i] == 0:
        # Those are ignored because those results won't tell us too much about the pruning algorithm.
        amount_games -= 1
        continue
    f = open(file_name, "rt")
    line_counter = 0

    # Get into the file and find out at which point the values can be pruned.
    for line in f:
        if line_counter == 0:
            # Skipt this line as it's the first line
            line_counter += 1
            continue
        split = line.split(";")
        prune_return = FreeOrionSharedFunctionality.pruning_result(int(split[0]), int(split[1]), float(split[2]),
                                                                   float(split[3]), int(split[4]),
                                                                   float(split[5]), int(split[6]), float(split[7]),
                                                                   float(split[8]), int(split[9]), float(split[10]))

        # Only prune if the pruning function gives back either 1 or -1, so 0 means keep on calculating.
        if prune_return != 0:
            # We've got a result.
            if prune_return == results[i]:
                correctly_classified += 1
            else:
                misclassified_list.append(i)
            # break from the loop
            break

        line_counter += 1

    line_counter_pruned = 0
    for line in f:
        line_counter_pruned += 1

    total_lines_in_files += line_counter
    total_lines_in_files += line_counter_pruned
    lines_pruned += line_counter_pruned
    f.close()

# Give back some nice-looking results.
print("Results: ")
print("Total Games: \t" + str(amount_games) + "\nMisclassified: \t" + str(len(misclassified_list)) +
      "\nMisclassified-Rate: \t" + str((len(misclassified_list) / amount_games)))
print("Percent Lines Pruned: " + str((lines_pruned / total_lines_in_files)))
print("Misclassified: ")
for i in misclassified_list:
    print("\t" + str(i))
