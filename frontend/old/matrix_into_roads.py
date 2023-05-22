import json
import utils

# matrix = [
#    ["R", "R", "R", "R", "R"],
#    ["R", "N", "R", "N", "R"],
#    ["R", "R", "R", "R", "R"],
#    ["R", "N", "R", "N", "R"],
#    ["R", "R", "R", "R", "R"]
# ]

# 0,0 - 0,4 = top horizontal road
# 0,0 - 4,0 = left vertical road
matrix = [
    ["G", "N", "P", "N", "G"],
    ["R", "R", "R", "R", "R"],
    ["R", "N", "N", "N", "R"],
    ["R", "P", "N", "N", "R"],
    ["R", "N", "N", "N", "R"]
]

matrix2 = [
    ["R", "R", "R", "R", "R", "R"],
    ["R", "P", "R", "P", "N", "R"],
    ["R", "N", "N", "N", "N", "R"],
    ["R", "N", "P", "N", "N", "R"],
    ["R", "N", "R", "N", "N", "R"],
    ["R", "R", "R", "R", "R", "R"]
]

# Assumption, that a gate can only be placed in the top-most row
# A gate can be connected to more than one road

matrix3 = [
    ["G", "R", "R", "R", "R", "R"],
    ["R", "P", "R", "P", "N", "R"],
    ["R", "N", "N", "N", "N", "R"],
    ["R", "N", "P", "N", "N", "R"],
    ["R", "N", "R", "N", "N", "R"],
    ["R", "R", "R", "R", "R", "R"]
]


# check all horizontal tiles
# then check all vertical tiles

def matrix_to_roads_horizontal():
    roads = []

    row_count = len(matrix)
    col_count = len(matrix[0])

    # check all horizontal tiles
    for x in range(0, row_count):

        curr_road_list = []

        for y in range(0, col_count):

            if matrix[x][y] == "R":
                curr_road_list.append(f"{x},{y}")

                if y == col_count - 1 or matrix[x][y + 1] != "R":
                    if len(curr_road_list) > 1:
                        roads.append(curr_road_list)
                        # print(f'Road finished: {curr_road_list}')
                    curr_road_list = []

    return roads


def matrix_to_roads_vertical():
    roads = []

    row_count = len(matrix)
    col_count = len(matrix[0])

    # check all horizontal tiles
    for y in range(0, row_count):

        curr_road_list = []

        for x in range(0, col_count):

            if matrix[x][y] == "R":
                curr_road_list.append(f"{x},{y}")

                if x == row_count - 1 or matrix[x + 1][y] != "R":
                    if len(curr_road_list) > 1:
                        roads.append(curr_road_list)
                        # print(f'Road finished: {curr_road_list}')
                    curr_road_list = []

    return roads


def roads_to_continuous(type_roads):
    horiz_roads = []
    for coord_list in type_roads:
        start_coords = coord_list[0]
        end_coords = coord_list[len(coord_list) - 1]
        horiz_roads.append((start_coords, end_coords))
    return horiz_roads


def convert_roads_to_json(hor_roads, ver_roads, type):
    roads = []

    if type == "h" or type == "hv":

        for road in hor_roads:
            counter = 0
            roads.append(
                {
                    "node_id": counter,
                    "type": "road",
                    "capacity": 10,
                    "allowed_veh": [
                        "cars",
                        "trucks"
                    ],
                    "start_pos": {
                        "x": int(road[0][0]),
                        "y": int(road[0][2])
                    },
                    "end_pos": {
                        "x": int(road[1][0]),
                        "y": int(road[1][2])
                    },
                    "connectsTo": [
                    ]
                })
            counter += 1

    if type == "v" or type == "hv":
        for road in ver_roads:
            counter = 0
            roads.append(
                {
                    "node_id": counter,
                    "type": "road",
                    "capacity": 10,
                    "allowed_veh": [
                        "cars",
                        "trucks"
                    ],
                    "start_pos": {
                        "x": int(road[0][0]),
                        "y": int(road[0][2])
                    },
                    "end_pos": {
                        "x": int(road[1][0]),
                        "y": int(road[1][2])
                    },
                    "connectsTo": [
                    ]
                })
            counter += 1

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(roads, f, ensure_ascii=False, indent=4)
    return roads


