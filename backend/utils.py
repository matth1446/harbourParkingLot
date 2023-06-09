from datetime import datetime, timedelta

import pymongo
import simpy
from pymongo import MongoClient, DESCENDING

import random
from TilesModel import*


class Graph:
    def __init__(self, jsonResult, vehicle_types, connections):
        self.vehiculesTypes = vehicle_types
        self.nodes = [jsonResult[index] for index in jsonResult]
        self.gates = {
            vehicle_type: [
                node for node in self.nodes if type(node) == Gate and vehicle_type in node.type 
            ] for vehicle_type in vehicle_types
        }
        self.parking_spots = {
            vehicle_type: [
                (node, True) for node in self.nodes if type(node) == ParkingSpot and vehicle_type in node.type 
            ] for vehicle_type in vehicle_types
        }
        self.entry_points = {
            vehicle_type: [
                node for node in self.nodes if type(node) == Road and vehicle_type in node.type and node.isEntry
            ] for vehicle_type in vehicle_types
        }
        self.connections = connections
        # paths[a][b] will contain the next node in the path from a to b, and the length of the path (for now, assimilated with capacity)
        self.paths = {t: [[(None, -1) for _n2 in self.nodes] for _n in self.nodes] for t in self.vehiculesTypes}
        self.make_paths()

    def get_valid_parking_spot(self, vehicle_type):
        for i in range(len(self.parking_spots[vehicle_type])):
            spot, spot_available = self.parking_spots[vehicle_type][i]
            if spot_available:
                self.parking_spots[vehicle_type][i] = (spot, False)
                return spot
        return None

    def get_valid_gate(self, vehicle_type):
        index = random.randrange(len(self.gates[vehicle_type]))
        return self.gates[vehicle_type][index]

    def get_all_cars_gates(self):
        return self.gates["car"]

    def get_all_trucks_gates(self):
        return self.gates["truck"]

    def get_valid_entry(self, vehicle_type):
        index = random.randrange(len(self.entry_points[vehicle_type]))
        return self.entry_points[vehicle_type][index]

    def link_resources(self, parking_lot, env):
        for node in self.nodes:
            node.define_store(simpy.Store(env, node.capacity), simpy.Resource(env, capacity=1))

    def make_paths(self):
        # First, we add direct paths
        for type in self.vehiculesTypes:
            for start in range(len(self.connections)):
                for e in self.connections[start]:
                    if type in e[1]:
                        self.paths[type][start][e[0]] = (e[0], self.nodes[start].capacity)
            # then, we build the rest (if we have a->b and b->c, we write paths[a][b] in paths[a][c] if it's interesting)
            changed = True
            while changed:
                changed = False
                for a in range(len(self.nodes)):
                    for b in range(len(self.nodes)):
                        if self.paths[type][a][b][1] != -1:  # path from a to b exists
                            for c in range(len(self.nodes)):
                                if self.paths[type][b][c][1] != -1:  # path from b to c exists
                                    c1 = self.paths[type][a][c][1] == -1
                                    # that would mean the path from a to c doesn't exist yet
                                    c2 = self.paths[type][a][c][1] > self.paths[type][a][b][1] + self.paths[type][b][c][
                                        1]
                                    # that would mean the existing path from a to c is longer than from a to b to c
                                    if c1 or c2:
                                        self.paths[type][a][c] = (
                                            self.paths[type][a][b][0],
                                            self.paths[type][a][b][1] + self.paths[type][b][c][1])
                                        changed = True

    def make_path(self, start, end, v_type="car"):
        if self.paths[v_type][start][end][1] != -1:
            current = start
            res = []
            while current != end:
                res.append(self.nodes[current])
                current = self.paths[v_type][current][end][0]
            res.append(self.nodes[end])
            return res
        else:
            print("Path from {} to {} not found".format(start, end))


def insert_output_into_db(self):
    # Conection to DB
    URI = "mongodb+srv://db_user:db_user@dss.icklgr1.mongodb.net/"
    client = MongoClient(URI)
    print("Connection Successful")
    db = client.database_dss
    # output collection
    collection_input = db.input
    collection_output = db.output

    # Get last entry
    last_entry = collection_input.find_one({}, sort=[('_id', pymongo.DESCENDING)])
    id_inputs = last_entry["_id"]

    # create entry for output
    entry = {"input_id": id_inputs, "outputs":
        {
            "avg_number_vehicles_per_gate": str(self.avg_vehicles_per_gate),

            "total_number_cars": self.total_number_cars,
            "total_number_trucks": self.total_number_trucks,

            "avg_waiting_time_car": self.avg_waiting_time_car,
            "avg_waiting_time_truck": self.avg_waiting_time_truck,

            "list_of_waiting_times_cars": str(self.total_wait_times_cars),
            "list_of_waiting_times_trucks": str(self.total_wait_times_trucks),

            "list_of_n_cars_per_gate_that_did_not_pass": str(self.cars_that_did_not_pass_per_gate),
            "list_of_n_trucks_per_gate_that_did_not_pass": str(self.trucks_that_did_not_pass_per_gate)
        }
    }
    var = collection_output.insert_one(entry).inserted_id
    # Close connection
    client.close()
    print("all the outputs should be online :))))")


