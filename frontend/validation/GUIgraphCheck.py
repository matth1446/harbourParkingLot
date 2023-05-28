from turtle import goto

import numpy as np


# This function is used just to get the adiacent cells for each cell.
# It returns the cells to the left, right, above and down
def getAdiacentCells(matrix, i, j, nrows, ncols):
    adiacents = []
    if j - 1 >= 0:
        adiacents.append(matrix[i, j - 1])
    if j + 1 < ncols:
        adiacents.append(matrix[i, j + 1])
    if i - 1 >= 0:
        adiacents.append(matrix[i - 1, j])
    if i + 1 < nrows:
        adiacents.append(matrix[i + 1, j])
    # if i + 1 < nrows and j + 1 < ncols:
    #   adiacents.append(matrix[i + 1, j + 1])
    # if i - 1 >= 0 and j - 1 >= 0:
    #     adiacents.append(matrix[i - 1, j - 1])
    # if i - 1 >= 0 and j + 1 < ncols:
    #    adiacents.append(matrix[i - 1, j + 1])
    # if i + 1 < nrows and j - 1 >= 0:
    #    adiacents.append(matrix[i + 1, j - 1])
    return adiacents


# This function checks if the roads make together one single connected component.
def count_connected_components(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    visited = [[False] * cols for _ in range(rows)]
    count = 0

    def dfs(row, col):
        if (
                row < 0
                or row >= rows
                or col < 0
                or col >= cols
                or visited[row][col]
                or matrix[row][col] != 'R'
        ):
            return

        visited[row][col] = True

        dfs(row - 1, col)
        dfs(row + 1, col)
        dfs(row, col - 1)
        dfs(row, col + 1)

    for i in range(rows):
        for j in range(cols):
            if matrix[i][j] == 'R' and not visited[i][j]:
                dfs(i, j)
                count += 1
    return count


# This function checks if the layout has at least one entry, and if it's connected to at least one road.
def check_hasConnectedEntry(parkingArray, nrows, ncols):
    if parkingArray.tolist().count('E') == 0:
        return False
    map = np.matrix(parkingArray.reshape(nrows, ncols))
    for i in range(nrows):
        for j in range(ncols):
            if map[i, j] == 'E':
                # Entries are allowed only on bottom of the map.
                if i != (nrows - 1):
                    return False
                adiacents = getAdiacentCells(map, i, j, nrows, ncols)
                if adiacents.count('R') + adiacents.count('P') + adiacents.count('G') + adiacents.count('E') >= 1:
                    return True
    return False


# This function checks if the layout has at least one check in gate, and if it's connected to at least one road.
def check_hasConnectedCheckInGate(parkingArray, nrows, ncols):
    if parkingArray.tolist().count('G') == 0:
        return False
    map = np.matrix(parkingArray.reshape(nrows, ncols))
    for i in range(nrows):
        for j in range(ncols):
            if map[i, j] == 'G':
                # Gates are allowed only on top of the map.
                if i != 0:
                    return False

                adiacents = getAdiacentCells(map, i, j, nrows, ncols)
                if adiacents.count('R') + adiacents.count('P') + adiacents.count('G') + adiacents.count('E') >= 1:
                    return True
    return False
    pass


# This function checks if the layout has all the parking lots connected to at least one road.
def check_hasParkingLotsConnectedToRoads(parkingArray, nrows, ncols):
    if parkingArray.tolist().count('P') == 0:
        return True
    map = np.matrix(parkingArray.reshape(nrows, ncols))
    for i in range(nrows):
        for j in range(ncols):
            if map[i, j] == 'P':
                adiacents = getAdiacentCells(map, i, j, nrows, ncols)
                if adiacents.count('R') + adiacents.count('P') < 1:
                    return False
    return True


# It prints the coloured layout in a matrix form, just for debugging purposes.
def print_colored_matrix(matrix):
    colors = {'R': '\033[0m', 'G': '\033[91m', 'E': '\033[92m', 'P': '\033[94m', 'N': '\033[37m'}
    for row in matrix:
        for elem in row:
            c = colors.get(elem, '\033[0m')
            if elem != 'N':
                print(c + elem, end=' ')
            else:
                print(c + '*', end=' ')
        print()


# This is the actual function to check if a layout given in a matrix form is valid or not, according to various checks.
# It return True if the layout is valid, False otherwise.
def isLayoutValid(sequence):
    map_list = sequence.split(",")
    map_array = np.array(map_list)
    nrows, ncols = int(np.sqrt(len(map_array))), int(np.sqrt(len(map_array)))
    map_matrix = np.matrix(map_array.reshape(nrows, ncols))
    print_colored_matrix(map_array.reshape(nrows, ncols))
    roadsConnected = count_connected_components(map_array.reshape(nrows, ncols))
    entriesConnected = check_hasConnectedEntry(map_array, nrows, ncols)
    checkInGatesConnected = check_hasConnectedCheckInGate(map_array, nrows, ncols)
    parkingsConnected = check_hasParkingLotsConnectedToRoads(map_array, nrows, ncols)
    roadSingleComponent = (roadsConnected == 1)
    isValid = roadSingleComponent and entriesConnected and checkInGatesConnected and parkingsConnected
    print('\nIs layout valid? ' + str(isValid))
    print('\nRoads are connected? ' + str(roadSingleComponent))
    print('Entries are connected and on bottom of the layout? ' + str(entriesConnected))
    print('Check In Gates are connected and on top of the layout? ' + str(checkInGatesConnected))
    print('Parkings are connected? ' + str(parkingsConnected))
    return isValid


# Example layout.
sequence = "N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,N,R,R,R,R,N,N,N,N,N,N,R,N,N,R,N,N,N,N,N,N,R,N,N,R,N,N,N,N,N,N,E,N,N,G,N,N,N,N,N"

# Actual check of the given layout.
isLayoutValid(sequence)