def index_all_tiles(roads, start_index=0):
    current_id = start_index
    for entry in roads:
        entry['node_id'] = current_id
        current_id += 1


# check if two roads overlap
def get_road_overlap():
    overlap_info = []

    for hor_road in hor_roads_json:
        for ver_road in ver_roads_json:
            # check for coordinates
            start1 = [hor_road['start_pos']['x'], hor_road['start_pos']['y']]
            end1 = [hor_road['end_pos']['x'], hor_road['end_pos']['y']]
            start2 = [ver_road['start_pos']['x'], ver_road['start_pos']['y']]
            end2 = [ver_road['end_pos']['x'], ver_road['end_pos']['y']]

            # Find the overlapping coordinates
            x_overlap_start = max(start1[0], start2[0])
            x_overlap_end = min(end1[0], end2[0])
            y_overlap_start = max(start1[1], start2[1])
            y_overlap_end = min(end1[1], end2[1])

            # Check if there is a valid overlap
            if x_overlap_start <= x_overlap_end and y_overlap_start <= y_overlap_end:
                overlapping_points = []

                for x in range(x_overlap_start, x_overlap_end + 1):
                    for y in range(y_overlap_start, y_overlap_end + 1):
                        overlapping_points.append((x, y))

                # Print the overlapping ranges and coordinates
                # print(
                #    f"{start1}-{end1} and {start2}-{end2} "
                #    f"overlap in {overlapping_points[-1]}"
                # )

                # Store the overlapping coordinates separately for each range
                overlap_info.append({
                    'range_A': (start1, end1),
                    'range_B': (start2, end2),
                    'overlapping_coordinates': overlapping_points
                })

    if overlap_info:
        return overlap_info

    # No overlap
    return None


def update_road_connections():
    try:
        for overlap_info in road_overlap_info:
            # assign vars
            r_one_x_start = overlap_info['range_A'][0][0]
            r_one_y_start = overlap_info['range_A'][0][1]
            r_one_x_end = overlap_info['range_A'][1][0]
            r_one_y_end = overlap_info['range_A'][1][1]

            r_two_x_start = overlap_info['range_B'][0][0]
            r_two_y_start = overlap_info['range_B'][0][1]
            r_two_x_end = overlap_info['range_B'][1][0]
            r_two_y_end = overlap_info['range_B'][1][1]

            road_ids_to_connect = []

            print(f'Road one from: {r_one_x_start},{r_one_y_start} - {r_one_x_end},{r_one_y_end}')
            print(f'Road two from: {r_two_x_start},{r_two_y_start} - {r_two_x_end},{r_two_y_end}')

            # find ids of roads one and two
            for road in all_roads_json:
                if road['start_pos']['x'] == r_one_x_start and road['start_pos']['y'] == r_one_y_start and \
                        road['end_pos'][
                            'x'] == r_one_x_end and road['end_pos']['y'] == r_one_y_end:
                    print(f'Road one id: {road["node_id"]}')
                    road_ids_to_connect.append(road["node_id"])

                if road['start_pos']['x'] == r_two_x_start and road['start_pos']['y'] == r_two_y_start and \
                        road['end_pos'][
                            'x'] == r_two_x_end and road['end_pos']['y'] == r_two_y_end:
                    print(f'Road two id: {road["node_id"]}')
                    road_ids_to_connect.append(road["node_id"])

            # update connection info for roads
            print(road_ids_to_connect)

            for road in all_roads_json:
                # look for the first id and connect the second id
                if road["node_id"] == road_ids_to_connect[0]:
                    road["connectsTo"].append((road_ids_to_connect[1], 0))

                if road["node_id"] == road_ids_to_connect[1]:
                    road["connectsTo"].append((road_ids_to_connect[0], 0))

            print()

            # print(overlap_info['range_A'][0][0], overlap_info['range_A'][0][1])
    except:
        print("No overlapping.")


