import pymongo
from pymongo import MongoClient
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect

from frontend.ui_revised.gui import Ui_PreGateParkingSimulation
from matrix import *
from frontend.visualization.visualization import *
from frontend.validation.GUIgraphCheck import *
import utils
import datetime


class MainWindow(QMainWindow):
    # track coordinates of currently selected tiles
    current_area_selected = []
    # track type of tile
    current_area_selected_color = []

    # Hold information on layout
    parking_layout = []

    # json safe path
    layout_json_save_path = 'layout.json'

    # status text
    status_text_OK = """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; font-weight:600;">Status</span><span style=" font-size:8pt;">: </span><span style=" font-size:8pt; color:#00aa00;">OK</span></p></body></html>
    """

    status_text_NOK = """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; font-weight:600; color:#000000;">Status:</span><span style=" font-size:8pt; color:#00ff00;"> </span><span style=" font-size:8pt; color:#aa0000;">Invalid layout</span></p></body></html>
    """

    status_output_OK = """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; font-weight:600;">Status</span><span style=" font-size:8pt;">: </span><span style=" font-size:8pt; color:#00aa00;">Showing simulation results</span></p></body></html>
"""

    status_output_NOK = """
   <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; font-weight:600;">Status</span><span style=" font-size:8pt;">:</span><span style=" font-size:8pt; color:#00aa00;"> </span><span style=" font-size:8pt; color:#aa0000;">No simulation results yet</span></p></body></html>
"""

    def __init__(self):
        super().__init__()

        # Create an instance of the generated UI class
        self.ui = Ui_PreGateParkingSimulation()
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

        # Add functionality for starting the simulation
        button_simulate = self.ui.but_simulate
        button_simulate.clicked.connect(self.start_simulation)

        # Default status to NOK
        self.ui.textBrowser_status.setHtml(self.status_text_NOK)

    def write_inputs_to_db(self):
        inp_gate_open_time = self.ui.timeEdit_gates_open.dateTime().toString("hh:mm")
        inp_gate_close_time = self.ui.timeEdit_gates_close.dateTime().toString("hh:mm")
        inp_num_cars = self.ui.doubleSpinBox_num_cars.property("value")
        inp_num_trucks = self.ui.doubleSpinBox_num_trucks.property("value")
        inp_num_trailers = self.ui.doubleSpinBox_num_trailers.property("value")
        inp_employee_cost = self.ui.doubleSpinBox_employ_cost.property("value")
        inp_gate_cost = self.ui.doubleSpinBox_gate_cost.property("value")
        inp_ticket_cost = self.ui.doubleSpinBox_ticket_cost.property("value")
        inp_area_width = self.ui.doubleSpinBox_area_width.property("value")
        inp_area_length = self.ui.doubleSpinBox_area_length.property("value")
        inp_perc_online_checkin = self.ui.horizontalSlider_perc_online_checkin.property("value")

        # write input data and layout information into the database
        URI = "mongodb+srv://db_user:db_user@dss.icklgr1.mongodb.net/"
        client = MongoClient(URI)
        db = client.database_dss
        collection_input = db.input

        # create entry for input
        entry = {"parameters":
            {
                "gate_open_time": inp_gate_open_time,
                "gate_closing_time": inp_gate_close_time,
                "no_of_cars": inp_num_cars,
                "no_of_trucks": inp_num_trucks,
                "no_of_trailers": inp_num_trailers,
                "employee_cost": inp_employee_cost,
                "gate_cost": inp_gate_cost,
                "ticket_cost": inp_ticket_cost,
                "total_area_width": inp_area_width,
                "total_area_length": inp_area_length,
                "perc_online_check_in": inp_perc_online_checkin
            },
            "layout": self.parking_layout,
            "timestamp": datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
        }
        collection_input.insert_one(entry)
        client.close()

    def start_simulation(self):
        # gather input fields data
        self.write_inputs_to_db()

    def retrieve_simulation_results(self):
        # check if there is data available for the last simulation
        # write input data and layout information into the database
        URI = "mongodb+srv://db_user:db_user@dss.icklgr1.mongodb.net/"
        client = MongoClient(URI)
        db = client.database_dss
        collection_input = db.input
        collection_output = db.output

        last_entry = collection_input.find_one({}, sort=[('_id', pymongo.DESCENDING)])
        entry_id = last_entry["_id"]
        if collection_output.find_one({"input_id": entry_id}) is not None:
            print(entry_id)
            # Set status to OK
            self.ui.textBrowser_out_result_status.setHtml(self.status_output_OK)
            # gather all data from the simulation (inputs, results)
            out_lab_1 = self.ui.lineEdit_out1
            out_lab_2 = self.ui.lineEdit_out2
            out_lab_3 = self.ui.lineEdit_out3
            out_lab_4 = self.ui.lineEdit_out4
            out_lab_5 = self.ui.lineEdit_out5
            out_lab_6 = self.ui.lineEdit_out6

            out_gate_open = self.ui.lineEdit_gate_open_out
            out_gate_close = self.ui.lineEdit_gate_close_out
            out_num_cars = self.ui.lineEdit_num_cars_out
            out_num_trucks = self.ui.lineEdit_num_trucks_out
            out_num_trailers = self.ui.lineEdit_num_trailers_out
            out_empl_cost = self.ui.lineEdit_employee_cost_out
            out_gate_cost = self.ui.lineEdit_gate_cost_out
            out_ticket_cost = self.ui.lineEdit_ticket_cost_out
            out_area_width = self.ui.lineEdit_area_width_out
            out_area_length = self.ui.lineEdit_area_length_out
            out_perc_online = self.ui.lineEdit_perc_online_checkin_out

            out_lab_1.setText("A")
            out_lab_2.setText("A")
            out_lab_3.setText("A")
            out_lab_4.setText("A")
            out_lab_5.setText("A")
            out_lab_6.setText("A")

            out_gate_open.setText("A")
            out_gate_close.setText("A")
            out_num_cars.setText("A")
            out_num_trucks.setText("A")
            out_num_trailers.setText("A")
            out_empl_cost.setText("A")
            out_gate_cost.setText("A")
            out_ticket_cost.setText("A")
            out_area_width.setText("A")
            out_area_length.setText("A")
            out_perc_online.setText("A")

            # display latest simulated layout
            layout_img = QPixmap('./img/current_gridlayout.jpg')
            layout_img = layout_img.scaled(150, 150)
            layout_img_label = self.ui.img_out_sim_layout
            layout_img_label.setPixmap(layout_img)

            # update simulation text label and id
            lab_sim_text = self.ui.lab_out_simulation_id_text
            lab_sim_id = self.ui.lab_out_simulation_id

            lab_sim_text.setText("Simulation id: ")
            lab_sim_id.setText("0")

            # generate charts for the simulation
            create_handled_vehicles_chart('./img/chart_0_0.png')
            create_income_expenses_chart('./img/chart_0_1.png')
            create_avg_waiting_chart('./img/chart_1_0.png')
            create_co2_emission_chart('./img/chart_1_1.png')

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
        else:
            # Set status to OK
            self.ui.textBrowser_out_result_status.setHtml(self.status_output_NOK)
            print(f"No simulation results for: {entry_id}")

        client.close()

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
        # change status text
        self.ui.textBrowser_status.setHtml(self.status_text_NOK)

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
                        connections,
                    "entry": False
                }

                self.parking_layout.append(area_info)
        # parking & check-in
        elif area_type == "Parking" or area_type == "Check-in":
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
                        connections,
                    "entry": False
                }

                self.parking_layout.append(area_info)
        # entry
        elif area_type == "Entry":
            # in case the area is marked as entry just assign the entry key of the corresponding
            # road to true and color the end of the road violet
            # check each coordinate of current road against existing roads
            for coord in self.current_area_selected:
                # check to which road the entry is connected to
                for area in self.parking_layout:
                    range_start = (area['start_pos']['x'], area['start_pos']['y'])
                    range_end = (area['end_pos']['x'], area['end_pos']['y'])

                    # if it is an overlap, change the entry key of the road to true
                    if is_coordinate_in_range(coord, range_start, range_end):
                        print(f'{coord} overlapping with road')
                        update_entry_key_for_road(self.parking_layout, area['id'])

        # print(f'====================\n'
        #       f'Area type: {area_type}\n'
        #       f'Allowed: {allowed_vehicles}\n'
        #       f'Parking: {capacity}\n'
        #       f'Multiplier: {capacity_multiplier}\n'
        #       f'Total: {int(capacity * capacity_multiplier)}')

        print("Added area to layout!")
        print(self.parking_layout)

        # create screenshot of current layout
        screenshot = self.grab(QRect(10, 220, 435, 395))
        # Save the screenshot as an image file
        screenshot.save("./img/current_gridlayout.jpg", "JPG")
        print("Screenshot saved!")

        # write layout to json file
        utils.write_layout_to_json(self.layout_json_save_path, self.parking_layout)

        # reset area type to road (index = 0)
        self.ui.comboBox_area_type.setCurrentIndex(0)

        # clear current selection
        self.current_area_selected.clear()
        self.current_area_selected_color.clear()

        # reset multiplier
        self.ui.horSlider_capacity_multiplier.setValue(100)

        # check for valid layout
        if isLayoutValid(self.convert_matrix_to_string()):
            # activate simulate button
            self.ui.but_simulate.setEnabled(True)
            # change status text
            self.ui.textBrowser_status.setHtml(self.status_text_OK)

    def handle_click_event_grid(self):
        button = self.sender()

        # before changing the color, remember the color (type) of the tile to help with reset selection process
        self.current_area_selected_color.append(button.property("color"))

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

        print(self.current_area_selected)
        print(self.current_area_selected_color)

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
        return layout_string[:-1]

    def reset_current_selection(self):
        counter = 0
        for x, y in self.current_area_selected:
            btn = self.ui.gridLayout_roads.itemAtPosition(x, y).widget()
            if btn.property("color") == "gray":
                btn.setProperty("color", None)
                btn.setStyleSheet("background-color: None")
            else:
                color = self.current_area_selected_color[counter]
                btn.setProperty("color", color)
                btn.setStyleSheet("background-color: " + color)
            counter += 1

        self.current_area_selected.clear()
        self.current_area_selected_color.clear()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
