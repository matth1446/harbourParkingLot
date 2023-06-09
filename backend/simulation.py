# -*- coding: utf-8 -*-
"""Copia di simulation_of_a_parkinglot.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BCB-H3Bz0cM0ZHoMrI4z2j_JJHvUf1Q6
"""

# pip install simpy
import time
from datetime import datetime

"""Companion code to https://realpython.com/simulation-with-simpy/

'Simulating Real-World Processes With SimPy'

Python version: 3.7.3
SimPy version: 3.0.11
"""

import simpy
import random
import statistics
from functools import reduce
from backend.utils import *
from backend.JsonReader import *
import numpy as np
import pymongo
from pymongo import MongoClient

# Global variables.
wait_times = []


# I didn't choose any of the time-inputs, so don't look at me

class VehicleType:
    def __init__(self, type_name, max_speed, size):
        self.max_speed = max_speed
        self.size = size
        self.name = type_name


def compare_floats(val1, val2, *, delta=0.00001, lte=False, gte=False):
    if gte and lte:
        raise ValueError("invalid comparison")

    if lte is True:
        return val1 < val2 + delta

    if gte is True:
        return val1 > val2 - delta

    return - delta < (val1 - val2) and (val1 - val2) < delta


class VehicleToken:
    def __init__(self, vehicle_id=None, vehicle_type=None, creation_time=None):
        self.total_wait_time = None
        self.outside_queue_wait_time = None
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.creation_time = creation_time

        self.trajectory = None

        self.total_travel_time = None
        self.activation_time = None

    def __str__(self):
        return f'[{self.vehicle_id} {self.is_true()}]' + (
            " {" + f'{self.activation_time}:{self.trajectory}:{self.total_travel_time}' + "} " if self.activation_time is not None else '')

    def __repr__(self):
        return self.__str__()

    def adjust_for_size(self):
        print(self.trajectory)
        return [(t, v, x - self.vehicle_type.size, t2) for (t, v, x, t2) in self.trajectory]

    def intersect(self, trajectory_segment_1, trajectory_segment_2):
        time_1, speed_1, pos_1, _ = trajectory_segment_1
        time_2, speed_2, pos_2, end_time_2 = trajectory_segment_2

        # if not compare_floats(time_1, time_2, gte=True):
        #    raise ValueError("trajectory segments must be ordered by start time for intersection")

        if not compare_floats(time_1, end_time_2, lte=True):
            raise ValueError("trajectory segments must have overlapping times for intersection")

        if not compare_floats(pos_1, pos_2 + speed_2 * (time_1 - time_2), lte=True):
            raise ValueError("trajectory segments must be ordered by position for intersection")

        end_pos_1 = pos_1 + speed_1 * (end_time_2 - time_1)
        end_pos_2 = pos_2 + speed_2 * (end_time_2 - time_2)

        if not compare_floats(end_pos_1, end_pos_2, gte=True):
            return (False, end_pos_1, (end_time_2, speed_1, end_pos_1, end_time_2))

        if compare_floats(end_pos_1, end_pos_2):
            return (False, end_pos_1, (end_time_2, speed_2, end_pos_1, end_time_2))

        if compare_floats(speed_1, speed_2):
            raise ValueError("segments were of same speed yet an intersection was discovered")

        intersect_time = (pos_2 - pos_1 + time_1 * speed_1 - time_2 * speed_2) / (speed_1 - speed_2)
        intersect_pos = pos_1 + speed_1 * (intersect_time - time_1)

        return True, end_pos_2, (intersect_time, speed_2, intersect_pos, end_time_2)

    def find_activation_time(self, followed_trajectory):
        move_start_index = None
        for i in range(len(followed_trajectory)):
            curr_follow_time, curr_follow_speed, _, _ = followed_trajectory[i]
            if compare_floats(curr_follow_time, self.activation_time, gte=True):
                move_start_index = i - 1
                break

        if move_start_index == -1:
            return 0  # raise ValueError(f"the followed trajectory starts after the activation time ({self.vehicle_id})")

        if move_start_index is None and not compare_floats(followed_trajectory[-1][3], self.activation_time, gte=True):
            return None  # raise ValueError("the followed trajectory ends before the activation time")
        elif move_start_index is None:
            move_start_index = len(followed_trajectory) - 1

        return move_start_index

    @staticmethod
    def find_zero_time(followed_trajectory, start_index):
        zero_index = None
        for i in range(start_index, len(followed_trajectory)):
            curr_follow_time, curr_follow_speed, cur_follow_pos, _ = followed_trajectory[i]
            if compare_floats(cur_follow_pos, 0, gte=True):
                zero_index = i - 1
                break

        if zero_index is None:
            zero_index = len(followed_trajectory) - 1

        if zero_index < start_index:
            raise ValueError("the followed trajectory reaches 0 before the given start index")

        prev_follow_time, prev_follow_speed, prev_follow_pos, prev_end_time = followed_trajectory[zero_index]
        follow_zero_time = prev_follow_time - prev_follow_pos / prev_follow_speed

        if not compare_floats(follow_zero_time, prev_end_time, lte=True):
            raise ValueError("the followed trajectory never reaches 0 before the activation time")

        return zero_index, follow_zero_time

    def follow_trajectory(self, followed_trajectory, road_size):

        # Format: [time_start, speed, position, time_end]
        # 1 find activation time in the followed trajectory
        # 2 if followed position < 0 at activation time: add [activation, 0, 0, time_end]
        # 3 set move_start = activation or time_end accordingly
        # 4 set curr_vel = speed if we are in the same position, else max_speed
        # 5 loop over trajectory points (starting at time_end) and calcutate the intersection
        # 6 for each point:
        # 7   calcutate end point of vehicle if we were always at curr_vel
        # 8   if we caught up (intersection) then add a point at the intersection, set curr_vel = catch up speed and add the followed point as well
        # 9   otherwise set a point anyway but dont change curr_vel
        # 10at the end point, we add a final point using curr_vel

        result_trajectory = []
        curr_time = self.activation_time
        curr_speed = self.vehicle_type.max_speed
        curr_pos = 0

        # 1
        move_start_index = self.find_activation_time(followed_trajectory)
        if move_start_index is None:
            return None

        # 2
        prev_follow_time, prev_follow_speed, prev_follow_pos, prev_end_time = followed_trajectory[move_start_index]
        follow_pos_at_activation = prev_follow_pos + (self.activation_time - prev_follow_time) * prev_follow_speed

        print(
            f' > {self} identified activation time between {move_start_index} and {move_start_index + 1}, followed segment = {followed_trajectory[move_start_index]}, followed position = {follow_pos_at_activation}')

        if not compare_floats(follow_pos_at_activation, 0, gte=True):
            zero_index, follow_zero_time = self.find_zero_time(followed_trajectory, move_start_index)
            result_trajectory.append((self.activation_time, 0, 0, follow_zero_time))
            curr_time = follow_zero_time
            move_start_index = zero_index
            print(f' > {self} added waiting segment from {self.activation_time} to {follow_zero_time}')

        # 5

        curr_index = move_start_index
        while curr_index < len(followed_trajectory):
            curr_follow_segment = followed_trajectory[curr_index]
            curr_segment = (curr_time, self.vehicle_type.max_speed, curr_pos, None)
            print(
                f' > {self} current segment: {curr_segment}, current follow index: {curr_index}, current follow segment: {curr_follow_segment}')

            caught_up, end_pos, new_segment = self.intersect(curr_segment, curr_follow_segment)

            print(f' > {self} intersection result: {caught_up}, {end_pos}, new segment: {new_segment}')
            if not compare_floats(curr_time, new_segment[0]):
                base_segment = (curr_time, curr_speed, curr_pos, new_segment[0])
                result_trajectory.append(base_segment)
                print(f' > {self} added base segment: {base_segment}')

            if caught_up:
                result_trajectory.append(new_segment)
                print(f' > {self} added slowed segment: {new_segment}')

            curr_time = new_segment[3]
            curr_pos = end_pos
            curr_speed = new_segment[1]
            curr_index += 1

            if curr_pos > road_size:
                raise ValueError("the segment went beyond the road size")

        # 10

        final_time = curr_time + (road_size - curr_pos) / curr_speed
        final_segment = (curr_time, curr_speed, curr_pos, final_time)
        result_trajectory.append(final_segment)
        print(f' > {self} added final segment: {final_segment}')

        return result_trajectory

    def default_trajectory(self, road_size):
        self.total_travel_time = road_size / self.vehicle_type.max_speed
        self.trajectory = [
            (self.activation_time, self.vehicle_type.max_speed, 0, self.total_travel_time + self.activation_time)]

    def follow_token(self, followed_token, road_size):
        followed_trajectory = followed_token.adjust_for_size()
        trajectory = self.follow_trajectory(followed_trajectory, road_size)

        if trajectory is None:
            self.default_trajectory(road_size)
            return

        self.trajectory = trajectory
        self.total_travel_time = self.trajectory[-1][3] - self.activation_time

    def activate(self, activation_time, *, wait_time=None, road_size=None, follow=None):
        self.activation_time = activation_time

        if road_size is None and wait_time is None:
            raise ValueError("cannot activate token without a road size or a given wait time")

        if road_size is not None and wait_time is not None:
            raise ValueError("cannot activate token with both a road size and a given wait time")

        if wait_time is not None:
            self.trajectory = [(self.activation_time, 0, 0, wait_time + self.activation_time)]
            self.total_travel_time = wait_time
        elif follow is None:
            self.default_trajectory(road_size)
        else:
            self.follow_token(follow, road_size)

        self.outside_queue_wait_time = self.activation_time - self.creation_time
        self.total_wait_time = self.outside_queue_wait_time + self.total_travel_time

        print(f'[{activation_time:.2f}] token activated : {self}')
        return self

    def is_true(self):
        return self.vehicle_type is not None

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
            self.path = graph.make_path(start, parking_step, self.type.name)[:-1] + graph.make_path(parking_step, end,
                                                                                                    self.type.name)
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
            # print(f'#[{env.now:.2f}] car {self.id} has got the lock for node {next_node.id}')
            yield env.process(self.perform_node_transfers(env, true_token, previous_node, next_node))

        # print(f'#[{env.now:.2f}] car {self.id} has released the lock for node {next_node.id}')

    def perform_node_transfers(self, env, true_token=None, previous_node=None, next_node=None):
        yield env.process(self.perform_node_transfer(env, previous_node, next_node, true_token))

        for i in range(self.type.size - 1):
            yield env.process(self.perform_node_transfer(env, previous_node, next_node, VehicleToken(self.id)))

    def perform_node_transfer(self, env, previous_node=None, next_node=None, token=None):
        def token_str(t):
            return 'true' if t.is_true() else 'dummy'

        if next_node is not None:
            yield next_node.store.put(token)
            # print(f"#[{env.now:.2f}] car {self.id} has placed a {token_str(token)} token in node {next_node.id}")

        if previous_node is not None:
            get_request = yield previous_node.store.get()
            # print(f"#[{env.now:.2f}] car {self.id} has removed a {token_str(get_request)} token in node {previous_node.id}")