def is_coordinate_in_range(coordinate, range_start, range_end):
    # 0, 1
    x, y = coordinate
    # 0, 0
    range_start_x, range_start_y = range_start
    # 4, 0
    range_end_x, range_end_y = range_end

    # Check if the coordinate is within the range
    if range_start_x <= x <= range_end_x and range_start_y <= y <= range_end_y:
        return True

    return False


def convert_parking_to_json():
    counter = len(all_roads_json)
    parking_lots = []
    # print("Adding parking lots...")
    for row in range(0, len(matrix)):
        for col in range(0, len(matrix[0])):
            if matrix[row][col] == 'P':
                print(f"Parking at: {(row, col)}")
                parking_lots.append((row, col))

    # check if there is a road on the right or the left of the parking lot
    for parking in parking_lots:
        # check coordinates around parking lot (left, right, top, bottom)
        print()
        x_park = parking[0]
        y_park = parking[1]

        # check the parking lot against all roads, connect with the first one that can be found
        for road in all_roads_json:
            road_id = road['node_id']
            road_start_coords = (road['start_pos']['x'], road['start_pos']['y'])
            road_end_coords = (road['end_pos']['x'], road['end_pos']['y'])
            print(road_start_coords, road_end_coords)

            try:
                parking_coords = (x_park, y_park)
                print(f'Checking P{parking_coords} with R{road_start_coords} - R{road_end_coords}')

                # left
                parking_coords = (x_park, y_park - 1)
                if is_coordinate_in_range(parking_coords, road_start_coords, road_end_coords):
                    # add parking lot with connection to json variable
                    all_roads_json.append(
                        {
                            "node_id": counter,
                            "type": "parking",
                            "capacity": 10,
                            "allowed_veh": [
                                "cars",
                                "trucks"
                            ],
                            "start_pos": {
                                "x": parking_coords[0],
                                "y": parking_coords[1] + 1
                            },
                            "end_pos": {
                                "x": parking_coords[0],
                                "y": parking_coords[1] + 1
                            },
                            "connectsTo": [
                                [road_id, 0]
                            ]
                        })
                    counter = len(all_roads_json)
                    print("Adding parking ...")
                    print()
                    break

                # right
                parking_coords = (x_park, y_park + 1)
                if is_coordinate_in_range(parking_coords, road_start_coords, road_end_coords):
                    # add parking lot with connection to json variable
                    all_roads_json.append(
                        {
                            "node_id": counter,
                            "type": "parking",
                            "capacity": 10,
                            "allowed_veh": [
                                "cars",
                                "trucks"
                            ],
                            "start_pos": {
                                "x": parking_coords[0],
                                "y": parking_coords[1] - 1
                            },
                            "end_pos": {
                                "x": parking_coords[0],
                                "y": parking_coords[1] - 1
                            },
                            "connectsTo": [
                                [road_id, 0]
                            ]
                        })
                    counter = len(all_roads_json)
                    print("Adding parking ...")
                    print()
                    break

                # top
                parking_coords = (x_park - 1, y_park)
                if is_coordinate_in_range(parking_coords, road_start_coords, road_end_coords):
                    # add parking lot with connection to json variable
                    all_roads_json.append(
                        {
                            "node_id": counter,
                            "type": "parking",
                            "capacity": 10,
                            "allowed_veh": [
                                "cars",
                                "trucks"
                            ],
                            "start_pos": {
                                "x": parking_coords[0] + 1,
                                "y": parking_coords[1]
                            },
                            "end_pos": {
                                "x": parking_coords[0] + 1,
                                "y": parking_coords[1]
                            },
                            "connectsTo": [
                                [road_id, 0]
                            ]
                        })
                    counter = len(all_roads_json)
                    print("Adding parking ...")
                    print()
                    break

                # bottom
                parking_coords = (x_park + 1, y_park)
                if is_coordinate_in_range(parking_coords, road_start_coords, road_end_coords):
                    # add parking lot with connection to json variable
                    all_roads_json.append(
                        {
                            "node_id": counter,
                            "type": "parking",
                            "capacity": 10,
                            "allowed_veh": [
                                "cars",
                                "trucks"
                            ],
                            "start_pos": {
                                "x": parking_coords[0] - 1,
                                "y": parking_coords[1]
                            },
                            "end_pos": {
                                "x": parking_coords[0] - 1,
                                "y": parking_coords[1]
                            },
                            "connectsTo": [
                                [road_id, 0]
                            ]
                        })
                    counter = len(all_roads_json)
                    print("Adding parking ...")
                    print()
                    break
            except:
                print("Range error")


