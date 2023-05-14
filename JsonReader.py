from collections import deque
from os.path import exists
import json

class QueueInterface :

    def __init__(self, lengthQueue):
        self.lengthQueue = lengthQueue
        self.queue = deque()

class Gate (QueueInterface):

    def __init__(self, type):
        super().__init__(0)
        self.type = type

class Road (QueueInterface):

    def __init__(self, type, lengthQueue, isEntry, goesTo):
        super().__init__(lengthQueue)
        self.type = type
        self.isEntry = isEntry
        self.goesTo = goesTo

class ParkingSlot (QueueInterface):

    def __init__(self, type, goesTo ):
        super().__init__(0)
        self.type = type
        self.goesTo = goesTo

def validateExtract(dict):
    for obj in dict:
        if type(obj) in [ParkingSlot, Road] :
            for g in obj.goesTo:
                if not (g[0] in dict.keys()):
                    return False
    return True

def buildFromJson(jsonInput):
    content = json.loads(jsonInput)
    res = {}

    for obj in content:
        if obj["type"].lower() == "parking":
            res[obj["id"]] = ParkingSlot(obj["parking-type"],
                                  [(obj["goesTo"][j]["id"], obj["goesTo"][j]["pos"]) for j in range(len(obj["goesTo"]))])
        elif obj["type"].lower() == "road":
            res[obj["id"]] = Road(obj["road-type"], obj["length"], obj["entry"],
                                  [(obj["goesTo"][j]["id"], obj["goesTo"][j]["pos"]) for j in range(len(obj["goesTo"]))])
        elif obj["type"].lower() == "check-in":
            res[obj["id"]] = Gate(obj["checkin-type"])
        else :
            print("unread object : " + str(obj))

    if validateExtract(res):
        return res
    else : return None


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