def size_of_type(type):
    if "truck" in type:
        return 2
    elif "car" in type:
        return 1
    else:
        raise ValueError(f"unknown type {type}")

def speed_of_type(type):
    if "truck" in type:
        return 10
    elif "car" in type:
        return 30
    else:
        raise ValueError(f"unknown type {type}")



class QueueInterface:
    i = 0

    def __init__(self, lengthQueue):
        self.id = QueueInterface.i
        QueueInterface.i += 1
        self.store = None
        self.queue_lock = None
        self.capacity = lengthQueue
        # self.queue = deque()

    def define_store(self, store, queue_lock):
        self.store = store
        self.queue_lock = queue_lock

    def __str__(self):
        return f"[{self.id} ({self.capacity})]"

    def __repr__(self):
        return self.__str__()


class Gate(QueueInterface):

    def __init__(self, type):
        super().__init__(size_of_type(type))
        self.type = type
        self.population_cars = 0.0
        self.population_trucks = 0.0

    def __str__(self):
        return super().__str__() + " (Gate)"


class Road(QueueInterface):

    def __init__(self, type, lengthQueue, isEntry, connectsTo):
        super().__init__(lengthQueue)
        self.type = type
        self.isEntry = isEntry
        self.goesTo = connectsTo

    def __str__(self):
        return super().__str__() + " (Road)"


class ParkingSpot(QueueInterface):

    def __init__(self, type, connectsTo, cap):
        super().__init__(cap)
        self.type = type
        self.goesTo = connectsTo

    def __str__(self):
        return super().__str__() + " (ParkingSpot)"