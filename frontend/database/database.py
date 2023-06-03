#install pymongo -> https://www.tutorialkart.com/mongodb/connect-to-mongodb-from-python/
#work with pymongo -> https://pymongo.readthedocs.io/en/stable/tutorial.html

import pymongo
from pymongo import MongoClient

#Conection to DB
URI = "mongodb+srv://db_user:db_user@dss.icklgr1.mongodb.net/"
client = MongoClient(URI)
print("Connection Successful")
db = client.database_dss
#two different collections, one for input and one for output
collection_input = db.input
collection_output = db.output

#INPUT
#create entry for input
entry = {"parameters":
    {
        "gate_open_time": "12:00",
        "gate_closing_time": "17:00",
        "no_of_cars": 201,
        "no_of_trucks": 51,
        "no_of_trailers": 21,
        "employee_cost": 11,
        "gate_cost": 10,
        "ticket_cost": 15,
        "total_area_width": 50.00,
        "total_area_length": 75.00,
        "perc_online_check_in": 10
    },
    "layout":
        [
            {
                "id": 0,
                "type": "Road",
                "capacity": 3.0,
                "allowed_veh": [],
                "start_pos": {
                    "x": 0,
                    "y": 4
                },
                "end_pos": {
                    "x": 0,
                    "y": 6
                },
                "connectsTo": []
            }
        ]
}
#id = collection_input.insert_one(entry).inserted_id
#print(id)

#for input -> to check if output is available for input
last_entry = collection_input.find_one({},sort=[('_id', pymongo.DESCENDING)])
id = last_entry["_id"]
if collection_output.find_one({"input_id":id}) is not None :
    print(id)


#OUTPUT

#get last entry from input
last_entry = collection_input.find_one({},sort=[('_id', pymongo.DESCENDING)])
#print(last_entry)

#create entry for database
output = {
    "input_id" : last_entry["_id"],
    "simulation": "OUTPUT"
}
#to insert created entry in database
#collection_output.insert_one(output)

client.close()
