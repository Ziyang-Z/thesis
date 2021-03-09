import numpy as np

mesh_size_girder = 0.01
width_girder = 0.10
length_girder = 1.45

force_position = 0.48
window = 7

all_nodes = True


def line_node_list():
    d = (width_girder/mesh_size_girder + 1)**2
    a1 = 1 + (width_girder/mesh_size_girder + 1)*(width_girder/mesh_size_girder/2)
    n = length_girder/mesh_size_girder + 1
    an = a1 + (n - 1)*d
    m = int(length_girder/mesh_size_girder//100)        # output required on 100 points, or near to 100 points
    nodes = np.arange(int(a1), int(an+1), int(m*d))
    nodes = nodes[::-1]
    D = len(nodes)
    print(D)
    return nodes


def set_force_node():
    node_array = line_node_list()
    force_node_position = int(force_position*(1/mesh_size_girder))
    print(force_node_position)
    force_node = node_array[force_node_position]
    print(force_node)
    return force_node


def main():
    node_array = line_node_list()
    force_node_position = int(force_position*(1/mesh_size_girder))
    print(force_node_position)
    force_node = node_array[force_node_position]
    print(force_node)

    if all_nodes:
        num = line_node_list()
    else:
        num = line_node_list()
        num1 = num[force_node_position-window:force_node_position+window+1]
        num2 = num[-15:]
        num = np.concatenate((num1, num2))
        print(len(num))

    return num