def get_last_entry_from_db():
    # Conection to DB
    URI = "mongodb+srv://db_user:db_user@dss.icklgr1.mongodb.net/"
    client = MongoClient(URI)
    print("Connection Successful")
    db = client.database_dss
    # two different collections, one for input and one for output
    collection_input = db.input
    collection_output = db.output

    # Get last entry
    last_entry = collection_input.find_one({}, sort=[('_id', pymongo.DESCENDING)])
    id = last_entry["_id"]
    if collection_output.find_one({"input_id": id}) is not None:
        print('id : ' + str(id))

    # Close connection
    client.close()
    return last_entry['parameters']


class Metrics:
    def __init__(self, initial_time):
        # Get inputs from the graph
        format = '%H:%M'
        dict_inputs = get_last_entry_from_db()
        print(dict_inputs)
        self.gate_open_time = dict_inputs['gate_open_time']
        minutes_to_subtract = 120
        self.entrance_opening_time = datetime.strptime(self.gate_open_time,format)- timedelta(minutes=minutes_to_subtract)
        self.entrance_opening_time = self.entrance_opening_time.strftime("%H:%M")
        print('Entrance opening time : '+str(self.entrance_opening_time))
        elapsed_time = datetime.strptime(self.gate_open_time, format) - datetime.strptime(self.entrance_opening_time,format)
        elapsed_hours = elapsed_time.seconds // 3600
        elapsed_minutes = (elapsed_time.seconds // 60) % 60
        self.checkin_opening_in_minutes = elapsed_hours * 60 + elapsed_minutes
        self.gate_closing_time = dict_inputs['gate_closing_time']
        self.no_of_cars = dict_inputs['no_of_cars']
        self.no_of_trucks = dict_inputs['no_of_trucks']
        self.no_of_trailers = dict_inputs['no_of_trailers']
        self.employee_cost = dict_inputs['employee_cost']
        self.gate_cost = dict_inputs['gate_cost']
        self.ticket_cost = dict_inputs['ticket_cost']
        self.total_area_width = dict_inputs['total_area_width']
        self.total_area_length = dict_inputs['total_area_length']
        self.perc_online_check_in = dict_inputs['perc_online_check_in']

        # things we need during the simulation
        self.number_of_cars_arrived_per_gate = {}
        self.number_of_trucks_arrived_per_gate = {}
        self.cars_that_did_not_pass_per_gate = {}
        self.trucks_that_did_not_pass_per_gate = {}
        self.outside_queue_wait_times_cars = {}
        self.outside_queue_wait_times_trucks = {}
        self.travel_times_cars = {}
        self.travel_times_trucks = {}
        self.total_wait_times_cars = {}
        self.total_wait_times_trucks = {}

        self.road_counts = {}
        self.road_capacities = {}
        self.initial_time = initial_time
        self.zero_intervals = {}
        self.full_intervals = {}

        self.roads = {}
        self.gates = []

        # outputs
        self.total_number_cars = 0.0
        self.total_number_trucks = 0.0
        self.avg_vehicles_per_gate = {}
        self.avg_waiting_time_car = 0.0
        self.avg_waiting_time_truck = 0.0
        pass

    def print_all(self):
        print(f"outside_queue_wait_times_cars = {self.outside_queue_wait_times_cars}")
        print(f"outside_queue_wait_times_trucks = {self.outside_queue_wait_times_trucks}")
        print(f"travel_times_cars = {self.travel_times_cars}")
        print(f"travel_times_trucks = {self.travel_times_trucks}")
        print(f"total_wait_times_cars = {self.total_wait_times_cars}")
        print(f"total_wait_times_trucks = {self.total_wait_times_trucks}")
        print(f"zero_intervals = {self.zero_intervals}")
        print(f"full_intervals = {self.full_intervals}")

        for gate in self.gates:
            self.avg_vehicles_per_gate[gate.id] = gate.population_cars + gate.population_trucks
            print(f"self.avg_vehicles_per_gate[x]: ", self.avg_vehicles_per_gate[gate.id])
            if gate.type.__contains__('car'):
                self.total_number_cars += self.number_of_cars_arrived_per_gate[gate.id]
                print("number of cars that went through gate n° " + str(gate.id) + f" : {gate.population_cars}")
                self.cars_that_did_not_pass_per_gate[gate.id] = self.number_of_cars_arrived_per_gate[gate.id] - gate.population_cars
                print("number of cars that did not go through gate n° " + str(gate.id) + ": " + str(self.cars_that_did_not_pass_per_gate[gate.id]))
            if gate.type.__contains__('truck'):
                self.total_number_trucks += self.number_of_trucks_arrived_per_gate[gate.id]
                print("number of trucks that went through gate n° " + str(gate.id) + f" : {gate.population_trucks}")
                self.trucks_that_did_not_pass_per_gate[gate.id] = self.number_of_trucks_arrived_per_gate[gate.id] - gate.population_trucks
                print("number of trucks that did not go through gate n°: " + str(gate.id) + ": " + str(self.trucks_that_did_not_pass_per_gate[gate.id]))
            #print(gate.type)
        print(f"total_trucks = {self.total_number_trucks}")
        print(f"total cars = {self.total_number_cars}")

        # extracting the avg_waiting_time
        for val in self.total_wait_times_trucks.values():
            self.avg_waiting_time_truck += val
        # using len() to get total keys for mean computation
        avg_waiting_time_truck = self.avg_waiting_time_truck / len(self.total_wait_times_trucks)
        print(f"avg_waiting_time_truck = {self.avg_waiting_time_truck}")
        for val in self.total_wait_times_cars.values():
            self.avg_waiting_time_car += val
        # using len() to get total keys for mean computation
        avg_waiting_time_car = self.avg_waiting_time_car / len(self.total_wait_times_cars)
        print(f"avg_waiting_time_car = {self.avg_waiting_time_car}")

        # dumps everything in the db as the "results" entry
        insert_output_into_db(self)

    def add_time_key_if_unknown(self, vehicle, road_id=None):
        if vehicle.type.name == "car":
            if vehicle.id not in self.outside_queue_wait_times_cars.keys():
                self.outside_queue_wait_times_cars[vehicle.id] = {}

            if road_id is not None and road_id not in self.outside_queue_wait_times_cars[vehicle.id].keys():
                self.outside_queue_wait_times_cars[vehicle.id][road_id] = 0

            if vehicle.id not in self.total_wait_times_cars.keys():
                self.total_wait_times_cars[vehicle.id] = 0

            if vehicle.id not in self.travel_times_cars.keys():
                self.travel_times_cars[vehicle.id] = {}

            if road_id is not None and road_id not in self.travel_times_cars[vehicle.id].keys():
                self.travel_times_cars[vehicle.id][road_id] = 0
        if vehicle.type.name == "truck":
            if vehicle.id not in self.outside_queue_wait_times_trucks.keys():
                self.outside_queue_wait_times_trucks[vehicle.id] = {}

            if road_id is not None and road_id not in self.outside_queue_wait_times_trucks[vehicle.id].keys():
                self.outside_queue_wait_times_trucks[vehicle.id][road_id] = 0

            if vehicle.id not in self.total_wait_times_trucks.keys():
                self.total_wait_times_trucks[vehicle.id] = 0

            if vehicle.id not in self.travel_times_trucks.keys():
                self.travel_times_trucks[vehicle.id] = {}

            if road_id is not None and road_id not in self.travel_times_trucks[vehicle.id].keys():
                self.travel_times_trucks[vehicle.id][road_id] = 0

    def add_outside_queue_wait_time(self, vehicle, road_id, wait_time):
        if road_id is None:
            road_id = "ENTRY"

        self.add_time_key_if_unknown(vehicle, road_id)

        #print("******************************************************* vehicle.type: " + str(vehicle.type.name) + "********************************************************")
        if vehicle.type.name == "car":
            self.total_wait_times_cars[vehicle.id] += wait_time
            self.outside_queue_wait_times_cars[vehicle.id][road_id] += wait_time
        if vehicle.type.name == "truck":
            self.total_wait_times_trucks[vehicle.id] += wait_time
            self.outside_queue_wait_times_trucks[vehicle.id][road_id] += wait_time

    def add_travel_time(self, vehicle, road_id, travel_time):
        self.add_time_key_if_unknown(vehicle, road_id)
        if vehicle.type.name == "car":
            self.travel_times_cars[vehicle.id][road_id] += travel_time
            self.total_wait_times_cars[vehicle.id] += travel_time
        if vehicle.type.name == "truck":
            self.travel_times_trucks[vehicle.id][road_id] += travel_time
            self.total_wait_times_trucks[vehicle.id] += travel_time

    def set_initial_values(self, node, initial_count):
        if type(node) == Gate:
            self.gates.append(node)

        self.roads[node.id] = node
        self.road_counts[node.id] = (
            initial_count,
            self.initial_time if initial_count == 0 else None,
            self.initial_time if initial_count == node.capacity else None
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
