import numpy as np
import subprocess
import datetime
import numpy
import math
import sys
import os

import excitation as ex


youngs_modulus_aggregate_start = 40E9
youngs_modulus_aggregate_end = 42E9
youngs_modulus_aggregate_step = 5E8

youngs_modulus_girder_start = 29E9
youngs_modulus_girder_end = 32E9
youngs_modulus_girder_step = 5E8

mesh_size_aggregate_start = 0.002
mesh_size_aggregate_end = 0.008
mesh_size_aggregate_step = 0.002

size_aggregate_start = 0.005
size_aggregate_end = 0.010
size_aggregate_step = 0.001


def specify_parameter_range(start, end, step_size):
    if end < start:
        raise Exception("Endpoint has to be larger or equal to the starting point")
    if step_size <= 0:
        raise Exception("step_size has to be positive")

    parameter_range = list(np.linspace(start, end, math.ceil(((end - start) / step_size) + 1)))
    return parameter_range


if __name__ == "__main__":

    ex.main()

    starttime = datetime.datetime.now()

    # analysis of concrete only = False, analysis of concrete with aggregates = True
    aggregates_insert = True

    parameter_switcher = {
        "youngs_modulus_aggregate": specify_parameter_range(youngs_modulus_aggregate_start, youngs_modulus_aggregate_end, youngs_modulus_aggregate_step),
        "youngs_modulus_girder": specify_parameter_range(youngs_modulus_girder_start, youngs_modulus_girder_end, youngs_modulus_girder_step),
        "mesh_size_aggregate": specify_parameter_range(mesh_size_aggregate_start, mesh_size_aggregate_end, mesh_size_aggregate_step),
        "size_aggregate": specify_parameter_range(size_aggregate_start, size_aggregate_end, size_aggregate_step)

        # "length_girder": specify_parameter_range(length_girder_start, length_girder_end, length_girder_step),
        # "width_girder": specify_parameter_range(width_girder_start, width_girder_end, width_girder_step),
        # "depth_girder": specify_parameter_range(depth_girder_start, depth_girder_end, depth_girder_step)
    }

    # print("which parameter you want to analyze.")
    # key_parameter = "mesh_size_aggregate"
    # print(key_parameter)
    for key_parameter in list(parameter_switcher.keys()):
        print(key_parameter)
        for value in parameter_switcher[key_parameter]:
            subprocess.run(['/prog/abaqus/2020/bin/abaqus', 'cae', 'noGUI=abq_generate_model.py', '--', str(aggregates_insert), key_parameter, str(parameter_switcher[key_parameter])])

            path_code = os.getcwd()
            os.chdir(path_code + '/' + str(key_parameter) + '-' + str(value))
            subprocess.run('/prog/abaqus/2020/bin/abaqus interactive job=Analysis.inp mp_mode=threads parallel=domain double=explicit cpus=32 domains=32',
                           shell=True, check=True)
        subprocess.run(['/prog/abaqus/2020/bin/abaqus', 'cae', 'noGUI=abq_result_export.py', '--', key_parameter, str(parameter_switcher[key_parameter])])

    endtime = datetime.datetime.now()
    print('runtime =', endtime - starttime)