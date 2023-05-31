#from collections import deque
from os.path import exists
import json
from TilesModel import Gate, Road, ParkingSpot
from utils import Graph
from pymongo import MongoClient, DESCENDING

def validateExtract(dict):
    for obj in dict:
        if type(obj) in [ParkingSpot, Road] :
            for g in obj.goesTo:
                if not (g[0] in dict.keys()):
                    return False
    return True

def buildFromJson(jsonInput):
    r = open(jsonInput,"r").read()
    content = json.loads(r)
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
        return Graph(res, getVehiculesType(r), buildConnections(res))
    else : return None

def buildFromTable(input):
    res = {}
    vehicle = set()
    for obj in input:
        if obj["type"].lower() == "parking":
            res[obj["id"]] = ParkingSpot(obj["allowed_veh"],
                                  [(obj["connectsTo"][j]["id"], obj["connectsTo"][j]["pos"]) for j in range(len(obj["connectsTo"]))],
                                         obj["capacity"])
            vehicle = vehicle.union(set(obj["allowed_veh"]))
        elif obj["type"].lower() == "road":
            res[obj["id"]] = Road(obj["allowed_veh"], obj["capacity"], obj["entry"],
                                  [(obj["connectsTo"][j]["id"], obj["connectsTo"][j]["pos"]) for j in range(len(obj["connectsTo"]))])
            vehicle = vehicle.union(set(obj["allowed_veh"]))
        elif obj["type"].lower() == "check-in":
            res[obj["id"]] = Gate(obj["allowed_veh"])
            vehicle = vehicle.union(set(obj["allowed_veh"]))
        else :
            print("unread object : " + str(obj))

    nodes = [res[index] for index in res]
    if validateExtract(res):
        return Graph(res, vehicle, buildConnections(nodes))
    else:
        return None

def buildFromDb():
    db = MongoClient("mongodb+srv://db_user:db_user@dss.icklgr1.mongodb.net/").database_dss.input
    last_entry = db.find_one({},sort=[('_id', DESCENDING)])
    print(last_entry["layout"])
    return buildFromTable(last_entry["layout"])



def getVehiculesType(jsonInput):
    content = json.loads(jsonInput)
    res = set()
    for it in range(len(content)):
        res = res.union(set(content[it]["type-allowed"]))
    return res

def buildConnections(graph):
    res = [[] for _i in range(len(graph))]
    for index in range(len(graph)):
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