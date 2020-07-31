"""This class contains shared static variables and functions."""

# Imports
import math
import os

# Static Variables
LOG_STORAGE = "./Log/"
FREEORION_STATISTICS_SUFFIX = ".csv"
FREEORION_STATISTICS_PREFIX = "gamelog"
MAX_TURN = 450

storage_exists = os.path.isdir(LOG_STORAGE)

if not storage_exists:
    # Create directory
    os.mkdir(LOG_STORAGE)


# Functions
def pruning_result(turn, planets_1, research_1, industry_1, ships_1, population_1,
                   planets_2, research_2, industry_2, ships_2, population_2):
    """
    Globally used pruning method.
    The current implementation works by:
    1, waiting for turn 100
    2, Test if industry_1 - industry_2 is < -8.39
    2.1, If yes, then return -1 if the relative industry difference is < -0.193
    2.2, If no, return 1 if planets_1 - planets_2 > 3.5
    Return 0 if no other value has been returned.

    :returns 0 if it's not clear which side wins, 1 if player 1 wins, -1 otherwise
    """
    if turn >= 100:
        industry_comparison_abs = industry_1 - industry_2
        industry_comparison = industry_comparison_abs / \
                              (industry_1 + industry_2)
        if math.isnan(industry_comparison):
            industry_comparison = 0
        planet_comparison_abs = planets_1 - planets_2
        if industry_comparison_abs < -8.3901:
            if industry_comparison < -0.1929:
                return -1
        else:
            if planet_comparison_abs > 3.5:
                return 1

    return 0


def get_results(prune_zero=False):
    """
    Returns the results of all games.
    If prune_zero is set to True, all values with the result 0 are tested: If player one has more research and more
    industry than player 2, than the value is replaced by 1, if player two has more research and more industry than
    player one, than the value is replaced by -1, and 0 if none of these cases is true.
    :return A dictionary containing each file in the Log-directory and 1 if player one won, -1 if player two won and 0
    otherwise. Structured as [filename, result].
    """
    if os.path.isdir(LOG_STORAGE):
        # Get all directories contained here
        dir_list_1 = os.listdir(LOG_STORAGE)

        if dir_list_1 is None or len(dir_list_1) <= 0:
            print("No directories in the log directory. Aborting")
            return None

        result = dict()

        for i in dir_list_1:
            if os.path.isdir(LOG_STORAGE + "/" + i):

                dir_list_2 = os.listdir(LOG_STORAGE + "/" + str(i))
                if dir_list_2 is None or len(dir_list_2) <= 0:
                    # This can happen when an empty directory has been created but not filled.
                    continue

                for a in dir_list_2:
                    file_list = os.listdir(LOG_STORAGE + "/" + str(i) + "/" + str(a))
                    if file_list is None or len(dir_list_2) <= 0:
                        # This can happen when an empty directory has been created but not filled.
                        continue

                    for h in file_list:
                        # Check the file name if it's a log file
                        if not h.startswith(FREEORION_STATISTICS_PREFIX) or not h.endswith(FREEORION_STATISTICS_SUFFIX):
                            # Ignore this file, someone has stored addtional information we don't need
                            continue

                        # Read the csv and take the last line
                        file_name = LOG_STORAGE + "/" + str(i) + "/" + str(a) + "/" + str(h)
                        f = open(file_name, "rt")

                        # From https://stackoverflow.com/questions/46258499/read-the-last-line-of-a-file-in-python
                        line = 0
                        for line in f:
                            pass
                        last_line = line

                        f.close()

                        win_loose = 0
                        split = last_line.split(";")
                        # print(str(split[1]) + ", " + last_line)
                        if split[1] == "0":
                            win_loose = -1
                        elif split[6] == "0":
                            win_loose = 1
                        elif int(split[0]) < MAX_TURN:
                            # Test if we've pruned it before, otherwise declare it as 0
                            win_loose = pruning_result(int(split[0]), int(split[1]), float(split[2]),
                                                       float(split[3]), int(split[4]), float(split[5]),
                                                       int(split[6]), float(split[7]),
                                                       float(split[8]), int(split[9]), float(split[10]))
                        elif not prune_zero:
                            # We've cutted of playing, so no one is the winner
                            win_loose = 0
                        elif prune_zero:
                            # Prune zeros as they can cause troubles
                            # Every game where research and production of one side are bigger by any means,
                            # it's set
                            if float(split[2]) > float(split[7]) and \
                                    float(split[3]) > float(split[8]):
                                win_loose = 1
                            elif float(split[2]) < float(split[7]) and \
                                    float(split[3]) < float(split[8]):
                                win_loose = -1
                            else:
                                win_loose = 0

                        # print(str(win_loose))
                        result[str(file_name)] = win_loose

            else:
                # Ignore it, this can happen
                pass

        return result

    else:
        print("Log-Directory not found.")
        return None
