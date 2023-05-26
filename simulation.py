# -*- coding: utf-8 -*-
"""Copia di simulation_of_a_parkinglot.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BCB-H3Bz0cM0ZHoMrI4z2j_JJHvUf1Q6
"""

#pip install simpy

"""Companion code to https://realpython.com/simulation-with-simpy/

'Simulating Real-World Processes With SimPy'

Python version: 3.7.3
SimPy version: 3.0.11
"""

import simpy
import random
import statistics
from functools import reduce
from utils import *
from JsonReader import *

wait_times = []

# I didn't choose any of the time-inputs, so don't look at me

class VehicleType:
    def __init__(self, type_name, free_travel_time, size):
        self.free_travel_time = free_travel_time
        self.size = size
        self.name = type_name

class VehicleToken:
    def __init__(self, vehicle_type=None, free_travel_time=None, creation_time=None):
        self.vehicle_type = vehicle_type
        self.free_travel_time = free_travel_time
        self.creation_time = creation_time
        self.total_travel_time = None
        self.activation_time = None

    def activate(self, activation_time, queue_wait_time):
        self.activation_time = activation_time
        self.total_travel_time = self.free_travel_time + queue_wait_time
        self.outside_queue_wait_time = self.activation_time - self.creation_time
        self.total_wait_time = self.outside_queue_wait_time + self.total_travel_time
        return self

    def time_left(self, current_time):
        if self.activation_time is None:
            raise ValueError("cannot compute time left if token has not been activated")
        return (self.activation_time + self.total_travel_time) - current_time

    def time_since_creation(self, current_time):
        return current_time - self.creation_time

class Vehicle:
    def __init__(self, id, vehicle_type, graph, start, end, parking_step=None):
        self.current_position = -1
        self.type = vehicle_type
        self.id = id
        
        if parking_step is not None:
            self.path = graph.make_path(start, parking_step, self.type.name)[:-1] + graph.make_path(parking_step, end, self.type.name)
        else:
            self.path = graph.make_path(start, end, self.type.name)
        
        print(f'PATH: {self.path}')
        

    def has_left(self):
        return self.current_position == len(self.path)

    def advance(self):
        self.current_position += 1
        return (
            None if self.current_position == 0 else self.path[self.current_position - 1],
            None if self.has_left() else self.path[self.current_position]
        )


    def queue_node_transitions(self, env, true_token, previous_node=None, next_node=None):
        if next_node is None:
            yield env.process(self.perform_node_transfers(env, previous_node=previous_node))
            return

        with next_node.queue_lock.request() as lock:
            yield lock
            print(f'#[{env.now:.2f}] car {self.id} has got the lock for node {next_node.id}')
            yield env.process(self.perform_node_transfers(env, true_token, previous_node, next_node))
        
        print(f'#[{env.now:.2f}] car {self.id} has released the lock for node {next_node.id}')

    def perform_node_transfers(self, env, true_token=None, previous_node=None, next_node=None):
        for i in range(self.type.size - 1):
            yield env.process(self.perform_node_transfer(env, previous_node, next_node))

        yield env.process(self.perform_node_transfer(env, previous_node, next_node, true_token))

    def perform_node_transfer(self, env, previous_node=None, next_node=None, token=VehicleToken()):
        def token_str(t):
            return 'true' if t.vehicle_type is not None else 'dummy'

        if next_node is not None:
            yield next_node.store.put(token)
            print(f"#[{env.now:.2f}] car {self.id} has placed a {token_str(token)} token in node {next_node.id}")

        if previous_node is not None:
            get_request = yield previous_node.store.get()
            print(f"#[{env.now:.2f}] car {self.id} has removed a {token_str(get_request)} token in node {previous_node.id}")

        


    


class Config:
    def __init__(self, initial_time, gate_opening_time):
        self.initial_time = initial_time
        self.gate_opening_time = gate_opening_time   


