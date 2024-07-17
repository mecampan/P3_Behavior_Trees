import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
import logging

def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 10:
        logging.info("Too many actions in play")
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    
    elif strongest_planet.num_ships < weakest_planet.num_ships:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2 )
    else:
        # (4) Send a number of ships from my strongest planet to the weakest enemy planet accounting for travel time
        distance = state.distance(strongest_planet.ID, weakest_planet.ID)
        ship_send = 5 + weakest_planet.num_ships + (weakest_planet.growth_rate * distance)
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, ship_send)

def attack_nearest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 5:
        return False
     # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find a enemys planet reachable within 5 seconds of travel that can be taken over
    close_planet = None
    distance = None
    ship_send = None

    for closest in state.enemy_planets():
        distance = state.distance(strongest_planet.ID, closest.ID)
        ship_send = 5 + closest.num_ships + (closest.growth_rate * distance)

        if distance <= 10 and strongest_planet.num_ships >= ship_send:
            close_planet = closest
            break
    if not strongest_planet or not close_planet:
        # No legal source or destination
        return False
    else:
    # (4) Send a number of ships from my strongest planet to the enemy's planet to accounting for the time of travel.
        return issue_order(state, strongest_planet.ID, closest.ID, ship_send + 1)

def attack_high_growth_enemy_planet(state):
    # (1) If we currently have 5 fleets in flight, just do nothing.
    if len(state.my_fleets()) >= 5:
        return False
    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)
    # (3) Sort planets by growth rate and check close distances.
    enemy_planets = sorted(state.enemy_planets(), key=lambda p: p.growth_rate, reverse=True)
    target_planet = None
    for planet in enemy_planets:
        distance = state.distance(strongest_planet.ID, planet.ID)
        ship_send = 5 + planet.num_ships + (planet.growth_rate * distance)
        if distance <= 10 and strongest_planet.num_ships >= ship_send:
            target_planet = planet
            break
    if not strongest_planet or not target_planet:
        # No legal source or destination
        return False
    else:
        return issue_order(state, strongest_planet, target_planet, ship_send)
    
def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 5:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, weakest_planet.num_ships + 20)

def spread_to_closest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 5:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None) 

    # (3) Find a neutral planet reachable within 5 seconds of travel that can be taken over
    close_planet = None
    distance = None
    ship_send = None

    for closest in state.neutral_planets():
        distance = state.distance(strongest_planet.ID, closest.ID)
        ship_send = 10 + closest.num_ships

        if distance <= 10 and strongest_planet.num_ships >= ship_send:
            close_planet = closest
            break

    if not strongest_planet or not close_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send a number of ships from my strongest planet to the neutral planet to accounting for the time of travel.
        return issue_order(state, strongest_planet.ID, close_planet.ID, ship_send)
    
def spread_to_high_growth_neutral_planet(state):
    # (1) If we currently have 5 fleets in flight, just do nothing.
    if len(state.my_fleets()) >= 5:
        return False
    
    # (2) Sort planets by growth rate and check close distances.
    neutral_planets = sorted(state.neutral_planets(), key=lambda p: p.growth_rate)
    distance = None
    closest_distance = float('inf')
    from_planet = None
    to_planet = None
    send_ships = None

    for growth in neutral_planets:
        for closest in state.my_planets():
            distance = state.distance(growth.ID, closest.ID)

            if distance < closest_distance:
                closest_distance = distance
                from_planet = closest
                to_planet = growth
                send_ships = to_planet.num_ships + 5

                if closest_distance <= 5:
                    break


    if not from_planet or not to_planet:
        # No legal source or destination
        return False
    elif from_planet.num_ships < send_ships:
        return False
    else:
        # (3) Send a number of ships from the closests planet to the neutral planet to accounting for the time of travel.
        return issue_order(state, from_planet.ID, to_planet.ID, send_ships)
