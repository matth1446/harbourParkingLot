from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.uic.properties import QtCore

from frontend.ui_revised.gui import Ui_MainWindow
from matrix import is_coordinate_in_range, update_connection_between_areas
import utils
import matplotlib.pyplot as mpl
import numpy as np


class MainWindow(QMainWindow):
    current_area_selected = []

    # Hold information on layout
    parking_layout = []

    # json safe path
    layout_json_save_path = 'layout.json'

    def __init__(self):
        super().__init__()

        # Create an instance of the generated UI class
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # self.setGeometry(100, 100, 800, 900)

        # Add functionality to grid buttons
        for row in range(self.ui.gridLayout_roads.rowCount()):
            for col in range(self.ui.gridLayout_roads.columnCount()):
                btn_on_grid = self.ui.gridLayout_roads.itemAtPosition(row, col).widget()
                btn_on_grid.clicked.connect(self.handle_click_event_grid)

        button_add_area = self.ui.but_add_to_layout
        button_add_area.clicked.connect(self.add_area_to_layout)

        # Add functionality for resetting layout
        button_reset_layout = self.ui.but_reset_layout
        button_reset_layout.clicked.connect(self.reset_area_layout)

        # Add functionality for resetting the current selection
        button_reset_selection = self.ui.but_reset_selection
        button_reset_selection.clicked.connect(self.reset_current_selection)

        # Add functionality for updating capacity multiplier text when moving slider
        slider_capacity_multiplier = self.ui.horSlider_capacity_multiplier
        slider_capacity_multiplier.valueChanged.connect(self.update_multiplier_text)

        # Add functionality for plotting a chart to the output panel
        button_retrieve_results = self.ui.but_retrieve_res
        button_retrieve_results.clicked.connect(self.retrieve_simulation_results)

    def retrieve_simulation_results(self):
        # gather all data from the simulation (inputs, results)

        # generate charts for the simulation

        ax, fig = self.create_serviced_vehicles_chart()

        # create chart two
        cars = 35
        trucks = 25
        ticket_price = 7.5
        percentage_for_parking = 0.05
        gates = 4
        gates_open = 2  # hours
        payment = 15  # hours

        ticket_parking = ticket_price * percentage_for_parking

        income = (cars * ticket_parking) + (trucks * (ticket_parking * 1.5))
        # Expenses = price for each employee per gate (excl. sel-check-in) and hours
        expenses = (gates * (gates_open * payment))

        x_labels = ["Income", "Expenses"]
        y_axis = [income, expenses]
        data_x = np.arange(len(x_labels))
        barlist = ax.bar(data_x, y_axis)
        barlist[1].set_color('red')
        ax.set_ylabel('Euro')
        ax.set_title('Overview of Income and Expenses')
        ax.set_xticks(data_x, x_labels)

        fig.savefig('img/chart_0_1.png')
        ax.clear()

        # create chart three
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

        fig.savefig('img/chart_1_0.png')
        ax.clear()

        # create chart four
        emission_car = 19.1
        emission_truck = 45.56
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

        fig.savefig('img/chart_1_1.png')

        # assigning charts to the placeholders

        chart_img_0_0 = QPixmap('./img/chart_0_0.png')
        chart_img_0_0 = chart_img_0_0.scaled(500, 500)

        chart_img_0_1 = QPixmap('./img/chart_0_1.png')
        chart_img_0_1 = chart_img_0_1.scaled(500, 500)

        chart_img_1_0 = QPixmap('./img/chart_1_0.png')
        chart_img_1_0 = chart_img_1_0.scaled(500, 500)

        chart_img_1_1 = QPixmap('./img/chart_1_1.png')
        chart_img_1_1 = chart_img_1_1.scaled(500, 500)

        chart_0_0_label = self.ui.img_out_0_0
        chart_0_0_label.setPixmap(chart_img_0_0)

        chart_0_1_label = self.ui.img_out_0_1
        chart_0_1_label.setPixmap(chart_img_0_1)

        chart_1_0_label = self.ui.img_out_1_0
        chart_1_0_label.setPixmap(chart_img_1_0)

        chart_1_1_label = self.ui.img_out_1_1
        chart_1_1_label.setPixmap(chart_img_1_1)

        # update simulation text label and id
        lab_sim_text = self.ui.lab_out_simulation_id_text
        lab_sim_id = self.ui.lab_out_simulation_id

        lab_sim_text.setText("Simulation id: ")
        lab_sim_id.setText("0")

    def create_serviced_vehicles_chart(self):
        # create chart one
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
        fig.savefig('img/chart_0_0.png')
        ax.clear()
        return ax, fig

    def update_multiplier_text(self):
        slider_capacity_multiplier = self.ui.horSlider_capacity_multiplier
        slider_val = slider_capacity_multiplier.property("value") / 100.0

        label_capacity_multiplier = self.ui.lab_horSlider_capacity_multi
        label_capacity_multiplier.setText(f'x {slider_val}')

    def reset_area_layout(self):
        # before resetting the layout create a string
        self.convert_matrix_to_string()

        for row in range(self.ui.gridLayout_roads.rowCount()):
            for col in range(self.ui.gridLayout_roads.columnCount()):
                btn = self.ui.gridLayout_roads.itemAtPosition(row, col).widget()
                btn.setProperty("color", "None")
                btn.setStyleSheet("background-color: None")
        # clear current selection
        self.current_area_selected.clear()
        # clear current layout
        self.parking_layout.clear()

    def get_vehicles_data(self):
        allowed_vehicles = []
        allowed_cars = self.ui.checkBox_allowed_car.isChecked()
        allowed_trucks = self.ui.checkBox_allowed_truck.isChecked()
        allowed_trailers = self.ui.checkBox_allowed_disabled.isChecked()
        allowed_disabled = self.ui.checkBox_allowed_disabled.isChecked()
        allowed_online = self.ui.checkBox_allowed_online.isChecked()

        if allowed_cars:
            allowed_vehicles.append("cars")

        if allowed_trucks:
            allowed_vehicles.append("trucks")

        if allowed_trailers:
            allowed_vehicles.append("trailers")

        if allowed_disabled:
            allowed_vehicles.append("disabled")

        if allowed_online:
            allowed_vehicles.append("online")

        return allowed_vehicles

    def add_area_to_layout(self):
        """
        each type of area has a different color
        when a user clicks on a tile it changes to light-blue (selected)
        once the user adds the current area to the layout, the color for the type of
        area will change accordingly:
        - red = road
        - green = check-in
        - yellow = parking
        - violet = entry

        Limitations:
        - Top row = only check-in possible
        - Bottom row = only entry possible
        """

        # update counter (id)
        area_id = len(self.parking_layout)
        # store all connections
        connections = []

        # first get necessary info for json and save them in variables
        # get current area type for coloring
        area_type = self.ui.comboBox_area_type.currentText()
        print(area_type)

        # get allowed vehicle types
        allowed_vehicles = self.get_vehicles_data()
        print(allowed_vehicles)

        # get capacity and capacity multiplier
        capacity = self.ui.doubleSpinBox_capacity.property("value")
        capacity_multiplier = self.ui.horSlider_capacity_multiplier.property("value") / 100.0

        # assign colors to tiles
        for x, y in self.current_area_selected:
            btn = self.ui.gridLayout_roads.itemAtPosition(x, y).widget()
            if area_type == "Road":
                btn.setProperty("color", "red")
                btn.setStyleSheet("background-color: red")
            elif area_type == "Entry":
                btn.setProperty("color", "violet")
                btn.setStyleSheet("background-color: violet")
            elif area_type == "Parking":
                # if area = parking; also check for the capacity
                # btn.setProperty("color", "yellow")
                # btn.setStyleSheet("background-color: yellow")
                print()
            elif area_type == "Check-in":
                btn.setProperty("color", "green")
                btn.setStyleSheet("background-color: green")

        # handle areas and connections
        num_entries = len(self.current_area_selected)

        # roads
        if area_type == "Road":
            # if it is a road the capacity is equal to the number of tiles
            capacity = num_entries

            if num_entries > 0:  # only if there is more than 1 entry
                start_coords = self.current_area_selected[0]
                end_coords = self.current_area_selected[num_entries - 1]

                # check each coordinate of current road against existing roads
                for coord in self.current_area_selected:
                    for area in self.parking_layout:
                        range_start = (area['start_pos']['x'], area['start_pos']['y'])
                        range_end = (area['end_pos']['x'], area['end_pos']['y'])

                        # if there is an overlap, get id from other area
                        if is_coordinate_in_range(coord, range_start, range_end):
                            # id of current area = area_id
                            other_area_id = area['id']

                            # add connection to current area (connection list)
                            connections.append({"id": other_area_id, "pos": 0})

                            # change connection information in other area
                            update_connection_between_areas(
                                self.parking_layout, other_area_id, area_id
                            )

                # add area to layout
                area_info = {
                    "id": area_id,
                    "type": area_type,
                    "capacity": capacity * capacity_multiplier,
                    "allowed_veh": allowed_vehicles,
                    "start_pos": {
                        "x": start_coords[0],
                        "y": start_coords[1]
                    },
                    "end_pos": {
                        "x": end_coords[0],
                        "y": end_coords[1]
                    },
                    "connectsTo":
                        connections

                }

                self.parking_layout.append(area_info)

        elif area_type == "Parking" or area_type == "Entry" or area_type == "Check-in":
            # assign color according to area
            color = ""
            if area_type == "Parking":
                color = "yellow"
            elif area_type == "Entry":
                color = "violet"
            elif area_type == "Check-in":
                color = "green"

            coord = ()
            # check if there are exactly 2 entries (one = parking/entry/check-in, other one = connection to road)
            if num_entries == 2:
                start_coord = self.current_area_selected[0]
                end_coord = self.current_area_selected[num_entries - 1]

                # check if either start or end coordinate are connected with
                for area in self.parking_layout:
                    range_start = (area['start_pos']['x'], area['start_pos']['y'])
                    range_end = (area['end_pos']['x'], area['end_pos']['y'])

                    # if start_coord is an overlap, get id from other area
                    if is_coordinate_in_range(start_coord, range_start, range_end):
                        coord = start_coord
                        print(f'{start_coord} overlapping with road')
                        # color the tile that has an overlap with the road red
                        btn_overlap = self.ui.gridLayout_roads.itemAtPosition(start_coord[0], start_coord[1]).widget()
                        btn_overlap.setProperty("color", "red")
                        btn_overlap.setStyleSheet("background-color: red")

                        # color the tile that connects to the road yellow = parking
                        btn_parking = self.ui.gridLayout_roads.itemAtPosition(end_coord[0], end_coord[1]).widget()
                        btn_parking.setProperty("color", color)
                        btn_parking.setStyleSheet("background-color: " + color)

                        # update the connection information for the tiles
                        other_area_id = area['id']

                        # add connection to current area (connection list)
                        connections.append({"id": other_area_id, "pos": 0})

                        # change connection information in other area
                        update_connection_between_areas(
                            self.parking_layout, other_area_id, area_id
                        )

                    # if end_coord is an overlap, get id from other area
                    elif is_coordinate_in_range(end_coord, range_start, range_end):
                        coord = end_coord
                        print(f'{end_coord} overlapping with road')
                        btn_overlap = self.ui.gridLayout_roads.itemAtPosition(end_coord[0], end_coord[1]).widget()
                        btn_overlap.setProperty("color", "red")
                        btn_overlap.setStyleSheet("background-color: red")

                        # color the tile that connects to the road
                        btn_parking = self.ui.gridLayout_roads.itemAtPosition(start_coord[0], start_coord[1]).widget()
                        btn_parking.setProperty("color", color)
                        btn_parking.setStyleSheet("background-color: " + color)

                        # update the connection information for the tiles
                        other_area_id = area['id']

                        # add connection to current area (connection list)
                        connections.append({"id": other_area_id, "pos": 0})

                        # change connection information in other area
                        update_connection_between_areas(
                            self.parking_layout, other_area_id, area_id
                        )

                # add area to layout
                area_info = {
                    "id": area_id,
                    "type": area_type,
                    "capacity": capacity,
                    "allowed_veh": allowed_vehicles,
                    "start_pos": {
                        "x": coord[0],
                        "y": coord[1]
                    },
                    "end_pos": {
                        "x": coord[0],
                        "y": coord[1]
                    },
                    "connectsTo":
                        connections

                }

                self.parking_layout.append(area_info)

        # print(f'====================\n'
        #       f'Area type: {area_type}\n'
        #       f'Allowed: {allowed_vehicles}\n'
        #       f'Parking: {capacity}\n'
        #       f'Multiplier: {capacity_multiplier}\n'
        #       f'Total: {int(capacity * capacity_multiplier)}')

        print("Added area to layout!")
        print(self.parking_layout)

        # write layout to json file
        utils.write_layout_to_json(self.layout_json_save_path, self.parking_layout)

        # reset area type to road (index = 0)
        self.ui.comboBox_area_type.setCurrentIndex(0)

        # clear current selection
        self.current_area_selected.clear()

        # reset multiplier
        self.ui.horSlider_capacity_multiplier.setValue(100)

    def handle_click_event_grid(self):
        button = self.sender()

        # check if current button has already area type associated and color it differently
        if button.property("color") != "None" and button.property("color") is not None:
            button.setProperty("color", "darkorange")
            button.setStyleSheet("background-color: darkorange")
        else:
            button.setProperty("color", "gray")
            button.setStyleSheet("background-color: gray")

        # add current coord tuple to selection
        self.current_area_selected.append(
            (
                int(str(button.property("objectName")).split("_")[1]),
                int(str(button.property("objectName")).split("_")[2])
            )
        )

    def convert_matrix_to_string(self):
        layout_string = ""

        # go through each tile and add its type to the string
        for row in range(self.ui.gridLayout_roads.rowCount()):
            for col in range(self.ui.gridLayout_roads.columnCount()):
                btn = self.ui.gridLayout_roads.itemAtPosition(row, col).widget()
                """according to the button color represent area type as letter
                N ... None, R ... Road (red), P ... Parking (yellow), 
                G ... Check-in gate (green), E ... Entry (violet)"""
                match btn.property("color"):
                    case "red":
                        layout_string += "R,"
                    case "yellow":
                        layout_string += "P,"
                    case "green":
                        layout_string += "G,"
                    case "violet":
                        layout_string += "E,"
                    case _:
                        layout_string += "N,"

        utils.write_content_to_file('layout_matrix.txt', layout_string)

    def reset_current_selection(self):
        for x, y in self.current_area_selected:
            btn = self.ui.gridLayout_roads.itemAtPosition(x, y).widget()
            btn.setProperty("color", None)
            btn.setStyleSheet("background-color: None")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