class ParkingLot(object):

    def __init__(self, env, metrics, config):
        self.env = env
        self.metrics = metrics
        self.config = config

    # what can the cars do

    # once the car comes in the entrance gate, the goal is to park it:
    # find a parking slot available (we should think of the type of vehicle/parking space)
    def park(self, car, previous_road, parking_spot):
        token = VehicleToken(car.type, 0, self.env.now) # vehicles do not take any time "travelling" through parking spots
        print(f"[{self.env.now:.2f}] car {car.id} is ready to park at spot {parking_spot.id}")

        yield self.env.process(car.queue_node_transitions(self.env, token, previous_road, parking_spot))
        print(f"[{self.env.now:.2f}] car {car.id} has left road {previous_road.id} and parked at spot {parking_spot.id}")
        self.metrics.acknowledge_count_change(previous_road, self.env.now)
        self.metrics.acknowledge_count_change(parking_spot, self.env.now)

        parking_wait_time = self.config.gate_opening_time - self.env.now
        token.activate(self.env.now, parking_wait_time)
        self.metrics.add_outside_queue_wait_time(car.id, previous_road.id, token.outside_queue_wait_time)

        print(f"[{self.env.now:.2f}] car {car.id} will spend {token.total_travel_time:.2f} on spot {parking_spot.id}")
        yield self.env.timeout(token.total_travel_time)
        self.metrics.add_travel_time(car.id, parking_spot.id, token.total_travel_time)

    # the car moves through roads, towards the check in gates:
    # every car is going to have multiple calls to this function, based on where it was parked and the connections between the roads
    def change_road(self, car, previous_road, next_road):
        token = VehicleToken(car.type, car.type.free_travel_time, self.env.now)
        print(f"[{self.env.now:.2f}] car {car.id} is ready to enter road {next_road.id}")

        yield self.env.process(car.queue_node_transitions(self.env, token, previous_road, next_road))
        print(f"[{self.env.now:.2f}] car {car.id} has left road/spot {previous_road.id} and entered road {next_road.id}")
        self.metrics.acknowledge_count_change(previous_road, self.env.now)
        self.metrics.acknowledge_count_change(next_road, self.env.now)

        #we have now entered the road
        queue_wait_time = self.get_queue_wait_time(car, next_road)
        token.activate(self.env.now, queue_wait_time)
        self.metrics.add_outside_queue_wait_time(car.id, previous_road.id, token.outside_queue_wait_time)

        print(f"[{self.env.now:.2f}] car {car.id} will spend {token.total_travel_time:.2f} on road {next_road.id}")
        yield self.env.timeout(token.total_travel_time)
        self.metrics.add_travel_time(car.id, next_road.id, token.total_travel_time)

    def enter_road(self, car, road):
        token = VehicleToken(car.type, car.type.free_travel_time, self.env.now)
        print(f"[{self.env.now:.2f}] car {car.id} is ready to enter road {road.id}")

        yield self.env.process(car.queue_node_transitions(self.env, token, None, road))
        print(f"[{self.env.now:.2f}] car {car.id} has entered road {road.id}")

        queue_wait_time = self.get_queue_wait_time(car, road)
        token.activate(self.env.now, queue_wait_time)
        self.metrics.add_outside_queue_wait_time(car.id, None, token.outside_queue_wait_time)
        self.metrics.acknowledge_count_change(road, self.env.now)

        print(f"[{self.env.now:.2f}] car {car.id} will spend {token.total_travel_time:.2f} on road {road.id}")
        yield self.env.timeout(token.total_travel_time)
        self.metrics.add_travel_time(car.id, road.id, token.total_travel_time)


    # cars arriving to the final queue/gate/goal:
    # after moving in the parking lot they reach the check-in gates, and then leave the system (get on board)
    def leave_gate(self, car, gate):
        yield self.env.process(car.queue_node_transitions(self.env, None, gate, None))
        self.metrics.acknowledge_count_change(gate, self.env.now)
        print(f"[{self.env.now:.2f}] car {car.id} has left road/gate {gate.id}")
        yield self.env.timeout(0) #leaving the gate is free (since we have already used timeout when we entered the gate)

    def get_queue_wait_time(self, car, road):
        if len(road.store.items) == 0:
            raise ValueError("cannot compute queue wait time on empty road")

        if len(road.store.items) == 1:
            return 0

        nearest_token = None
        #print([t.vehicle_type for t in road.store.items])
        for i in range(len(road.store.items) - 2, 0, -1):
            #print(road.store.items[i].vehicle_type)
            if road.store.items[i].vehicle_type is not None:
                nearest_token = road.store.items[i]
                break
        
        if nearest_token is None:
            return 0

        #nearest_token = road.store.items[-2]
        return nearest_token.time_left(self.env.now)


