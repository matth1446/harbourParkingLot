import simpy
from JsonReader import *


class Graph:
    def __init__(self, jsonFile):
        r = open(jsonFile,"r").read()
        jsonResult = buildFromJson(r)
        self.nodes = [jsonResult[index] for index in jsonResult]
        self.connections = buildConnections(jsonResult)

    def link_resources(self, parking_lot, env):
        for node in self.nodes:
            node.define_store(simpy.Store(env, node.capacity))

    def make_path(self, start, end): #TODO
        if start == 0:
            return [self.nodes[0], self.nodes[2], self.nodes[3]]
        else:
            return [self.nodes[0], self.nodes[2], self.nodes[1], self.nodes[2], self.nodes[3]]


class Metrics:
    def __init__(self, initial_time):
        self.outside_queue_wait_times = {}
        self.travel_times = {}
        self.total_wait_times = {}

        self.road_counts = {}
        self.road_capacities = {}
        self.initial_time = initial_time
        self.zero_intervals = {}
        self.full_intervals = {}

        self.roads = {}
        pass

    def print_all(self):
        print(f"outside_queue_wait_times = {self.outside_queue_wait_times}")
        print(f"travel_times = {self.travel_times}")
        print(f"total_wait_times = {self.total_wait_times}")
        print(f"zero_intervals = {self.zero_intervals}")
        print(f"full_intervals = {self.full_intervals}")

    def add_time_key_if_unknown(self, car_id, road_id=None):
        if car_id not in self.outside_queue_wait_times.keys():
            self.outside_queue_wait_times[car_id] = {}

        if road_id is not None and road_id not in self.outside_queue_wait_times[car_id].keys():
            self.outside_queue_wait_times[car_id][road_id] = 0

        if car_id not in self.total_wait_times.keys():
            self.total_wait_times[car_id] = 0

        if car_id not in self.travel_times.keys():
            self.travel_times[car_id] = {}

        if road_id is not None and road_id not in self.travel_times[car_id].keys():
            self.travel_times[car_id][road_id] = 0

    def add_outside_queue_wait_time(self, car_id, road_id, wait_time):
        if road_id is None:
            road_id = "ENTRY"

        self.add_time_key_if_unknown(car_id, road_id)

        self.outside_queue_wait_times[car_id][road_id] += wait_time
        self.total_wait_times[car_id] += wait_time

    def add_travel_time(self, car_id, road_id, travel_time):
        self.add_time_key_if_unknown(car_id, road_id)

        self.travel_times[car_id][road_id] += travel_time
        self.total_wait_times[car_id] += travel_time

    def set_initial_values(self, road, initial_count):
        self.roads[road.id] = road
        self.road_counts[road.id] = (
            initial_count,
            self.initial_time if initial_count == 0 else None,
            self.initial_time if initial_count == road.capacity else None
        )

    def add_zero_interval(self, road_id, zero_time):
        if road_id not in self.zero_intervals.keys():
            self.zero_intervals[road_id] = []
        if zero_time != 0:
            self.zero_intervals[road_id].append(zero_time)

    def add_full_interval(self, road_id, full_time):
        if road_id not in self.full_intervals.keys():
            self.full_intervals[road_id] = []
        if full_time != 0:
            self.full_intervals[road_id].append(full_time)

    def acknowledge_count_change(self, road, current_time):
        previous_count, last_zero, last_full = self.road_counts[road.id]
        new_count = len(road.store.items)
        # print(f"ack road {road.id} from {previous_count}, {last_zero}, {last_full} to {new_count} at {current_time}")

        if previous_count == 0 and new_count != 0:
            self.add_zero_interval(road.id, current_time - last_zero)
            last_zero = None
        elif previous_count != 0 and new_count == 0:
            last_zero = current_time

        capacity = road.capacity
        if previous_count == capacity and new_count != capacity:
            self.add_full_interval(road.id, current_time - last_full)
            last_full = None
        elif previous_count != capacity and new_count == capacity:
            last_full = current_time

        self.road_counts[road.id] = new_count, last_zero, last_full

    def finalize_count_changes(self, current_time):
        for road_id in self.roads.keys():
            previous_count, last_zero, last_full = self.road_counts[road_id]
            if previous_count == self.roads[road_id].capacity:
                self.add_full_interval(road_id, current_time - last_full)

            if previous_count == 0:
                self.add_zero_interval(road_id, current_time - last_zero)