class Config:
    def __init__(self, initial_time, gate_opening_time, checkin_opening_in_minutes, gate_service_time):
        self.initial_time = initial_time
        self.gate_opening_time = gate_opening_time
        self.checkin_opening_in_minutes = checkin_opening_in_minutes
        self.gate_service_time = gate_service_time


class ParkingLot(object):

    def __init__(self, env, metrics, config):
        self.env = env
        self.metrics = metrics
        self.config = config

    # what can the cars do

    # once the car comes in the entrance gate, the goal is to park it:
    # find a parking slot available (we should think of the type of vehicle/parking space)
    def park(self, car, previous_road, parking_spot):
        token = VehicleToken(car.id, car.type,
                             self.env.now)  # vehicles do not take any time "travelling" through parking spots
        print(f"[{self.env.now:.2f}] car {car.id} is ready to park at spot {parking_spot.id}")

        yield self.env.process(car.queue_node_transitions(self.env, token, previous_road, parking_spot))
        print(
            f"[{self.env.now:.2f}] car {car.id} has left road {previous_road.id} and parked at spot {parking_spot.id}")
        self.metrics.acknowledge_count_change(previous_road, self.env.now)
        self.metrics.acknowledge_count_change(parking_spot, self.env.now)

        parking_wait_time = self.config.checkin_opening_in_minutes - self.env.now
        parking_wait_time = 0 if parking_wait_time < 0 else parking_wait_time
        token.activate(self.env.now, wait_time=parking_wait_time)
        self.metrics.add_outside_queue_wait_time(car, previous_road.id, token.outside_queue_wait_time)

        print(f"[{self.env.now:.2f}] car {car.id} will spend {token.total_travel_time:.2f} on spot {parking_spot.id}")
        yield self.env.timeout(token.total_travel_time)
        self.metrics.add_travel_time(car, parking_spot.id, token.total_travel_time)

    # the car moves through roads, towards the check in gates:
    # every car is going to have multiple calls to this function, based on where it was parked and the connections between the roads
    def change_road(self, car, previous_road, next_road):
        token = VehicleToken(car.id, car.type, self.env.now)
        print(f"[{self.env.now:.2f}] car {car.id} is ready to enter road {next_road.id}")

        yield self.env.process(car.queue_node_transitions(self.env, token, previous_road, next_road))
        print(
            f"[{self.env.now:.2f}] car {car.id} has left road/spot {previous_road.id} and entered road {next_road.id}")
        self.metrics.acknowledge_count_change(previous_road, self.env.now)
        self.metrics.acknowledge_count_change(next_road, self.env.now)

        # we have now entered the road
        token.activate(self.env.now, follow=self.get_follow_token(next_road), road_size=next_road.capacity)
        self.metrics.add_outside_queue_wait_time(car, previous_road.id, token.outside_queue_wait_time)

        print(f"[{self.env.now:.2f}] car {car.id} will spend {token.total_travel_time:.2f} on road {next_road.id}")
        yield self.env.timeout(token.total_travel_time)
        self.metrics.add_travel_time(car, next_road.id, token.total_travel_time)

    def enter_road(self, vehicle, road):
        token = VehicleToken(vehicle.id, vehicle.type, self.env.now)
        print(f"[{self.env.now:.2f}] car {vehicle.id} is ready to enter road {road.id}")

        yield self.env.process(vehicle.queue_node_transitions(self.env, token, None, road))
        print(f"[{self.env.now:.2f}] car {vehicle.id} has entered road {road.id}")

        token.activate(self.env.now, follow=self.get_follow_token(road), road_size=road.capacity)

        self.metrics.add_outside_queue_wait_time(vehicle, None, token.outside_queue_wait_time)
        self.metrics.acknowledge_count_change(road, self.env.now)
        print(f"[{self.env.now:.2f}] car {vehicle.id} will spend {token.total_travel_time:.2f} on road {road.id}")
        yield self.env.timeout(token.total_travel_time)
        self.metrics.add_travel_time(vehicle, road.id, token.total_travel_time)

    # cars arriving to the final queue/gate/goal:
    # after moving in the parking lot they reach the check-in gates, and then leave the system (get on board)
    def leave_gate(self, vehicle, gate):
        yield self.env.process(vehicle.queue_node_transitions(self.env, None, gate, None))
        # increasing the number of vehicles that went through a gate
        self.metrics.acknowledge_count_change(gate, self.env.now)
        print(f"[{self.env.now:.2f}] vehicle {vehicle.id} has left gate {gate.id}")
        if vehicle.type.name == 'car':
            gate.population_cars += 1.0
        elif vehicle.type.name == 'truck':
            gate.population_trucks += 1.0
        yield self.env.timeout(
            0)  # leaving the gate is free (since we have already used timeout when we entered the gate)

    def enter_gate(self, car, previous_road, gate):
        token = VehicleToken(car.id, car.type,
                             self.env.now)  # vehicles do not take any time "travelling" through parking spots
        print(f"[{self.env.now:.2f}] car {car.id} is ready to enter gate {gate.id}")

        yield self.env.process(car.queue_node_transitions(self.env, token, previous_road, gate))
        print(
            f"[{self.env.now:.2f}] car {car.id} has left road {previous_road.id} and entered gate {gate.id}")
        self.metrics.acknowledge_count_change(previous_road, self.env.now)
        self.metrics.acknowledge_count_change(gate, self.env.now)

        gate_wait_time = self.config.gate_service_time
        # parking_wait_time = 0 if parking_wait_time < 0 else parking_wait_time
        token.activate(self.env.now, wait_time=gate_wait_time)
        self.metrics.add_outside_queue_wait_time(car, previous_road.id, token.outside_queue_wait_time)

        print(f"[{self.env.now:.2f}] car {car.id} will spend {token.total_travel_time:.2f} in gate {gate.id}")
        yield self.env.timeout(token.total_travel_time)
        self.metrics.add_travel_time(car, gate.id, token.total_travel_time)

    def get_follow_token(self, road):
        if len(road.store.items) == 0:
            raise ValueError("cannot compute follow token on empty road")

        print(road.store.items)

        last_vehicle_passed = False
        for i in range(len(road.store.items) - 1, -1, -1):
            # print(road.store.items[i], last_vehicle_passed)
            found_vehicle_head = road.store.items[i].is_true()
            if found_vehicle_head and last_vehicle_passed:
                print(f'FOLLOWING {road.store.items[i]}')
                return road.store.items[i]

            last_vehicle_passed = last_vehicle_passed or found_vehicle_head

        # print(None)
        return None


