import json
import numpy as np


def write_layout_to_json(file_path, entries):
    with open(file_path, 'w') as json_file:
        json.dump(entries, json_file,
                  indent=4,
                  separators=(',', ': '))


def write_content_to_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)


def matrix_to_txt(file_path, content):
    row_str = ""
    arr = np.array(content)
    print(arr)

    np.ndarray.tofile(arr, file_path, sep=",", format="%s")

    # # Write the array to file
    # with open(file_path, 'w') as file:
    #     row_count = arr.shape[0]
    #     counter = 0
    #     for row in arr:
    #         if counter < row_count - 1:
    #             file.write(str(row.tolist()) + ',\n')
    #         else:
    #             file.write(str(row.tolist()))
    #         counter += 1


def matrix_from_txt(file_path):
    # Read the text file into a 2D NumPy array
    # arr = np.genfromtxt(file_path, delimiter=',', dtype=str)
    arr = np.loadtxt(file_path, delimiter=",", dtype=str)

    # Print the array
    print(arr)
    return arr
