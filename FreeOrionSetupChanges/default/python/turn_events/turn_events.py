from common.configure_logging import redirect_logging_to_freeorion_logger

# Logging is redirected before other imports so that import errors appear in log files.
redirect_logging_to_freeorion_logger()

import sys
from random import random, uniform, choice
from math import sin, cos, pi, hypot
import os.path

import freeorion as fo
from universe_tables import MONSTER_FREQUENCY


def execute_turn_events():
    print "Executing turn events for turn", fo.current_turn()

    # creating fields
    systems = fo.get_systems()
    radius = fo.get_universe_width() / 2.0
    if random() < max(0.0003 * radius, 0.03):
        if random() < 0.4:
            field_type = "FLD_MOLECULAR_CLOUD"
            size = 5.0
        else:
            field_type = "FLD_ION_STORM"
            size = 5.0

        x = y = radius
        dist_from_center = 0.0
        while (dist_from_center < radius) or any(hypot(fo.get_x(s) - x, fo.get_y(s) - y) < 50.0 for s in systems):
            angle = random() * 2.0 * pi
            dist_from_center = radius + uniform(min(max(radius * 0.02, 10), 50.0), min(max(radius * 0.05, 20), 100.0))
            x = radius + (dist_from_center * sin(angle))
            y = radius + (dist_from_center * cos(angle))

        print "...creating new", field_type, "field, at distance", dist_from_center, "from center"
        if fo.create_field(field_type, x, y, size) == fo.invalid_object():
            print >> sys.stderr, "Turn events: couldn't create new field"

    # creating monsters
    gsd = fo.get_galaxy_setup_data()
    monster_freq = MONSTER_FREQUENCY[gsd.monsterFrequency]
    # monster freq ranges from 1/30 (= one monster per 30 systems) to 1/3 (= one monster per 3 systems)
    # (example: low monsters and 150 Systems results in 150 / 30 * 0.01 = 0.05)
    if monster_freq > 0 and random() < len(systems) * monster_freq * 0.01:
        # only spawn Krill at the moment, other monsters can follow in the future
        if random() < 1:
            monster_type = "SM_KRILL_1"
        else:
            monster_type = "SM_FLOATER"

        # search for systems without planets or fleets
        candidates = [s for s in systems if len(fo.sys_get_planets(s)) <= 0 and len(fo.sys_get_fleets(s)) <= 0]
        if not candidates:
            print >> sys.stderr, "Turn events: unable to find system for monster spawn"
        else:
            system = choice(candidates)
            print "...creating new", monster_type, "at", fo.get_name(system)

            # create monster fleet
            monster_fleet = fo.create_monster_fleet(system)
            # if fleet creation fails, report an error
            if monster_fleet == fo.invalid_object():
                print >> sys.stderr, "Turn events: unable to create new monster fleet"
            else:
                # create monster, if creation fails, report an error
                monster = fo.create_monster(monster_type, monster_fleet)
                if monster == fo.invalid_object():
                    print >> sys.stderr, "Turn events: unable to create monster in fleet"

    # Store statistics
    try:
        # Check if we simply append a file or if we have to open a new one
        use_first_line = False
        if not(os.path.isfile("gamelog" + fo.get_galaxy_setup_data().gameUID + ".csv")):
            use_first_line = True
        f = open("gamelog" + fo.get_galaxy_setup_data().gameUID + ".csv", "a+")
        if use_first_line:
            # Writing the headers as this file is a new one
            f.write("Turn;")

            for i in fo.get_all_empires():
                empire = fo.get_empire(i)
                name = empire.playerName
                f.write("Planet_count_" + str(name) + ";")
                f.write("Research_" + str(name) + ";")
                f.write("Industry_" + str(name) + ";")
                # f.write("Stockpile_" + str(name) + ";")
                f.write("Ships_" + str(name) + ";")
                f.write("Population_" + str(name) + ";")

            f.write("\n")


        # Inserting data
        to_write = "" + str(fo.current_turn()) + ";"

        # For each player store the basic meters:
        # How many planets are owned (colonies + outposts), current research, current production
        # Ship count, number of inhabitants
        count_planet = dict()
        research = dict()
        industry = dict()
        stockpile = dict()
        ship_count = dict()
        population = dict()

        universe = fo.get_universe()
        for sid in fo.get_systems():
            for pid in fo.sys_get_planets(sid):
                planet = universe.getPlanet(pid)
                if not(str(planet.owner) in population):
                    population[str(planet.owner)] = 0
                    count_planet[str(planet.owner)] = 0
                    research[str(planet.owner)] = 0
                    industry[str(planet.owner)] = 0
                    # stockpile[str(planet.owner)] = 0

                count_planet[str(planet.owner)] = count_planet[str(planet.owner)] + 1
   #             research[str(planet.owner)] = research[str(planet.owner)] + planet.getMeter(
    #                fo.meterTyp.research).current
 #               industry[str(planet.owner)] = industry[str(planet.owner)] + planet.getMeter(
  #                  fo.meterType.industry).current
                population[str(planet.owner)] = population[str(planet.owner)] + planet.getMeter(fo.meterType.population).current

        for sid in universe.shipIDs:
            ship = universe.getShip(sid)
            ownerEmpireID = ship.owner
            if not(str(ownerEmpireID) in ship_count):
                ship_count[str(ownerEmpireID)] = 0
            ship_count[str(ownerEmpireID)] = ship_count[str(ownerEmpireID)] + 1

        empires = fo.get_all_empires()
        for i in empires:
            empire = fo.get_empire(i)
            research["" + str(empire.empireID)] = empire.resourceProduction(fo.resourceType.research)
            industry["" + str(empire.empireID)] = empire.resourceProduction(fo.resourceType.industry)
            # stockpile["" + str(empire.empireID)] = empire.resourceProduction(fo.resourceType.stockpile)


#         for pop in population:
        # from https://stackoverflow.com/questions/4990718/about-catching-any-exception
        for i in empires:
            # Ignore "no-owner"
            if i != -1:
                i2 = "" + str(i)
                try:
                    to_write = to_write + str(count_planet[i2]) + ";" + str(research[i2]) + ";" + str(industry[i2]) +\
                               ";" + str(ship_count[i2]) + ";" + str(population[i2]) + ";"
                except:
                    # Simply fill it with zeros
                    to_write = to_write + "0;0;0;0;0;"

        '''";" + str(stockpile[i]) +'''
        f.write(to_write + "\n")

        # And close everything
        f.close()

    except Exception as e:
        # do nothing
        print >> sys.stderr, "Turn events: unable to write to file, " + str(repr(e))


    return True
