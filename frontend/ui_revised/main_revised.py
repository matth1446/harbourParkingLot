from PyQt5.QtWidgets import QApplication, QMainWindow
from gui import Ui_MainWindow
from matrix import is_coordinate_in_range, update_connection_between_areas


class MainWindow(QMainWindow):
    current_area_selected = []
    # Hold information on layout
    parking_layout = []

    def __init__(self):
        super().__init__()

        # Create an instance of the generated UI class
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setGeometry(100, 100, 800, 900)

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

        # Add functionality for updating capacity multiplier text when moving slider
        slider_capacity_multiplier = self.ui.horSlider_capacity_multiplier
        slider_capacity_multiplier.valueChanged.connect(self.update_multiplier_text)

        all = []
        a = {
            "text": "a"
        }
        b = {
            "text": "b"
        }

        all.append(a)
        all.append(b)

        # print(all)

    def update_multiplier_text(self):
        slider_capacity_multiplier = self.ui.horSlider_capacity_multiplier
        slider_val = slider_capacity_multiplier.property("value") / 100.0

        label_capacity_multiplier = self.ui.lab_horSlider_capacity_multi
        label_capacity_multiplier.setText(f'x {slider_val}')

    def reset_area_layout(self):
        for row in range(self.ui.gridLayout_roads.rowCount()):
            for col in range(self.ui.gridLayout_roads.columnCount()):
                btn = self.ui.gridLayout_roads.itemAtPosition(row, col).widget()
                btn.setProperty("color", "None")
                btn.setStyleSheet("background-color: None")
        # clear current selection
        self.current_area_selected.clear()

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

        # update counter (node_id)
        area_id = len(self.parking_layout)

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
                btn.setProperty("color", "yellow")
                btn.setStyleSheet("background-color: yellow")
            elif area_type == "Check-in":
                btn.setProperty("color", "green")
                btn.setStyleSheet("background-color: green")

        # handle areas and connections
        # roads
        if area_type == "Road":
            num_entries = len(self.current_area_selected)
            # if it is a road the capacity is equal to the number of tiles
            capacity = num_entries
            connections = []

            if num_entries > 0:  # only if there is more than 1 entry
                start_coords = self.current_area_selected[0]
                end_coords = self.current_area_selected[num_entries - 1]

                # check each coordinate of current road against existing roads
                for coord in self.current_area_selected:
                    for area in self.parking_layout:
                        range_start = (area['start_pos']['x'], area['start_pos']['y'])
                        range_end = (area['end_pos']['x'], area['end_pos']['y'])

                        # if there is an overlap, get node_id from other area
                        if is_coordinate_in_range(coord, range_start, range_end):
                            # id of current area = area_id
                            other_area_id = area['node_id']

                            # add connection to current area (connection list)
                            connections.append([other_area_id, 0])

                            # change connection information in other area
                            update_connection_between_areas(
                                self.parking_layout, other_area_id, area_id
                            )

                # add area to layout
                area_info = {
                    "node_id": area_id,
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
                    "connectsTo": [
                        connections
                    ]
                }

                self.parking_layout.append(area_info)

        # print(f'====================\n'
        #       f'Area type: {area_type}\n'
        #       f'Allowed: {allowed_vehicles}\n'
        #       f'Parking: {capacity}\n'
        #       f'Multiplier: {capacity_multiplier}\n'
        #       f'Total: {int(capacity * capacity_multiplier)}')

        print(self.parking_layout)
        # print("Added area to layout!")
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


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
