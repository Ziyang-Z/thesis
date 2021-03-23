import numpy as np
import random
import math
import sys
import os

radius_gravel_max = 0.008
length_girder_default = 1.45
width_girder_default = 0.1
depth_girder_default = 0.1


class Gird:
    def __init__(self, radius_gravel, length_girder, width_girder, depth_girder):
        self.length_girder = length_girder
        self.width_girder = width_girder
        self.depth_girder = depth_girder
        self.radius_gravel = radius_gravel
        self.grid_right_limit_length = self.length_girder - 1.5*self.radius_gravel + 0.0001
        self.grid_right_limit_width = self.width_girder - 1.5*self.radius_gravel + 0.0001
        self.grid_right_limit_depth = self.depth_girder - 1.5*self.radius_gravel + 0.0001
        self.grid_left_limit_length = 1.5*self.radius_gravel
        self.grid_left_limit_width = 1.5*self.radius_gravel
        self.grid_left_limit_depth = 1.5*self.radius_gravel
        self.delta_x = 3 * self.radius_gravel
        self.delta_y = 3 * self.radius_gravel
        self.delta_z = 3 * self.radius_gravel
        self.num_aggregate_each_piece = ((self.grid_right_limit_width-self.grid_left_limit_width)//self.delta_y + 1)**2
        # self.noise_radius = self.radius_gravel
        # self.noise_radius_Horizontal = (self.delta_x//self.radius_gravel/2)*self.noise_radius

    # def generate_random_grid(self):
    #     grid_list = []
    #     x = [round(i, 2) for i in np.arange(self.grid_left_limit_length, self.grid_right_limit_length, self.delta_x)]
    #     y = [round(i, 2) for i in np.arange(self.grid_left_limit_width, self.grid_right_limit_width, self.delta_y)]
    #     z = [round(i, 2) for i in np.arange(self.grid_left_limit_depth, self.grid_right_limit_depth, self.delta_z)]
    #     for x_point in x:
    #         for y_point in y:
    #             for z_point in z:
    #                 dx = random.uniform(x_point - self.noise_radius, x_point + self.noise_radius_Horizontal)
    #                 dy = random.uniform(y_point - self.noise_radius, y_point + self.noise_radius)
    #                 dz = random.uniform(z_point - self.noise_radius, z_point + self.noise_radius)
    #                 grid_list.append((dx, dy, dz))
    #     return grid_list

    def generate_evenly_grid(self):
        grid_list = []
        x = [round(i, 2) for i in np.arange(self.grid_left_limit_length, self.grid_right_limit_length, self.delta_x)]
        y = [round(i, 2) for i in np.arange(self.grid_left_limit_width, self.grid_right_limit_width, self.delta_y)]
        z = [round(i, 2) for i in np.arange(self.grid_left_limit_depth, self.grid_right_limit_depth, self.delta_z)]
        for x_point in x:
            for y_point in y:
                for z_point in z:
                    grid_list.append((x_point, y_point, z_point))
        return grid_list


def random_grid(number):
    grid = Gird(radius_gravel_max, length_girder_default, width_girder_default, depth_girder_default)
    grid_list = grid.generate_evenly_grid()
    slice_list = np.arange(0, len(grid_list), 1)
    np.random.seed(0)
    chosen_grid_slice = np.random.choice(slice_list, number, replace=False)
    chosen_grid_slice.sort()

    chosen_grid = []
    for item in chosen_grid_slice:
        grid_item = grid_list[item]
        chosen_grid.append(grid_item)
    return chosen_grid


def evenly_grid(number):
    grid = Gird(radius_gravel_max, length_girder_default, width_girder_default, depth_girder_default)
    grid_list = grid.generate_evenly_grid()
    num_aggregate_each_piece = grid.num_aggregate_each_piece
    piece_number = int(len(grid_list)/int(num_aggregate_each_piece))

    node_each_piece_array = []
    for i in np.arange(0, len(grid_list), int(num_aggregate_each_piece)):
        node_each_piece = grid_list[i:int(i+num_aggregate_each_piece)]
        node_each_piece_array.append(node_each_piece)
    chosen_node_slice = list(map(int, np.linspace(0, int(num_aggregate_each_piece) - 1, int(number/piece_number))))

    chosen_grid = []
    for item in node_each_piece_array:
        for slice in chosen_node_slice:
            grid_item = item[slice]
            chosen_grid.append(grid_item)