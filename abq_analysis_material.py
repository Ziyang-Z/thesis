import numpy as np
import subprocess
import datetime
import logging
import traceback
import numpy
import math
import sys
import os

import excitation as ex

parent_path = os.path.dirname(os.path.abspath('abq_analysis.py'))

youngs_modulus_girder_start =
youngs_modulus_girder_end =
youngs_modulus_girder_step =

poissons_ratio_girder_start =
poissons_ratio_girder_end =
poissons_ratio_girder_step =


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
        "youngs_modulus_girder": specify_parameter_range(youngs_modulus_girder_start, youngs_modulus_girder_end, youngs_modulus_girder_step),
        "number_of_aggregates": [0],
        "youngs_modulus_aggregate": [0],
        "position_of_aggregates": [0, 0.005],
        "size_aggregate": [0],
        "length_girder": [0],
        "depth_girder": [0],
        "width_girder": [0],
        "poissons_ratio_girder": specify_parameter_range(poissons_ratio_girder_start, poissons_ratio_girder_end, poissons_ratio_girder_step),
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

    logging.basicConfig(filename='analysis-log.txt', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    file_handle = logging.FileHandler('error.log', 'a')
    file_handle.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(module)s: %(message)s',))
    logger = logging.Logger('s1', level=logging.WARNING)
    logger.addHandler(file_handle)

    os.chdir(parent_path)
    total_folder_path = create_folder(parent_path, 'analysis')
    for poisson_ratio in parameter_switcher["poissons_ratio_girder"]:
        subfolder_path = create_folder(total_folder_path,
                                       "pr_girder=" + str(float('%.2g' % poisson_ratio)))
        try:
            if os.path.exists(subfolder_path):
                logging.info('the subfolder:' + subfolder_path + ' exists, ready for analysis!')
            else:
                raise Warning('Error occurred! the subfolder:' + subfolder_path + ' not exists! Analysis cannot go on!')
        except Warning:
            logger.warning(traceback.format_exc())
            continue
            
        for youngs_modulus in parameter_switcher["youngs_modulus_girder"]:
            coding = youngs_modulus
            analysis_parameters = {"youngs_modulus_girder": youngs_modulus,
                                   "number_of_aggregates": 0,
                                   "youngs_modulus_aggregate": 0,
                                   "position_of_aggregates": 0,
                                   "size_aggregate": 0,
                                   "length_girder": 0,
                                   "depth_girder": 0,
                                   "width_girder": 0,
                                   "poissons_ratio_girder": poisson_ratio,
                                   "poissons_ratio_aggregate": 0}

            parameters_dict = check_default_parameters(analysis_parameters,
                                                       default_parameters)
            logging.info('the parameters values are ', str(parameters_dict))

            subprocess.run(['/prog/abaqus/2020/bin/abaqus', 'cae',
                            'noGUI=abq_generate_model.py', '--', str(coding),
                            subfolder_path, str(parameters_dict)])

            os.chdir(parent_path)
            try:
                if os.path.exists(os.path.join(subfolder_path, 'Job-'+str(coding)+'.inp')):
                    logging.info("Job-"+str(coding)+".inp file exists!")
                else:
                    raise Warning('Error occurred! Job-'+str(coding)+'.inp file not exists! parameters are'
                                  + str(parameters_dict))
            except Warning:
                logger.warning(traceback.format_exc())
                continue

        for sequence in np.arange(1, len(parameter_switcher["youngs_modulus_girder"]) + 1, 3):
            os.chdir(subfolder_path)
            try:
                subprocess.run('/prog/abaqus/2020/bin/abaqus interactive job=Job-' + str(sequence) + '.inp cpus=3 domains=3 mp_mode=threads parallel=domain double=explicit '
                                '& /prog/abaqus/2020/bin/abaqus interactive job=Job-' + str(sequence + 1) + '.inp cpus=3 domains=3 mp_mode=threads parallel=domain double=explicit '
                                    '& /prog/abaqus/2020/bin/abaqus interactive job=Job-' + str(sequence + 2) + '.inp cpus=3 domains=3 mp_mode=threads parallel=domain double=explicit',
                               shell=True, check=True)
            except:
                logger.warning(traceback.format_exc())
                continue

        for sequence1 in np.arange(1, len(parameter_switcher["youngs_modulus_girder"]) + 1, 1):
            os.chdir(parent_path)
            subprocess.run(['/prog/abaqus/2020/bin/abaqus', 'cae', 'noGUI=abq_result_export.py', '--',
                            str(sequence1), subfolder_path])

    endtime = datetime.datetime.now()
    logging.info('runtime =', endtime - starttime)