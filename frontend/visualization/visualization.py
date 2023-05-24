import matplotlib.pyplot as mpl
import numpy as np


def create_handled_vehicles_chart():
    # chart 1 ---------------------------------------------------------------------------------------
    # Handled Vehicles per Gate
    # createing ficticious data to plot.
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
    # ax.grid()
    # mpl.show()


def create_income_expenses_chart():
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


def create_avg_waiting_chart():
    # chart 3 ---------------------------------------------------------------------------------------
    # Average waiting time
    avg_car = 23
    avg_truck = 45
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


def create_co2_emission_chart():
    # chart 4 ---------------------------------------------------------------------------------------
    # CO² Emission of Vehicles
    # Car: 19,1 Gramm CO² per min
    # Truck: 45,56 gramm CO² per min
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

    mpl.show()