def is_coordinate_in_range(coordinate, range_start, range_end):
    # 0, 1
    x, y = coordinate
    # 0, 0
    range_start_x, range_start_y = range_start
    # 4, 0
    range_end_x, range_end_y = range_end

    # Check if the coordinate is within the range (positive direction)
    if range_start_x <= x <= range_end_x and range_start_y <= y <= range_end_y:
        return True

    # Check if the coordinate is within the range (negative direction)
    if range_start_x >= x >= range_end_x and range_start_y >= y >= range_end_y:
        return True

    return False


def update_connection_between_areas(data_list, filter_value, new_connection_value):
    filtered_list = [item for item in data_list if item.get('node_id') == filter_value]
    for item in filtered_list:
        item['connectsTo'].append([new_connection_value, 0])
    return filtered_list
