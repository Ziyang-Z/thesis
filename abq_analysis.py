import numpy as np
import subprocess
import datetime
import numpy
import math
import sys
import os

import excitation as ex

parent_path = os.path.dirname(os.path.abspath('abq_analysis.py'))

youngs_modulus_girder_start = 30.5E9
youngs_modulus_girder_end = 31E9
youngs_modulus_girder_step = 5E8

youngs_modulus_aggregate_start = 40E9
youngs_modulus_aggregate_end = 41E9
youngs_modulus_aggregate_step = 5E8

size_aggregate_start = 0.009
size_aggregate_end = 0.010
size_aggregate_step = 0.001

length_girder_start = 1.4
length_girder_end = 1.5
length_girder_step = 0.05

depth_girder_start = 0.10
depth_girder_end = 0.11
depth_girder_step = 0.05

width_girder_start = 0.10
width_girder_end = 0.11
width_girder_step = 0.05


def specify_parameter_range(start, end, step_size):
    if end < start:
        raise Exception("Endpoint has to be larger or equal to the starting point")
    if step_size <= 0:
        raise Exception("step_size has to be positive")

    parameter_range = list(np.linspace(start, end, math.ceil(((end - start) / step_size) + 1)))
    parameter_range.insert(0, 0)
    return parameter_range


def create_folder(parent_path, folder_name):
    os.chdir(parent_path)
    os.mkdir(os.path.join(parent_path, folder_name))
    parameter_analysis_path = os.path.join(os.path.join(parent_path, folder_name))
    return parameter_analysis_path


if __name__ == "__main__":

    ex.main()

    starttime = datetime.datetime.now()

    parameter_switcher = {
        "youngs_modulus_girder": specify_parameter_range(youngs_modulus_girder_start, youngs_modulus_girder_end,
                                                         youngs_modulus_girder_step),
        "number_of_aggregates": [0, 8],
        "youngs_modulus_aggregate": specify_parameter_range(youngs_modulus_aggregate_start,
                                                            youngs_modulus_aggregate_end,
                                                            youngs_modulus_aggregate_step),
        "position_of_aggregates": [0, 1],
        "size_aggregate": specify_parameter_range(size_aggregate_start, size_aggregate_end, size_aggregate_step),
        "length_girder": specify_parameter_range(length_girder_start, length_girder_end, length_girder_step),
        "depth_girder": specify_parameter_range(depth_girder_start, depth_girder_end, depth_girder_step),
        "width_girder": specify_parameter_range(width_girder_start, width_girder_end, width_girder_step),
        "poissons_ratio_girder": [1, 2],
        "poissons_ratio_aggregate": [1, 2]
    }

    parameter_analysis_path = create_folder(parent_path, 'analysis')
    for value10 in parameter_switcher["poissons_ratio_aggregate"]:
        parameter_analysis_path = create_folder(parameter_analysis_path,
                                                "poissons_ratio_aggregate_" + str(float('%.2g' % value10)))
        for value9 in parameter_switcher["poissons_ratio_girder"]:
            parameter_analysis_path = create_folder(parameter_analysis_path,
                                                    "poissons_ratio_girder_" + str(float('%.2g' % value9)))
            for value8 in parameter_switcher["width_girder"]:
                parameter_analysis_path = create_folder(parameter_analysis_path,
                                                        "width_girder_" + str(float('%.2g' % value8)))
                for value7 in parameter_switcher["depth_girder"]:
                    parameter_analysis_path = create_folder(parameter_analysis_path,
                                                            "depth_girder_" + str(float('%.2g' % value7)))
                    for value6 in parameter_switcher["length_girder"]:
                        parameter_analysis_path = create_folder(parameter_analysis_path,
                                                                "length_girder_" + str(float('%.2g' % value6)))
                        for value5 in parameter_switcher["size_aggregate"]:
                            parameter_analysis_path = create_folder(parameter_analysis_path,
                                                                    "size_aggregate_" + str(float('%.2g' % value5)))
                            for value4 in parameter_switcher["position_of_aggregates"]:
                                parameter_analysis_path = create_folder(parameter_analysis_path,
                                                                        "position_of_aggregates_" + str(float('%.2g' % value4)))
                                for value3 in parameter_switcher["youngs_modulus_aggregate"]:
                                    parameter_analysis_path = create_folder(parameter_analysis_path,
                                                                            "youngs_modulus_aggregate_" + str(float('%.2g' % value3)))
                                    for value2 in parameter_switcher["number_of_aggregates"]:
                                        parameter_analysis_path = create_folder(parameter_analysis_path,
                                                                                "number_of_aggregates_" + str(float('%.2g' % value2)))
                                        coding = 1
                                        for value1 in parameter_switcher["youngs_modulus_girder"]:
                                            coding += 1
                                            value_list = [value1, value2, value3, value4, value5, value6, value7, value8, value9, value10]

                                            os.chdir(parent_path)

                                            subprocess.run(['/prog/abaqus/2020/bin/abaqus', 'cae', 'noGUI=abq_generate_model.py', '--', str(coding),
                                                            parameter_analysis_path, str(value_list)])

                                        for sequence in np.arange(1, len(parameter_switcher["youngs_modulus_girder"])+1, 3):
                                            os.chdir(parameter_analysis_path)
                                            subprocess.run('/prog/abaqus/2020/bin/abaqus interactive job=Job-'+str(sequence)+'.inp cpus=3 domains=3 mp_mode=threads parallel=domain double=explicit '
                                                           '& /prog/abaqus/2020/bin/abaqus interactive job=Job-'+str(sequence+1)+'.inp cpus=3 domains=3 mp_mode=threads parallel=domain double=explicit '
                                                           '& /prog/abaqus/2020/bin/abaqus interactive job=Job-'+str(sequence+2)+'.inp cpus=3 domains=3 mp_mode=threads parallel=domain double=explicit',
                                                            shell=True, check=True)
                                            if exit(1):
                                                subprocess.run('/prog/abaqus/2020/bin/abaqus interactive restart job='+str(sequence)+'.inp step=Step-1 cpus=3 domains=3 mp_mode=threads parallel=domain double=explicit '
                                                               '& /prog/abaqus/2020/bin/abaqus interactive restart job='+str(sequence+1)+'.inp step=Step-1 cpus=3 domains=3 mp_mode=threads parallel=domain double=explicit '
                                                               '& /prog/abaqus/2020/bin/abaqus interactive restart job='+str(sequence+2)+'.inp step=Step-1 cpus=3 domains=3 mp_mode=threads parallel=domain double=explicit ',
                                                                shell=True, check=True)
                                                # if error occurred, the simulations will stop, with restart-job we can restart the job from end of the step.

                                        for sequence1 in np.arange(1, len(parameter_switcher["youngs_modulus_girder"])+1, 1):
                                            os.chdir(parent_path)
                                            subprocess.run(['/prog/abaqus/2020/bin/abaqus', 'cae', 'noGUI=abq_result_export.py', '--',
                                                            str(sequence1), parameter_analysis_path])

    endtime = datetime.datetime.now()
    print('runtime =', endtime - starttime)