# what actually happens to a car inside the parkinglot
def car_through_the_pl(env, car, parkinglot):

    # car arrives at the parkinglot
    arrival_time = env.now

    while(not car.has_left()):
        previous_road, next_road = car.advance()

        #leaving gate
        if next_road is None:
            yield env.process(parkinglot.leave_gate(car, previous_road))
            continue

        #entry
        if previous_road is None:
            yield env.process(parkinglot.enter_road(car, next_road))
            continue

        #entering parking spot
        if type(next_road) == ParkingSpot:
            yield env.process(parkinglot.park(car, previous_road, next_road))
            continue

        #moving to a road (base case)
        yield env.process(parkinglot.change_road(car, previous_road, next_road))

    # Car is boarded : "thread" is finished
    wait_times.append(env.now - arrival_time)


def run_parkinglot(env, metrics):

    # I think here the input parameters should be something derived from the graph
    config = Config(env.now, 10)
    parkinglot = ParkingLot(env, metrics, config)
    graph = buildFromJson("input.json")
    graph.link_resources(parkinglot, env)
    for node in graph.nodes:
        metrics.set_initial_values(node, 0)
    car_id = 0
    #car = Vehicle(car_id, VehicleType(1 + car_id % 2, 1), graph, 1, 0, 3)

    car_arrival_stop_time = env.now + 1.2

    # we can use the avg_num_of_cars we expect
    while env.now < car_arrival_stop_time:
        yield env.timeout(0.2)  # Wait a bit before generating a new person / we can do the exp distribution for the arrivals

        car_id += 1

        type_is_car = car_id % 2 == 0
        type_name = "car" if type_is_car else "truck"
        type_size = 1 if type_is_car else 2
        type_time = 1 if type_is_car else 2

        gate_id = 2 if type_is_car else 0
        parking_spot = 3 if car_id % 3 == 0 else None

        car = Vehicle(car_id, VehicleType(type_name, type_time, type_size), graph, 1, gate_id, parking_spot)
        env.process(car_through_the_pl(env, car, parkinglot))


def get_average_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)
    # Pretty print the results
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)

# this is not my code, of course we need to elaborate the graph input
def get_user_input():
    num_roads = input("Input # of roads: ")
    # we will have different gates for trucks and cars
    num_gates = input("Input # of gates: ")
    params = [num_roads, num_gates]
    if all(str(i).isdigit() for i in params):  # Check input is valid
        params = [int(x) for x in params]
    else:
        print(
            "Could not parse input. Simulation will use default values:",
            "\n1 roads, 1 gates.",
        )
        params = [1, 1]
    return params

def input():
  # Read the json file
  # extract the graph and turn it into roads and connections
  # and get the other attributes inserted by the user

  # Budget stuff that will be used at the end of the simulation:
  # wages, ticket prices

  # Capacity stuff:
  # N of parking slots per type
  # N of check-in gates

  # Flow stuff:
  # arrivals are exp
  # departures depend on the roads
  avg_num_of_cars = 90
  avg_num_of_trucks = 5
  avg_num_of_trailers = 10

  perc_online_tickets = 0.60

  # Time stuff:
  # how long is the simulation?
  # opening time-closing time of the check-in gates
  # closing time of the entrace gates
  # 'how long' the roads are (time value)?
  # how long does it take to serve at the check-in gates?

def main():
    # Setup
    random.seed(42)

    # Get inputs from the graph
    #num_roads, num_gates = get_user_input()

    # Run the simulation
    env = simpy.Environment()
    metrics = Metrics(env.now)
    env.process(run_parkinglot(env, metrics))
    # it decides here when to stop the simulation, I think we can either leave this decision to the avg num of cars we expect (so the run_parkinglot())
    # or to the main, speaking in terms of time, meaning for ex when the check-in gates close.
    env.run(until=100)

    metrics.finalize_count_changes(env.now)
    metrics.print_all()

    # View the results
    mins, secs = get_average_wait_time(wait_times)
    print(
        "Running simulation...",
        f"\nThe average wait time is {mins} minutes and {secs} seconds.",
    )

    # Of course we can add all the details we need for our ..*calculations^.^


if __name__ == "__main__":
    main()
