"""
This script is made to start and restart FreeOrion in order to collect data about the self-play of the AI.
This script starts the Server for FreeOrion, starts a game of 1 vx 1 (AI only) with the given parameters and
then listens to the network interface (in order to keep the server running).
During that the script observes the performance of the game so that the game is ended (by killing the server)
when the game is set for one side.
The statistical information is collected in a sub-folder of this project.
"""

# Imports
import sys
import os
import subprocess
import time
import socket
import xml.etree.ElementTree as ET
import string
import random
import shutil
import FreeOrionSharedFunctionality

# Global fixed variables (should be changed to change the behaviour of the script but should not be changed by the
# script itself.)

# The target amount of log files per directory.
TARGET_DATA_FILE_COUNT = 71
# States if the script should use the pruning function for cutting of the game.
# True = Pruning is turned on and will be used (faster but less pricese games).
# False = Pruning won't be used (way slower but more pricese games).
DO_PRUNING = False
FREEORION_SPECIES_CONFIG_DIRECTORY = "/home/user/freeOrion/freeorion/default/scripting/species/"
FREEORION_STATISTICS_DIRECTORY = "/home/user/freeOrion/freeorion/default/python/turn_events/"
FREEORION_SERVER_LOCATION = "/home/user/freeOrion/freeorion/build/freeoriond"
# Used to fake FreeOrion-Client-messages.
STR_DOCTYPE = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>\n" + \
              "<!DOCTYPE boost_serialization>\n"
STR_DOCTYPE = bytearray(STR_DOCTYPE, encoding="UTF-8")
# Socket address of the server
FREEORION_SERVER_ADDRESS = ("localhost", 12346)

"""Check Variables"""
server_exists = os.path.exists(FREEORION_SERVER_LOCATION)
species_exists = os.path.isdir(FREEORION_SPECIES_CONFIG_DIRECTORY)
statistics_exists = os.path.isdir(FREEORION_STATISTICS_DIRECTORY)

print("Server exists: " + str(server_exists))
print("Species-directory exists: " + str(species_exists))
print("Statistics-directory exists: " + str(statistics_exists))

if not server_exists or not species_exists or not statistics_exists:
    print("Check the path variables: One of the pathes doesn't point to a valid target!")


# Global Functions
def species():
    """Get all species playable
        :returns A list of strings containing all species with the value "\n    Playable" in their focs-files.
    """
    # Go into the species directory and get all files
    files_list = os.listdir(FREEORION_SPECIES_CONFIG_DIRECTORY)
    species_list_def = list()
    for i_species in files_list:
        # print("Reading file " + str(i))
        if i_species.endswith(".focs.txt"):
            # Check if file contains the string playable
            with open(FREEORION_SPECIES_CONFIG_DIRECTORY + "/" + str(i_species)) as f:
                text_content = f.read()
                if "\n    Playable\n" in text_content:
                    print("File contains starting-species information.")
                    species_list_def.append(str(i_species).replace(".focs.txt", ""))
    return species_list_def


def read_next_n_bytes(socket_read, n):
    """Read the next n bytes from the socket. If there are no bytes available on the socket,
    the function sleeps for one seconds and tries it again."""
    if n <= 0:
        return [0]
    received = 0
    while not received:
        received = socket_read.recv(n)
        if not received:
            time.sleep(1)
    return received


def random_string(string_length=8):
    """Creates random strings of ASCII-letters."""
    # From https://pynative.com/python-generate-random-string/
    # letters = string.ascii_lowercase
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(string_length))


def set_player(xmlelem, species_def):
    """Takes the item (from an xml-document) representing a player and changes the species to the given species.
    Also add the species name to the player name for later use."""
    # Get the second element of that list (don't know what the first one is doing here, but the
    # communication seems to need it).
    first_second = list(xmlelem)
    data = first_second[1]
    # Change the player name
    settings_player = list(data)
    for i2 in settings_player:
        if i2.tag == "m_player_name":
            i2.text = i2.text + "_" + species_def
        elif i2.tag == "m_starting_species_name":
            i2.text = species_def


# Identify the species playable at the start of the game and print them.
species_list = species()

print("Stored species: ")
for i in species_list:
    print("\t" + i)

# Start all games and play X games where X is the difference between TARGET_DATA_FILE_COUNT and the
# already existing files in the directory of that species-combination.
# WARNING: Recombination: Species1 vs Species2 is considered equal to Species2 vs Species1

