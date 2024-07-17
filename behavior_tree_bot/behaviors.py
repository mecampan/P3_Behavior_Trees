import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
import logging

def count_target_planets(state, player, target):
    planet_counts = 0
    fleets = state.my_fleets() if player == 'my' else state.enemy_fleets()

    for fleet in fleets:

        if fleet.destination_planet == target:
            planet_counts += 1

    return planet_counts


def attack_weakest_enemy_planet(state):
    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if count_target_planets(state, "my", weakest_planet.ID) >= 5:
        return False

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    
    elif strongest_planet.num_ships < weakest_planet.num_ships:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)
    else:
        # (4) Send a number of ships from my strongest planet to the weakest enemy planet accounting for travel time
        distance = state.distance(strongest_planet.ID, weakest_planet.ID)
        ship_send = 5 + weakest_planet.num_ships + (weakest_planet.growth_rate * distance)
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, ship_send)

def attack_strongest_enemy_planet(state):
    # (2) Organize my strongest planets.
    my_strongest_planet = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    from_planet = None

    # (3) Find the strongest enemy planet.
    enemy_strongest_planet = max(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    # (4) If we currently have multiple ships being sent to the enemies strongest planet, abort plan.
    if count_target_planets(state, "my", enemy_strongest_planet.ID) >= 5:
        return False
    
    # (5) Cycle through my strongest planet, finding a planet that has not yet sent ships
    ships_sent = False
    for planet in my_strongest_planet:

        for fleet in state.my_fleets():
            ships_sent = False
            if fleet.source_planet == planet.ID and fleet.destination_planet == enemy_strongest_planet.ID:
                ships_sent = True
                break
            
        if ships_sent:
            from_planet = planet

    if not from_planet or not enemy_strongest_planet:
        # No legal source or destination
        return False
    
    elif from_planet.num_ships < enemy_strongest_planet.num_ships:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, from_planet.ID, enemy_strongest_planet.ID, from_planet.num_ships / 2)
    else:
        # (4) Overwhelm enemy planet with numbers
        return issue_order(state, from_planet.ID, enemy_strongest_planet.ID, from_planet.num_ships - 10)

def attack_nearest_enemy_planet(state):
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
        return issue_order(state, strongest_planet.ID, closest.ID, ship_send)


def attack_high_growth_enemy_planet(state):
    # (2) Sort planets by growth rate and check close distances.
    enemy_planets = sorted(state.enemy_planets(), key=lambda p: p.growth_rate)
    distance = None
    closest_distance = float('inf')
    from_planet = None
    to_planet = None
    send_ships = None

    for growth in enemy_planets:
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


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 15:
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
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def spread_to_closest_neutral_planet(state):
    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None) 

    # (3) Find a neutral planet reachable within 5 seconds of travel that can be taken over
    close_planet = None
    distance = None
    ship_send = None

    for closest in state.neutral_planets():
        distance = state.distance(strongest_planet.ID, closest.ID)
        ship_send = 5 + closest.num_ships

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
    targeted_planet_ids = {fleet.destination_planet for fleet in state.my_fleets()}

    # (2) Sort planets by growth rate and check close distances.
    neutral_planets = sorted(state.neutral_planets(), key=lambda p: p.growth_rate, reverse=True)
    distance = None
    closest_distance = float('inf')
    from_planet = None
    to_planet = None
    send_ships = None

    for growth in neutral_planets:
        if growth.ID in targeted_planet_ids:
            continue  # Skip this planet if it's already being targeted

        for closest in state.my_planets():
            distance = state.distance(growth.ID, closest.ID)
            if distance < closest_distance:

                closest_distance = distance
                from_planet = closest
                to_planet = growth
                send_ships = to_planet.num_ships + 5

                if closest_distance <= 5:
                    break

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
    
def target_same_planet_as_enemy(state):
    my_owned_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)

    target_planet = None
    send_from = None
    send_ships = None

    # Iterate through enemy targets
    for planet in state.enemy_fleets():
            
        # Find a target that enemy planet not currently targeted
        if planet.destination_planet not in state.my_fleets():

            # Check to see if there are any owned planets that are close by
            for my_planets in my_owned_planets:
                if state.distance(planet.destination_planet, my_planets.ID) <= 5:
                    target_planet = planet
                    send_from = my_planets
                    break
        
        if target_planet:
            break

    if not target_planet:
        return False
    elif target_planet in state.neutral_planets() or target_planet in state.my_planets():
        send_ships = target_planet.num_ships() + 5
        if send_from.num_ships() >= send_ships:
            return issue_order(state, send_from.ID, target_planet.ID, send_ships)   
        else:
            return issue_order(state, send_from.ID, target_planet.ID, send_from.num_ships / 2)
    else:
        return False