def convert_checkin_to_json():
    # check-in gates can only connect downwards
    counter = len(all_roads_json)
    print("Processing check-in gates")
    gates = []

    for row in range(0, len(matrix)):
        for col in range(0, len(matrix[0])):
            if matrix[row][col] == 'G':
                print(f"Parking at: {(row, col)}")
                gates.append((row, col))

    for gate in gates:
        # check coordinates around parking lot (left, right, top, bottom)
        print()
        x_park = gate[0]
        y_park = gate[1]
        gate_connect_to_road_id = []

        for road in all_roads_json:
            road_id = road['node_id']
            road_start_coords = (road['start_pos']['x'], road['start_pos']['y'])
            road_end_coords = (road['end_pos']['x'], road['end_pos']['y'])
            print(road_start_coords, road_end_coords)

            parking_coords = (x_park, y_park)
            print(f'Checking G{parking_coords} with R{road_start_coords} - R{road_end_coords}')

            # bottom
            parking_coords = (x_park + 1, y_park)
            if is_coordinate_in_range(parking_coords, road_start_coords, road_end_coords):
                # add id of road connections to temporary list
                gate_connect_to_road_id.append([road_id, 0])
                counter = len(all_roads_json)

        if len(gate_connect_to_road_id) > 0:
            # check if there is at least one connection to a road
            # save gate information including all road connections to json
            all_roads_json.append(
                {
                    "node_id": counter,
                    "type": "gate",
                    "capacity": 0,
                    "allowed_veh": [
                        "cars",
                        "trucks"
                    ],
                    "start_pos": {
                        "x": parking_coords[0] - 1,
                        "y": parking_coords[1]
                    },
                    "end_pos": {
                        "x": parking_coords[0] - 1,
                        "y": parking_coords[1]
                    },
                    "connectsTo": gate_connect_to_road_id
                })
            print("Adding gate ...")
            print()

    print(gates)


# read matrix from file
matrix_file_path = "grid_layout.txt"
matrix_temp = utils.matrix_from_txt(matrix_file_path)
# bring matrix into the correct format
matrix = matrix_temp.reshape(5, 5)

# start the process of converting the matrix to a json
horizontal_roads = matrix_to_roads_horizontal()
vertical_roads = matrix_to_roads_vertical()

# connect all horizontal and vertical roads in two steps
horizontal_roads_cont = roads_to_continuous(horizontal_roads)
vertical_roads_cont = roads_to_continuous(vertical_roads)

# first add the vertical roads, then the horizontal
ver_roads_json = convert_roads_to_json(horizontal_roads_cont, vertical_roads_cont, "v")
hor_roads_json = convert_roads_to_json(horizontal_roads_cont, vertical_roads_cont, "h")

# update all indices of roads
index_all_tiles(hor_roads_json)
index_all_tiles(ver_roads_json, len(hor_roads_json))

# get road overlap info
road_overlap_info = get_road_overlap()

# combine horizontal and vertical roads
all_roads_json = hor_roads_json + ver_roads_json

# update road connections
update_road_connections()
utils.write_json('data.json', all_roads_json)

# connect parking lots to adjacent roads
convert_parking_to_json()
utils.write_json('data.json', all_roads_json)

# connect check-in gates to adjacent road
convert_checkin_to_json()
utils.write_json('data.json', all_roads_json)
###
