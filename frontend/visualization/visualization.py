import matplotlib.pyplot as mpl
import numpy as np
import pymongo
from pymongo import MongoClient


URI = "mongodb+srv://db_user:db_user@dss.icklgr1.mongodb.net/"
client = MongoClient(URI)
print("Connection Successful")
db = client.database_dss
#two different collections, one for input and one for output
collection_input = db.input
collection_output = db.output

last_input = collection_input.find_one({},sort=[('_id', pymongo.DESCENDING)])
last_output = collection_output.find_one({},sort=[('_id', pymongo.DESCENDING)])

print(last_input)

#---------------------------------------------------

cars = last_output["outputs"]["total_number_cars"]
trucks = last_output["outputs"]["total_number_trucks"]
ticket_price = last_input["parameters"]["ticket_cost"]
gate_cost = last_input["parameters"]["gate_cost"]
employee_cost = last_input["parameters"]["employee_cost"]
gates = 4
gates_open = 2  # hours


# how much is for the parking?
# 5% for the pre-gate-parking
percentage_for_parking = 0.05
ticket_parking = ticket_price * percentage_for_parking

income = (cars * ticket_parking) + (trucks * (ticket_parking * 1.5))

# Expenses = price for each employee per gate (excl. sel-check-in) and hours + gates cost per hour
expenses = (gates * (gates_open * employee_cost)) + (gates * (gates_open * gate_cost))

# chart
fig = mpl.figure(figsize=(5, 5))
ax = fig.add_subplot()
x_labels = ["Income", "Expenses"]
y_axis = [income, expenses]
data_x = np.arange(len(x_labels))
barlist = ax.bar(data_x, y_axis)
barlist[1].set_color('red')
ax.set_ylabel('Euro')
ax.set_title('Overview of Income and Expenses')
ax.set_xticks(data_x, x_labels)

mpl.show()






def create_handled_vehicles_chart(save_path):
    # chart 1 ---------------------------------------------------------------------------------------
    # Handled Vehicles per Gate
    # creating ficticious data to plot.
    gates = [1, 2, 3, 4]
    data_y1 = [10, 20, 30, 40]
    data_y2 = [20, 30, 40, 50]
    data_x = np.arange(len(gates))
    # Creating the Figure container
    fig = mpl.figure(figsize=(5, 5))
    # Creating the axis
    ax = fig.add_subplot()
    # Line plot command
    ax.bar(data_x, data_y1, label='Vehicles handled')
    ax.bar(data_x, data_y2, bottom=data_y1, label='Vehicles waiting')
    ax.set_ylabel('Vehicles')
    ax.set_xlabel('Gates')
    ax.set_title('Handled Vehicles per Gate')
    ax.legend()

    ax.set_xticks(data_x, gates)
    fig.savefig(save_path)
    # ax.grid()
    # mpl.show()


def create_income_expenses_chart(save_path):
    # chart 2 ---------------------------------------------------------------------------------------
    # Overview of Income and Expenses
    # Income = sold ticked
    cars = 35
    trucks = 25
    ticket_price = 7.5
    # how much is for the parking?
    # 5% for the pre-gate-parking
    percentage_for_parking = 0.05
    ticket_parking = ticket_price * percentage_for_parking

    income = (cars * ticket_parking) + (trucks * (ticket_parking * 1.5))

    # Expenses = price for each employee per gate (excl. sel-check-in) and hours

    gates = 4
    gates_open = 2  # hours
    # payment between 10 to 20 wuro
    payment = 15  # hours

    expenses = (gates * (gates_open * payment))

    # chart
    fig = mpl.figure(figsize=(5, 5))
    ax = fig.add_subplot()
    x_labels = ["Income", "Expenses"]
    y_axis = [income, expenses]
    data_x = np.arange(len(x_labels))
    barlist = ax.bar(data_x, y_axis)
    barlist[1].set_color('red')
    ax.set_ylabel('Euro')
    ax.set_title('Overview of Income and Expenses')
    ax.set_xticks(data_x, x_labels)
    # mpl.show()
    fig.savefig(save_path)


def create_avg_waiting_chart(save_path):
    # chart 3 ---------------------------------------------------------------------------------------
    # Average waiting time
    #avg_cars_waiting = last_output["_id"]["avg_waiting_time_car"]
    #print(avg_cars_waiting)

    avg_car = last_output["outputs"]["avg_waiting_time_car"]
    avg_truck = last_output["outputs"]["avg_waiting_time_truck"]
    fig = mpl.figure(figsize=(5, 5))
    ax = fig.add_subplot()
    x_labels = ["Car", "Truck"]
    y_axis = [avg_car, avg_truck]
    data_x = np.arange(len(x_labels))
    ax.bar(data_x, y_axis)
    ax.set_ylabel('Minutes')
    ax.set_title('Average Waiting Time in Minutes')
    ax.set_xticks(data_x, x_labels)
    # mpl.show()
    fig.savefig(save_path)


def create_co2_emission_chart(save_path):
    # chart 4 ---------------------------------------------------------------------------------------
    # CO² Emission of Vehicles
    # Car: 19,1 g CO² per min
    # Truck: 45,56 g CO² per min
    emission_car = 19.1
    emission_truck = 45.56

    fig = mpl.figure(figsize=(5, 5))
    ax = fig.add_subplot()
    gates = [1, 2, 3, 4]

    waiting_time_cars = [50, 30, 58, 48]
    waiting_time_trucks = [60, 12, 0, 70]

    # to add emission
    for i in range(len(waiting_time_cars)):
        waiting_time_cars[i] = waiting_time_cars[i] * emission_car

    for i in range(len(waiting_time_trucks)):
        waiting_time_trucks[i] = waiting_time_trucks[i] * emission_truck

    print(waiting_time_cars)
    data_x = np.arange(len(gates))
    width = 0.25
    ax.bar(data_x - width / 2, waiting_time_cars, width, label='Cars')
    ax.bar(data_x + width / 2, waiting_time_trucks, width, label='Trucks')
    ax.set_ylabel('co¹ emission in gramm per min')
    ax.set_xlabel('Gates')
    ax.set_title('Produced CO² Emission during Waiting Time')
    ax.set_xticks(data_x, gates)
    ax.grid()
    ax.legend()
    # mpl.show()
    fig.savefig(save_path)