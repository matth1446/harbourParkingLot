import simpy


def size_of_type(type):
    if "truck" in type:
        return 2
    else:
        return 1

class QueueInterface :

    i = 0;

    def __init__(self, lengthQueue):
        self.id = QueueInterface.i
        QueueInterface.i += 1
        self.store = None
        self.queue_lock = None
        self.capacity = lengthQueue
        #self.queue = deque()

    def define_store(self, store, queue_lock):
        self.store = store
        self.queue_lock = queue_lock

    def __str__(self):
        return f"[{self.id} ({self.capacity})]"

    def __repr__(self):
        return self.__str__()

class Gate (QueueInterface):

    def __init__(self, type):
        super().__init__(size_of_type(type))
        self.type = type
        self.population = 0.0

    def __str__(self):
        return super().__str__() + " (Gate)"

class Road (QueueInterface):

    def __init__(self, type, lengthQueue, isEntry, connectsTo):
        super().__init__(lengthQueue)
        self.type = type
        self.isEntry = isEntry
        self.goesTo = connectsTo

    def __str__(self):
        return super().__str__() + " (Road)"

class ParkingSpot (QueueInterface):

    def __init__(self, type, connectsTo, cap):
        super().__init__(cap)
        self.type = type
        self.goesTo = connectsTo

    def __str__(self):
        return super().__str__() + " (ParkingSpot)"


class Graph:
    def __init__(self, jsonResult, vehicle_types, connections):
        self.vehiculesTypes = vehicle_types
        self.nodes = [jsonResult[index] for index in jsonResult]
        self.connections = connections
        # paths[a][b] will contain the next node in the path from a to b, and the length of the path (for now, assimilated with capacity)
        self.paths = {t:[[(None,-1)for _n2 in self.nodes] for _n in self.nodes]for t in self.vehiculesTypes}
        self.make_paths()

    def link_resources(self, parking_lot, env):
        for node in self.nodes:
            node.define_store(simpy.Store(env, node.capacity), simpy.Resource(env, capacity=1))

    def make_paths(self):
        #First, we add direct paths
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
                                    c2 = self.paths[type][a][c][1] > self.paths[type][a][b][1] + self.paths[type][b][c][1]
                                    # that would mean the existing path from a to c is longer than from a to b to c
                                    if c1 or c2:
                                        self.paths[type][a][c] = (
                                            self.paths[type][a][b][0], self.paths[type][a][b][1] + self.paths[type][b][c][1])
                                        changed = True



    def make_path(self, start, end, v_type = "car"):
        if self.paths[v_type][start][end][1] != -1:
            current = start
            res = []
            while current != end:
                res.append(self.nodes[current])
                current = self.paths[v_type][current][end][0]
            res.append(self.nodes[end])
            return res
        else : print("Path from {} to {} not found".format(start, end))


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
        self.gates = {}
        pass

    def print_all(self):
        print(f"outside_queue_wait_times = {self.outside_queue_wait_times}")
        print(f"travel_times = {self.travel_times}")
        print(f"total_wait_times = {self.total_wait_times}")
        print(f"zero_intervals = {self.zero_intervals}")
        print(f"full_intervals = {self.full_intervals}")

        for gate in self.gates:
            print("number of vehicules that went through gate n°" + gate.id+f" : {gate.population}")

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

    def set_initial_values(self, node, initial_count):
        if(type(node)=="Road"):
            self.roads[node.id] = node
            self.road_counts[node.id] = (
                initial_count,
                self.initial_time if initial_count == 0 else None,
                self.initial_time if initial_count == road.capacity else None
            )
        if(type(node)=="Gate"):
            self.gates[node.id] = node


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