for r1 in range(len(species_list)):
    for r2 in range(len(species_list)):
        if r2 <= r1:
            # Recombination: Drop it as we have done that one before.
            continue

        # Count how many files we need to reach the target
        # From https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
        file_count = 0
        try:
            species_directory = FreeOrionSharedFunctionality.LOG_STORAGE + "/" + species_list[r1] + "/" + species_list[
                r2]
            if os.path.isdir(species_directory):
                # currently a primitive "count all files in that directory and don't care what file it's". This
                # means that we have to keept the log-directories clear and tidy
                file_count = len([f for f in os.listdir(species_directory) if os.path.isfile(
                    os.path.join(species_directory, f))])
        except:
            # Do nothing when error occurred
            file_count = 0

        to_calc = TARGET_DATA_FILE_COUNT - file_count
        # Fail-safe state when there are errors
        if to_calc < 0:
            to_calc = 0

        # For every file we have to create:
        # Start a game by starting the server and sending fake messages
        # When the server is started, watch the log files.
        # When one file indicates a victory for one side, stop the game (by killing the server) and
        # move the log into our directory.
        for i in range(to_calc):
            print("Starting round " + str(i) + " of " + str(species_list[r1]) + " vs " + str(species_list[r2])
                  + " of " + str(to_calc))

            # Kill any instance of freeoriond if one is still running
            retcode = subprocess.call(["killall", "freeoriond"])

            if retcode == 0:
                # Wait until kill takes effect
                # Strange but true, in some cases FreeOrion doesn't free the used port instantly -->
                # The new FreeOrion-Instance may protest that the port is still in use.
                time.sleep(10)

            # Clean all not-used logs in the log-directory given above
            # os.system ran without problems in this context although changing it to subprocess.call produces more
            # redundant code.
            os.system("rm " + FREEORION_STATISTICS_DIRECTORY + "" +
                      FreeOrionSharedFunctionality.FREEORION_STATISTICS_PREFIX +
                      "*" + FreeOrionSharedFunctionality.FREEORION_STATISTICS_SUFFIX)

            # Start the server
            freeorion_server_process = subprocess.Popen([FREEORION_SERVER_LOCATION, "--hostless"], shell=False,
                                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # To play it safe, sleep here for a second (or two)
            time.sleep(2)
            server_socket = socket.create_connection(FREEORION_SERVER_ADDRESS)
            # A mode to tell the software what to do and when
            mode = 0

            # Setting the parameters and starting the game
            # Greetings message from version v0.4.9
            msg_1 = b"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>\n" + \
                    b"<!DOCTYPE boost_serialization>\n" + \
                    b"<boost_serialization signature=\"serialization::archive\" version=\"17\">\n" + \
                    b"<player_name>Observerr</player_name>\n" + \
                    b"<client_type>2</client_type>\n" + \
                    b"<client_version_string>v0.4.9 HEAD [build 2020-02-02.db53471] CMake</client_version_string>\n" + \
                    b"<cookie>00000000-0000-0000-0000-000000000000</cookie>\n" + \
                    b"</boost_serialization>\n\n"

            # Dirty workaround to create the message.
            header_1 = (5).to_bytes(4, byteorder="little")
            length_1 = len(msg_1).to_bytes(4, byteorder="little")
            msg_1_total = header_1 + length_1 + msg_1

            server_socket.send(msg_1_total)

            while mode < 2:
                # We're in the lobby, so process the incomming xml-like files and try to start the server.
                rec_msg_head = list(read_next_n_bytes(server_socket, 8))
                rec_msg_length = int.from_bytes(rec_msg_head[4:8], "little")
                rec_msg_type = int.from_bytes(rec_msg_head[:1], "little")

                # print(str(rec_msg_length) + ", " + str(rec_msg_head))

                data_to_process = read_next_n_bytes(server_socket, rec_msg_length)

                # mode 0 is the mode where we are setting up the lobby for the target game settings
                if mode == 0 and rec_msg_type == 7:
                    # Read the data as xml
                    parser = ET.fromstring(data_to_process)

                    # From https://docs.python.org/3/library/xml.etree.elementtree.html
                    # and from
                    # https://stackoverflow.com/questions/25428751/print-out-xml-to-the-console-xml-etree-elementtree
                    lobby_data = list(parser)[0]
                    # Go through the tree and change the elements we wanted changed
                    for elem in list(lobby_data):
                        # print(elem.tag)
                        if elem.tag == "GalaxySetupData":
                            for elem2 in list(elem):
                                if elem2.tag == "m_seed":
                                    # Sometimes, this value isn't random, so play it safe here
                                    elem2.text = random_string()
                                    # print("New Seed: " + elem.text)

                                elif elem2.tag == "m_size":
                                    # Set it to an amount advised in the tool tip:
                                    # The advice is to set it between 15 and 30 systems per player, we've got two
                                    # players so we can set it to a medium 45
                                    elem2.text = "45"

                                elif elem2.tag == "m_ai_aggr":
                                    # Set the AI-Aggression to "maniac".
                                    # This is a personal setting to speed up calculation.
                                    elem2.text = "5"

                                elif elem2.tag == "m_shape":
                                    # Give it a random shape. I'm not sure if this matters, but I wanted to play it safe
                                    elem2.text = "9"

                                elif elem2.tag == "m_age":
                                    # Set the galaxy age
                                    elem2.text = "2"

                                elif elem2.tag == "m_starlane_freq":
                                    # Set the starlane frequency
                                    elem2.text = "2"

                                elif elem2.tag == "m_planet_density":
                                    # Set the planet density
                                    elem2.text = "2"

                                elif elem2.tag == "m_specials_freq":
                                    # Set the special density
                                    elem2.text = "2"

                                elif elem2.tag == "m_monster_freq":
                                    # Set the monster frequency
                                    elem2.text = "2"

                                elif elem2.tag == "m_native_freq":
                                    # Set the native frequency
                                    elem2.text = "2"
                            # I dropped the other game rules. This is not wise as e.g. the Experimentator have a
                            # huge influence on the game, but here I'll just state that I didn't changed the values
                            # from the original git-commit.
                            # By now, I think this would have been too much of hard coding.

                        if elem.tag == "m_players":
                            # Change the players in the game
                            # Because of the additional informations stored (xml-tags in the document),
                            # we'll remove all players except the
                            # first one and the last two ones (where we're one of the last two ones)
                            player_count = None
                            m_players_children = list(elem)
                            for elem2 in m_players_children:
                                if elem2.tag == "count":
                                    player_count = elem2
                                    if int(player_count.text) <= 2:
                                        # We've got big troubles. End the program and give an error message
                                        msg = "The standard starting conditions for the program are not given: The " + \
                                              "Server starts with too few AI players. This script currently can't " \
                                              "handle " + \
                                              "this case. Please try again when the standard configuration has changed."
                                        print(msg)
                                        sys.exit(msg)

                            # Now we need to delete elements to have a count of two (plus us)
                            to_delete = int(player_count.text) - 3
                            for h in range(to_delete):
                                elem.remove(m_players_children[3 + h])

                            # Now set the player count correctly again & change the species of the remaining AIs
                            player_count.text = "3"
                            m_players_children = list(elem)
                            set_player(m_players_children[2], species_list[r1])
                            set_player(m_players_children[3], species_list[r2])

                    # Now that we've set all this, send it back to the server
                    # Dirty Workaround for the header of the xml file

                    # From https://stackoverflow.com/questions/28813876/how-do-i-get-pythons-elementtree-to-pretty-print-to-an-xml-file
                    xml_str = ET.tostring(parser, short_empty_elements=False, method="xml") + b"\n"
                    xml_str = STR_DOCTYPE + xml_str
                    # From https://stackoverflow.com/questions/606191/convert-bytes-to-a-string
                    # print(xml_str.decode("UTF-8"))
                    header_2 = (7).to_bytes(4, byteorder="little")
                    length_2 = len(xml_str).to_bytes(4, byteorder="little")
                    msg_2_total = header_2 + length_2 + xml_str

                    server_socket.send(msg_2_total)

                    mode = 1

                # Here we send an "we're ready for the game to start" answear when we get the correct header.
                # All other headers are ignored.
                elif mode == 1 and rec_msg_type == 7:
                    # We now set our readiness to ready and so the game starts
                    parser = ET.fromstring(data_to_process)
                    lobby_data = list(parser)[0]
                    for elem in list(lobby_data):
                        if elem.tag == "m_players":
                            players = list(elem)
                            observer = players[4]
                            settings = list(list(observer)[1])
                            for elem2 in settings:
                                if elem2.tag == 'm_player_ready':
                                    elem2.text = "1"
                                    break
                            break

                    xml_str = ET.tostring(parser, short_empty_elements=False, method="xml") + b"\n"
                    xml_str = STR_DOCTYPE + xml_str
                    # From https://stackoverflow.com/questions/606191/convert-bytes-to-a-string
                    # print(xml_str.decode("UTF-8"))
                    header_2 = (7).to_bytes(4, byteorder="little")
                    length_2 = len(xml_str).to_bytes(4, byteorder="little")
                    msg_2_total = header_2 + length_2 + xml_str

                    server_socket.send(msg_2_total)

                    mode = 2

            # Now the game is started.
            # We need to observing the statistics
            # Subprocess for the tail-instruction
            tails = None
            game_finished = False
            # Full position of the log file
            log_name = ""
            print("Game started.")

            # The server seems to be a little stubburn when we don't read out the very first messages of the
            # game start (it simply does nothing and wait for us).
            # So the socket is simply read out (yes, we are supposed to read faster then the server
            # writes) and closed afterwards. In this case the server keeps on running instead of waiting idly.
            # From https://stackoverflow.com/questions/409783/socket-shutdown-vs-socket-close
            time.sleep(1)
            server_socket.setblocking(False)
            try:
                while True:
                    server_socket.recv(1024)
            except TimeoutError:
                # Do nothing
                pass
            except BlockingIOError:
                # Nothing on the line, so go on with it.
                pass
            server_socket.shutdown(socket.SHUT_RDWR)
            server_socket.close()

            # While the game is not finished yet, read out the statistics and decide if the game is finished.
            while not game_finished:
                if tails is None:
                    # Check if we can start a subprocess for tails -f out of one of the statistics files
                    files = os.listdir(FREEORION_STATISTICS_DIRECTORY)
                    for f in files:
                        if f.startswith(FreeOrionSharedFunctionality.FREEORION_STATISTICS_PREFIX) and \
                                f.endswith(FreeOrionSharedFunctionality.FREEORION_STATISTICS_SUFFIX):
                            # Take this one
                            log_name = f
                            tails = subprocess.Popen(["tail", "-f", FREEORION_STATISTICS_DIRECTORY + log_name],
                                                     stdout=subprocess.PIPE)
                            break

                if not (tails is None):
                    # From https://stackoverflow.com/questions/2804543/read-subprocess-stdout-line-by-line
                    # and from https://stackoverflow.com/questions/18421757/live-output-from-subprocess-command
                    # Read out the tail-function and analyse the results.
                    while True:
                        line = tails.stdout.readline()
                        if not line:
                            break

                        # print(line)
                        line_string = line.decode(encoding="UTF-8", errors="ignore")
                        splitted = line_string.split(";")
                        # print(splitted[1] + ", " + splitted[6])

                        # Finish the game if one side has no more planets or if the pruning-function says so.
                        try:
                            # print("Turn: " + str(splitted[0]) + ", Minimum Amount of Planets: " + str(
                            #     min(int(splitted[1]), int(splitted[6]))
                            # ))
                            if int(splitted[1]) <= 0 or int(splitted[6]) <= 0:
                                game_finished = True
                                print("One side lost all planets.")
                                break
                            elif int(splitted[0]) >= FreeOrionSharedFunctionality.MAX_TURN:
                                # Prevent the game from equilibrium
                                game_finished = True
                                print("Maximum amount of turns reached: Draw.")
                                break
                            elif DO_PRUNING:
                                pruning_return = FreeOrionSharedFunctionality.pruning_result(int(splitted[0]),
                                                                                             int(splitted[1]),
                                                                                             float(splitted[2])
                                                                                             , float(splitted[3]),
                                                                                             int(splitted[4]),
                                                                                             float(splitted[5]),
                                                                                             int(splitted[6]),
                                                                                             float(splitted[7]),
                                                                                             float(splitted[8]),
                                                                                             int(splitted[9]),
                                                                                             float(splitted[10]))
                                if pruning_return != 0:
                                    game_finished = True
                                    print("Game finished because of pruning.")
                                    break
                        except ValueError as e:
                            # The first row is text only, so ignore this error gently
                            pass

            # Quiting and cleaning
            tails.kill()
            freeorion_server_process.kill()
            # To prevent Defunct-zombies in the process list
            # Working solution from https://www.reddit.com/r/learnpython/comments/776r96/defunct_python_process_when_using_subprocesspopen/
            while freeorion_server_process.poll() is None:
                time.sleep(1)
            # Play it save: https://stackoverflow.com/questions/21936597/blocking-and-non-blocking-subprocess-calls
            # indicates that the process keeps on running when calling terminate(). As kill() is the new terminate,
            # I'll call a process kill here as well.
            # retcode = subprocess.call(["killall", "freeoriond"])
            # retcode = subprocess.call(["killall", "tail"])

            # Wait until all resources are freed again
            # Kommented out as the Kill-instruction at the beginning of the loop triggers also.
            # time.sleep(10)

            # copy the game log into a directory structure we'll build up
            species_directory_1 = FreeOrionSharedFunctionality.LOG_STORAGE + "/" + species_list[r1]
            species_directory_1_exists = os.path.isdir(species_directory_1)
            if not species_directory_1_exists:
                os.mkdir(species_directory_1)
            species_directory_2 = species_directory_1 + "/" + species_list[r2]
            species_directory_2_exists = os.path.isdir(species_directory_2)
            if not species_directory_2_exists:
                os.mkdir(species_directory_2)

            # now copy the new gamelog into the species directory
            # From https://stackoverflow.com/questions/8858008/how-to-move-a-file
            # I kept shutil as I first tried copy methods, but shutil can be used for moving as well, so I kept it
            shutil.move(FREEORION_STATISTICS_DIRECTORY + log_name, species_directory_2 + "/" + log_name)

            print("Copy completed, shutdown ordered, now get on with the next game.")
