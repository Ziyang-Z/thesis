import numpy as np
import math

mesh_size_girder = 0.01
width_girder = 0.10
length_girder = 1.45

force_position = 0.48
window = 7

all_nodes = False


def double_line_node_list():
    d = (width_girder/mesh_size_girder + 1)**2
    a1 = 1 + (width_girder/mesh_size_girder + 1)*(width_girder/mesh_size_girder//4+1)
    n = length_girder/mesh_size_girder + 1
    an = a1 + (n - 1)*d
    # m = int(length_girder/mesh_size_girder//100)
    nodes_left = np.arange(int(a1), int(an+1), int(d))
    nodes_left = nodes_left[::-1]

    a1 = 1 + (width_girder/mesh_size_girder + 1)*(width_girder/mesh_size_girder//4 * 3+1)
    n = length_girder/mesh_size_girder + 1
    an = a1 + (n - 1)*d
    # m = int(length_girder/mesh_size_girder//100)
    nodes_right = np.arange(int(a1), int(an+1), int(d))
    nodes_right = nodes_right[::-1]
    return nodes_left, nodes_right


def choose_node():
    slice_list = np.linspace(start, end, math.ceil(((end - start) / step_size) + 1))
    slice_list = list(map(int, list(map(lambda x: x/mesh_size_girder, slice_list))))

    nodes_left, nodes_right = double_line_node_list()

    node_list = []
    for i in slice_list:
        node_list.append(nodes_left[i])
    for j in slice_list:
        node_list.append(nodes_right[j])

    print(len(node_list))

    return node_list


def line_node_list():
    d = (width_girder/mesh_size_girder + 1)**2
    a1 = 1 + (width_girder/mesh_size_girder + 1)*(width_girder/mesh_size_girder/2)
    n = length_girder/mesh_size_girder + 1
    an = a1 + (n - 1)*d
    nodes = np.arange(int(a1), int(an+1), int(d))
    nodes = nodes[::-1]
    return nodes


def set_force_node():
    node_array = line_node_list()
    force_node_position = int(force_position*(1/mesh_size_girder))
    force_node = node_array[force_node_position]
    return force_node


def main():

    force_node_position = int(force_position*(1/mesh_size_girder))

    if all_nodes:
        num = line_node_list()
    else:
        num = line_node_list()
        num1 = num[force_node_position-window:force_node_position+window+1]
        num2 = num[-15:]
        num = np.concatenate((num1, num2))

    return num


start = 0.05
end = 1.45
step_size = 0.1