# what actually happens to a car inside the parkinglot
def car_through_the_pl(env, car, parkinglot):
    # car arrives at the parkinglot
    arrival_time = env.now

    while (not car.has_left()):
        previous_road, next_road = car.advance()

        # leaving gate
        if next_road is None:
            yield env.process(parkinglot.leave_gate(car, previous_road))
            continue

        # entry
        if previous_road is None:
            yield env.process(parkinglot.enter_road(car, next_road))
            continue

        # entering parking spot
        if type(next_road) == ParkingSpot:
            yield env.process(parkinglot.park(car, previous_road, next_road))
            continue

        if type(next_road) == Gate:
            yield env.process(parkinglot.enter_gate(car, previous_road, next_road))
            continue

        # moving to a road (base case)
        yield env.process(parkinglot.change_road(car, previous_road, next_road))

    # Car is boarded : "thread" is finished
    wait_times.append(env.now - arrival_time)


def run_parkinglot(env, metrics):
    # I think here the input parameters should be something derived from the graph
    config = Config(env.now, metrics.gate_closing_time, metrics.checkin_opening_in_minutes, 1)
    parkinglot = ParkingLot(env, metrics, config)
    graph = buildFromDb()
    graph.link_resources(parkinglot, env)
    for node in graph.nodes:
        metrics.set_initial_values(node, 0)
    car_id = 0
    # truck_id
    # car = Vehicle(car_id, VehicleType(1 + car_id % 2, 1), graph, 1, 0, 3)

    # Computing of the simulation duration
    format = '%H:%M'
    opening = datetime.strptime(metrics.entrance_opening_time, format)
    closing = datetime.strptime(metrics.gate_closing_time, format)

    elapsed_time = closing - opening

    # Ottieni il tempo trascorso in ore e minuti
    elapsed_hours = elapsed_time.seconds // 3600
    elapsed_minutes = (elapsed_time.seconds // 60) % 60

    total_elapsed_minutes = elapsed_minutes + elapsed_hours * 60

    # Stampa il tempo trascorso
    sim_duration = total_elapsed_minutes
    car_arrival_stop_time = env.now + sim_duration
    print('car_arrival_stop_time = ' + str(car_arrival_stop_time))

    expected_num_of_cars = metrics.no_of_cars
    expected_num_of_trucks = metrics.no_of_trucks

    for g in graph.get_all_cars_gates():
        metrics.number_of_cars_arrived_per_gate[g.id] = 0.0
    for g in graph.get_all_trucks_gates():
        metrics.number_of_trucks_arrived_per_gate[g.id] = 0.0

    p_car = expected_num_of_cars / (expected_num_of_trucks + expected_num_of_cars)
    p_truck = 1 - p_car
    min_arrival = 0.0
    mean_interarrival_time = (expected_num_of_cars+expected_num_of_trucks)/total_elapsed_minutes
    print('mean_arrival_time : '+str(mean_interarrival_time))

    # we can use the avg_num_of_cars we expect
    while env.now < car_arrival_stop_time:
        vehicle_type = np.random.choice(['car', 'truck'], p=[p_car, p_truck])
        print(f"New vehicle: " + vehicle_type)
        arrival_time = max(0, np.random.exponential(1/mean_interarrival_time))
        yield env.timeout(arrival_time)  # Wait a bit before generating a new person / we can do the exp distribution for the arrivals

        car_id += 1
        type_name = vehicle_type
        type_size = size_of_type([vehicle_type])
        type_speed = speed_of_type([vehicle_type])

        parking_spot_id = None
        if env.now < config.checkin_opening_in_minutes:
            parking_spot = graph.get_valid_parking_spot(type_name)
            parking_spot_id = parking_spot.id if parking_spot is not None else None

        gate_id = graph.get_valid_gate(type_name).id
        print('gate_id = ')
        print(gate_id)
        entry_id = graph.get_valid_entry(type_name).id
        if vehicle_type == 'car':
            metrics.number_of_cars_arrived_per_gate[gate_id] += 1
        else:
            metrics.number_of_trucks_arrived_per_gate[gate_id] += 1

        vehicle = Vehicle(car_id, VehicleType(type_name, type_speed, type_size), graph, entry_id, gate_id,
                          parking_spot_id)
        env.process(car_through_the_pl(env, vehicle, parkinglot))
    print('FINAL env.now = ' + str(env.now))


def main():
    # Setup
    random.seed(42)

    # num_roads, num_gates = get_user_input()

    # Run the simulation
    env = simpy.Environment()
    metrics = Metrics(env.now)
    #print(metrics.gates)
    env.process(run_parkinglot(env, metrics))
    # it decides here when to stop the simulation, I think we can either leave this decision to the avg num of cars we expect (so the run_parkinglot())
    # or to the main, speaking in terms of time, meaning for ex when the check-in gates close.
    # Computing of the simulation duration
    format = '%H:%M'
    opening = datetime.strptime(metrics.entrance_opening_time, format)
    closing = datetime.strptime(metrics.gate_closing_time, format)

    elapsed_time = closing - opening

    # Ottieni il tempo trascorso in ore e minuti
    elapsed_hours = elapsed_time.seconds // 3600
    elapsed_minutes = (elapsed_time.seconds // 60) % 60

    total_elapsed_minutes = elapsed_minutes + elapsed_hours * 60

    stop_time = total_elapsed_minutes
    print('STOP TIME : ' + str(stop_time))
    env.run(until=stop_time)
    print('MAIN env.now = ' + str(env.now))
    metrics.finalize_count_changes(env.now)
    # this is the output
    metrics.print_all()

    # View the results
    # mins, secs = get_average_wait_time(wait_times)
    # print(
    #    "Running simulation...",
    #    f"\nThe average wait time is {mins} minutes and {secs} seconds.",
    # )

    # Of course we can add all the details we need for our ..*calculations^.^


if __name__ == "__main__":
    main()
