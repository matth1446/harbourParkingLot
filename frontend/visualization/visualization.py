import matplotlib.pyplot as mpl
import numpy as np


def addlabels(x, y):
    for i in range(len(x)):
        mpl.text(i, y[i], "{:.2f}".format(y[i]), ha='center')


def create_handled_vehicles_chart(save_path, keys_array, did_pass, did_not_pass):
    # chart 1 ---------------------------------------------------------------------------------------
    # Handled Vehicles per Gate
    # creating ficticious data to plot.
    data_x = np.arange(len(keys_array))
    # Creating the Figure container
    fig = mpl.figure(figsize=(5, 5))
    # Creating the axis
    ax = fig.add_subplot()
    # Line plot command
    bar_width = 0.8
    ax.bar(data_x, did_pass, label='Vehicles handled', width=bar_width, align="center")
    ax.bar(data_x, did_not_pass, bottom=did_pass, label='Vehicles waiting', width=bar_width, align="center")

    array = []
    if len(keys_array) == 1:
        print(len(keys_array))
        ax.set_ylim(0, (sum(did_pass) + sum(did_not_pass)) * 1.2)
        print(sum(did_pass) + sum(did_not_pass) * 1.2)
        ax.set_xlim(-0.8, 0.8)
    else:
        for i in range(len(did_pass)):
            array.append(did_pass[i] + did_not_pass[i])
        val = max(array)
        ax.set_ylim(0, val * 1.2)


    did_and_did_not = []
    for i in range(len(did_pass)):
        did_and_did_not.append(did_pass[i] + did_not_pass[i])

    addlabels(keys_array, did_and_did_not)

    ax.set_ylabel('Vehicles')
    ax.set_xlabel('Gates')
    ax.set_title('Handled Vehicles per Gate')
    ax.legend()
    # Setting x-tick labels
    ax.set_xticks(data_x)
    ax.set_xticklabels(keys_array)
    mpl.tight_layout()
    fig.savefig(save_path)

    # ax.grid()
    # mpl.show()


def create_income_expenses_chart(save_path, income, expenses):
    # chart 2 ---------------------------------------------------------------------------------------
    # Overview of Income and Expenses
    # chart
    fig = mpl.figure(figsize=(5, 5))
    ax = fig.add_subplot()
    x_labels = ["Ticket Income", "Expenses"]
    y_axis = [income, expenses]
    data_x = np.arange(len(x_labels))
    barlist = ax.bar(data_x, y_axis)
    barlist[1].set_color('red')
    barlist[0].set_color('green')
    addlabels(x_labels, y_axis)
    ax.set_ylabel('Euro')
    ax.set_title('Overview of Ticket Income and Expenses')
    ax.set_xticks(data_x, x_labels)
    # mpl.show()
    fig.savefig(save_path)


def create_avg_waiting_chart(save_path, avg_car, avg_truck):
    # chart 3 ---------------------------------------------------------------------------------------
    # Average waiting time
    # avg_cars_waiting = last_output["_id"]["avg_waiting_time_car"]
    # print(avg_cars_waiting)

    fig = mpl.figure(figsize=(5, 5))
    ax = fig.add_subplot()
    x_labels = ["Car", "Truck"]
    y_axis = [avg_car, avg_truck]
    data_x = np.arange(len(x_labels))
    barlist = ax.bar(data_x, y_axis)
    barlist[1].set_color('orange')
    addlabels(x_labels, y_axis)
    ax.set_ylabel('Minutes')
    ax.set_title('Average Waiting Time in Minutes')
    ax.set_xticks(data_x, x_labels)
    # mpl.show()
    fig.savefig(save_path)


def create_co2_emission_chart(save_path, emission_car_all, emission_truck_all):
    # chart 4 ---------------------------------------------------------------------------------------
    # CO² Emission of Vehicles
    # Car: 19,1 g CO² per min
    # Truck: 45,56 g CO² per min

    fig = mpl.figure(figsize=(5, 5))
    ax = fig.add_subplot()
    x_labels = ["Cars", "Trucks"]

    y_axis = [(emission_car_all), (emission_truck_all)]
    data_x = np.arange(len(x_labels))
    barlist = ax.bar(data_x, y_axis)
    barlist[1].set_color('orange')
    addlabels(x_labels, y_axis)
    ax.set_ylabel('co¹ emission in gramm per min')
    ax.set_title('Produced CO² Emission during Waiting Time')
    ax.set_xticks(data_x, x_labels)
    # ax.set_yticks(y_axis,"k")
    ylabels = ['{:,.0f}'.format(x) + 'K' for x in ax.get_yticks() / 1000]
    ax.set_yticklabels(ylabels)
    fig.savefig(save_path)
