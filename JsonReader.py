from collections import deque
from os.path import exists
import json

class QueueInterface :

    i = 0;

    def __init__(self, lengthQueue):
        self.id = QueueInterface.i
        QueueInterface.i += 1
        self.store = None
        self.capacity = lengthQueue
        self.queue = deque()

    def define_store(self, store):
        self.store = store

class Gate (QueueInterface):

    def __init__(self, type):
        super().__init__(1)
        self.type = type

class Road (QueueInterface):

    def __init__(self, type, lengthQueue, isEntry, connectsTo):
        super().__init__(lengthQueue)
        self.type = type
        self.isEntry = isEntry
        self.goesTo = connectsTo

class ParkingSpot (QueueInterface):

    def __init__(self, type, connectsTo, cap):
        super().__init__(cap)
        self.type = type
        self.goesTo = connectsTo

def validateExtract(dict):
    for obj in dict:
        if type(obj) in [ParkingSpot, Road] :
            for g in obj.goesTo:
                if not (g[0] in dict.keys()):
                    return False
    return True

def buildFromJson(jsonInput):
    content = json.loads(jsonInput)
    res = {}

    for obj in content:
        if obj["type"].lower() == "parking":
            res[obj["id"]] = ParkingSpot(obj["type-allowed"],
                                  [(obj["connectsTo"][j]["id"], obj["connectsTo"][j]["pos"]) for j in range(len(obj["connectsTo"]))],
                                         obj["capacity"])
        elif obj["type"].lower() == "road":
            res[obj["id"]] = Road(obj["type-allowed"], obj["capacity"], obj["entry"],
                                  [(obj["connectsTo"][j]["id"], obj["connectsTo"][j]["pos"]) for j in range(len(obj["connectsTo"]))])
        elif obj["type"].lower() == "check-in":
            res[obj["id"]] = Gate(obj["type-allowed"])
        else :
            print("unread object : " + str(obj))

    if validateExtract(res):
        return res
    else : return None

def getVehiculesType(jsonInput):
    content = json.loads(jsonInput)
    res = set()
    for it in range(len(content)):
        res = res.union(set(content[it]["type-allowed"]))
    return res

def buildConnections(graph):
    res = [[] for _i in range(len(graph))]
    for index in graph:
        if type(graph[index]) != Gate:
            res[index] = [(id_node,graph[id_node].type) for (id_node,p) in graph[index].goesTo]
    return res

if __name__ == "__main__" :
    got = ""
    if exists("./input.json"):
        f = open("./input.json","r")
        got = f.read()
    else:
        nbLine = int(input("How many lines do you want to enter?"))

        got = ""
        for i in range(nbLine):
            got += input("next line : ")

    print(buildFromJson(got))