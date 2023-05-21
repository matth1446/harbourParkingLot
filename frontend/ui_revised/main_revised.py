from PyQt5.QtWidgets import QApplication, QMainWindow
from gui import Ui_MainWindow


class MainWindow(QMainWindow):
    current_area_selected = []

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

    def reset_area_layout(self):
        for row in range(self.ui.gridLayout_roads.rowCount()):
            for col in range(self.ui.gridLayout_roads.columnCount()):
                btn = self.ui.gridLayout_roads.itemAtPosition(row, col).widget()
                btn.setProperty("color", "None")
                btn.setStyleSheet("background-color: None")
        # clear current selection
        self.current_area_selected.clear()

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

        # first get necessary info for json and save them in variables
        # get current area type for coloring
        area_type = self.ui.comboBox_area_type.currentText()

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

        print(area_type)
        print(allowed_vehicles)

        for x, y in self.current_area_selected:
            btn = self.ui.gridLayout_roads.itemAtPosition(x, y).widget()
            if area_type == "Road":
                btn.setProperty("color", "red")
                btn.setStyleSheet("background-color: red")
            elif area_type == "Entry":
                btn.setProperty("color", "violet")
                btn.setStyleSheet("background-color: violet")
            elif area_type == "Parking":
                btn.setProperty("color", "yellow")
                btn.setStyleSheet("background-color: yellow")
            elif area_type == "Check-in":
                btn.setProperty("color", "green")
                btn.setStyleSheet("background-color: green")

        print("Added area to layout!")
        # reset area type to road (index = 0)
        self.ui.comboBox_area_type.setCurrentIndex(0)
        # clear current selection
        self.current_area_selected.clear()

    def handle_click_event_grid(self):
        button = self.sender()

        # check if current button has already area type associated and color it differently
        if button.property("color") is not None:
            button.setProperty("color", "darkorange")
            button.setStyleSheet("background-color: darkorange")
        else:
            button.setProperty("color", "gray")
            button.setStyleSheet("background-color: gray")

        print(str(button.property("objectName")).split("_")[1],
              str(button.property("objectName")).split("_")[2])

        # add current coord tuple to selection
        self.current_area_selected.append(
            (
                int(str(button.property("objectName")).split("_")[1]),
                int(str(button.property("objectName")).split("_")[2])
            )
        )
        print(self.current_area_selected)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
