import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QLineEdit

import utils

# Define the file name and location
file_path = 'grid_layout.json'
txt_file_path = 'grid_layout.txt'

# Create an empty list to hold entries
matrix = [
    ["R", "R", "R", "R", "R"],
    ["R", "N", "N", "R", "N"],
    ["R", "N", "N", "N", "N"],
    ["R", "N", "N", "N", "N"],
    ["R", "N", "N", "N", "N"]
]

X_SIZE = 5
Y_SIZE = 5


# noinspection PyUnresolvedReferences
class Grid(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Grid')
        self.setGeometry(100, 100, 500, 500)

        # Create the grid layout
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)

        # Add the buttons to the grid layout
        for i in range(X_SIZE):
            for j in range(Y_SIZE):
                button = QPushButton()
                button.setFixedSize(50, 50)
                # handle changing colors (left-click)
                button.setStyleSheet('background-color: white')
                # button.setText(f'{i},{j}')
                button.setText('0')
                button.clicked.connect(self.change_color)
                # handle increasing capacity (right-click)
                button.setContextMenuPolicy(Qt.CustomContextMenu)
                button.customContextMenuRequested.connect(self.right_click)
                self.grid_layout.addWidget(button, i, j)

        # Create the input layout
        input_layout = QGridLayout()

        # Add labels and input fields to the input layout
        input_layout.addWidget(QLabel('Field 1:'), 0, 0)
        input_layout.addWidget(QLineEdit(), 0, 1)
        input_layout.addWidget(QLabel('Field 2:'), 1, 0)
        input_layout.addWidget(QLineEdit(), 1, 1)
        input_layout.addWidget(QLabel('Field 3:'), 2, 0)
        input_layout.addWidget(QLineEdit(), 2, 1)
        input_layout.addWidget(QLabel('Field 4:'), 3, 0)
        input_layout.addWidget(QLineEdit(), 3, 1)
        input_layout.addWidget(QLabel('Field 5:'), 4, 0)
        input_layout.addWidget(QLineEdit(), 4, 1)
        input_layout.addWidget(QLabel('Field 6:'), 5, 0)
        input_layout.addWidget(QLineEdit(), 5, 1)

        # Create the save button
        save_button = QPushButton('Save')
        input_layout.addWidget(save_button, 6, 0, 1, 2)

        # Create the generate button for JSON generation
        generate_button = QPushButton('Generate', self)
        input_layout.addWidget(generate_button, 7, 0, 1, 2)
        generate_button.clicked.connect(self.generate_json)

        # Add the grid and input layouts to the main layout
        main_layout = QGridLayout()
        main_layout.addLayout(self.grid_layout, 0, 0)
        main_layout.addLayout(input_layout, 0, 1)

        # Set the main layout for the window
        self.setLayout(main_layout)

    def right_click(self):
        button = self.sender()
        capacity = int(button.text()) + 1
        button.setText(str(capacity))

    def change_color(self):
        button = self.sender()
        color = button.property("color")
        if color == "red":
            button.setProperty("color", "yellow")
            button.setStyleSheet("background-color: yellow")
        elif color == "yellow":
            button.setProperty("color", "green")
            button.setStyleSheet("background-color: green")
        elif color == "green":
            button.setProperty("color", "white")
            button.setStyleSheet("background-color: white")
        elif color == "white":
            button.setProperty("color", "red")
            button.setStyleSheet("background-color: red")
        else:
            button.setProperty("color", "red")
            button.setStyleSheet("background-color: red")

    def generate_json(self):
        print('Pressed generate button')
        for row in range(self.grid_layout.rowCount()):
            for col in range(self.grid_layout.columnCount()):
                button = self.grid_layout.itemAtPosition(row, col).widget()
                button_color = button.property("color")
                # define additional parameters
                tile_type = ''
                capacity = button.text()
                # red = road, yellow = parking, green = gate

                if button_color == 'red':
                    tile_type = 'R'
                elif button_color == 'yellow':
                    tile_type = 'P'
                elif button_color == 'green':
                    tile_type = 'G'
                else:
                    tile_type = 'N'

                # fill matrix with information from GUI
                matrix[row][col] = tile_type

        utils.matrix_to_txt(txt_file_path, matrix)
        # utils.write_json(file_path, entries)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    grid = Grid()
    grid.show()
    sys.exit(app.exec_())
