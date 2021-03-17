import numpy as np
import subprocess
import datetime
import numpy
import math
import sys
import os

import excitation as ex

parent_path = os.path.dirname(os.path.abspath('abq_analysis.py'))

size_aggregate_start = 0.005
size_aggregate_end = 0.009
size_aggregate_step = 0.001

number_of_aggregates_start = 100
number_of_aggregates_end = 500
number_of_aggregates_step = 100


def specify_parameter_range(start, end, step_size):
    if end < start:
        raise Exception("Endpoint has to be larger or equal to the starting point")
    if step_size <= 0:
        raise Exception("step_size has to be positive")

    parameter_range = list(np.linspace(start, end, math.ceil(((end - start) / step_size) + 1)))
    parameter_range.insert(0, 0)
    return parameter_range


def create_folder(parent_path, folder_name):
    os.mkdir(os.path.join(parent_path, folder_name))
    parameter_analysis_path = os.path.join(parent_path, folder_name)
    return parameter_analysis_path


def text_create(path_name, msg):
    location_path = os.getcwd()
    file = open(os.path.join(location_path, path_name), 'w')
    file.write(msg)
    file.close()


def check_default_parameters(parameters, default_parameters):
    parameters_key = parameters.keys()
    for key in parameters_key:
        if parameters[key] == 0:
            parameters[key] = default_parameters[key]
    return parameters


if __name__ == "__main__":

    ex.main()

    starttime = datetime.datetime.now()

    parameter_switcher = {
        "youngs_modulus_girder": [0],
        "number_of_aggregates": specify_parameter_range(number_of_aggregates_start,
                                                        number_of_aggregates_end,
                                                        number_of_aggregates_step),
        "youngs_modulus_aggregate": [0],
        "position_of_aggregates": [0, 0.005],
        "size_aggregate": specify_parameter_range(size_aggregate_start, size_aggregate_end, size_aggregate_step),
        "length_girder": [0],
        "depth_girder": [0],
        "width_girder": [0],
        "poissons_ratio_girder": [0],
        "poissons_ratio_aggregate": [0]
    }
    default_parameters = {"youngs_modulus_girder": 3E10,
                          'number_of_aggregates': 0,
                          "youngs_modulus_aggregate": 5E10,
                          "size_aggregate": 0.005,
                          'position_of_aggregates': 0,
                          "length_girder": 1.45,
                          "depth_girder": 0.10,
                          "width_girder": 0.10,
                          "poissons_ratio_girder": 0.20,
                          "poissons_ratio_aggregate": 0.30}

    os.chdir(parent_path)
    total_folder_path = create_folder(parent_path, 'analysis')
    for size_aggregate in parameter_switcher["size_aggregate"]:
        first_level_subfolder_path = create_folder(total_folder_path,
                                                   "size_a_" + str(float('%.2g' % size_aggregate)))
        for position_of_aggregates in parameter_switcher["position_of_aggregates"]:
            second_level_subfolder_path = create_folder(first_level_subfolder_path,
                                                         "position_a_" + str(float(
                                                             '%.2g' % position_of_aggregates)))
            coding = 0
            for number_of_aggregates in parameter_switcher["number_of_aggregates"]:
                coding += 1
                analysis_parameters = {"youngs_modulus_girder": 0,
                                       "number_of_aggregates": number_of_aggregates,
                                       "youngs_modulus_aggregate": 0,
                                       "position_of_aggregates": position_of_aggregates,
                                       "size_aggregate": size_aggregate,
                                       "length_girder": 0,
                                       "depth_girder": 0,
                                       "width_girder": 0,
                                       "poissons_ratio_girder": 0,
                                       "poissons_ratio_aggregate": 0}

                parameters_dict = check_default_parameters(analysis_parameters,
                                                           default_parameters)
                try:
                    subprocess.run(['/prog/abaqus/2020/bin/abaqus', 'cae',
                                    'noGUI=abq_generate_model.py', '--', str(coding),
                                    second_level_subfolder_path, str(parameters_dict)])
                except:
                    text_create('error.txt', str(parameters_dict))
                    continue

            for sequence in np.arange(1,len(parameter_switcher["youngs_modulus_girder"]) + 1, 3):
                os.chdir(second_level_subfolder_path)
                try:
                    subprocess.run('/prog/abaqus/2020/bin/abaqus interactive job=Job-' + str(sequence) + '.inp cpus=3 domains=3 mp_mode=threads parallel=domain double=explicit '
                                    '& /prog/abaqus/2020/bin/abaqus interactive job=Job-' + str(sequence + 1) + '.inp cpus=3 domains=3 mp_mode=threads parallel=domain double=explicit '
                                        '& /prog/abaqus/2020/bin/abaqus interactive job=Job-' + str(sequence + 2) + '.inp cpus=3 domains=3 mp_mode=threads parallel=domain double=explicit',
                                   shell=True, check=True)
                except:
                    text_create('error.txt', str('Job-'+str(sequence)+'failed'))
                    continue

            for sequence1 in np.arange(1, len(parameter_switcher["youngs_modulus_girder"]) + 1, 1):
                os.chdir(parent_path)
                subprocess.run(['/prog/abaqus/2020/bin/abaqus', 'cae', 'noGUI=abq_result_export.py', '--',
                                str(sequence1), second_level_subfolder_path])

    endtime = datetime.datetime.now()
    print('runtime =', endtime - starttime)