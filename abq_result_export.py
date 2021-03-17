from abaqus import *
from abaqusConstants import *
import __main__

from part import *
from section import *
from material import *
from assembly import *
from mesh import *
from step import *
from interaction import *
from load import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
from odbAccess import *
from scipy import fft
import scipy.fftpack
import numpy as np
import datetime
import math
import csv
import os

import abq_node_list as nl


# =============================================================================
# this python file is for Hostory data exporting, which are exported into csv files.
# =============================================================================


def odb_path(path, sequence):
    os.chdir(path)
    path_odb = os.path.abspath('Job-'+str(sequence)+'.odb')
    return path_odb


def create_folder():
    os.mkdir(os.path.join(parameter_analysis_path, 'output_csv'))
    csv_save_path = os.path.join(parameter_analysis_path, 'output_csv')
    return csv_save_path


def save_output_data_csv(path_odb, csv_save_path):
    path = path_odb
    odb = session.openOdb(name=path)
    step1 = odb.steps['Step-1']

    force_node = nl.set_force_node()
    region = step1.historyRegions['Node CONCRETE-1.' + str(force_node)]
    input_Data = region.historyOutputs['CF2'].data

    print('Data output starts!')
    os.chdir(csv_save_path)
    path_current = os.getcwd()
    file = 'input.csv'
    with open(os.path.join(path_current, file), 'w') as csv.file:
        pass

    path = file
    file1 = open(path, 'wb')
    writer = csv.writer(file1, dialect='excel')
    writer.writerow(["time_step", "force"])

    for row in input_Data:
        writer.writerow(row)
    print("Write data sucessful")
    file1.close()

    s = 0
    num = nl.main()
    for i in num:
        region = step1.historyRegions['Node CONCRETE-1.' + str(i)]
        u1_data = region.historyOutputs['U2'].data

        file = 'output-' + str(s) + '.csv'
        with open(os.path.join(path_current, file), 'w') as csv.file:
            pass

        path = file
        file1 = open(path, 'wb')
        writer = csv.writer(file1, dialect='excel')
        writer.writerow(["time_step", "y_disp"])

        for row in u1_data:
            writer.writerow(row)
        print("Write data sucessful")
        file1.close()
        s = s + 1


# =============================================================================
# This code is for the calculation and storage of the transfer functions.
# =============================================================================


# Read input data from csv file.
def import_input_data(path):
    with open(path, 'rt') as csv_file:
        reader = csv.DictReader(csv_file)
        time = []
        force = []
        for row in reader:
            time.append(float(row['time_step']))
            force.append(float(row['force']))

    return time, force


# Read output data from csv file.
def import_output_data(path):
    with open(path, 'rt') as csv_file:
        reader = csv.DictReader(csv_file)
        time = []
        dis_y = []
        for row in reader:
            time.append(float(row['time_step']))
            dis_y.append(float(row['y_disp']))

    return time, dis_y


def check_aliasing(output_signal):
    abs_output_signal = np.abs(output_signal)
    mag_max_position = np.argmax(abs_output_signal)  # 1) Locate the maximum magnitude of the absolute output signal

    energy_max = 0
    window_width = window_width_default
    for output_value in abs_output_signal[mag_max_position - window_width:mag_max_position + window_width + 1]:
        energy_max += output_value ** 2
    print(energy_max)

    energy_end = 0
    for output_value in abs_output_signal[-1 - 2 * window_width - 1:-1]:
        energy_end = output_value ** 2
    print(energy_end)

    print(energy_end / energy_max)
    threshold = threshold_default
    if energy_end / energy_max < threshold:
        print("No aliasing occurs!!!")
    else:
        raise Exception("Error: Aliasing occurs!!!")


def calculate_transfer_function(input_signal, output_signal):
    output_fft = fft(output_signal)                                                    # output data dft.
    output_fft[0] = output_fft[0] * 0.5

    input_fft = fft(input_signal)                                                      # input data dft.
    input_fft[0] = input_fft[0] * 0.5

    tf = np.divide(output_fft, input_fft)
    magnitude = np.abs(tf[0:len(output_fft) // 2]) * 2
    # im = np.imag(tf)
    # re = np.real(tf)
    # phase = np.arctan2(im, re)
    return magnitude


def save_transfer_function(csv_save_path, magnitude_list):
    print('Writing tfs into csvfile starts!')
    path_csv = csv_save_path
    file = 'tf.csv'
    with open(os.path.join(path_csv, file), 'w') as csv.file:
        pass

    path = os.path.join(path_csv, file)
    file1 = open(path, 'w')
    writer = csv.writer(file1, dialect='excel')

    for row in magnitude_list:
        writer.writerow(row)
        print("Transfer function's writting finished!")
    file1.close()
    print("All transfer functions' data output finished!")


def main(parameter_analysis_name, sequence):

    starttime = datetime.datetime.now()

    path_odb = odb_path(parameter_analysis_name, sequence)

    csv_save_path = create_folder()

    save_output_data_csv(path_odb, csv_save_path)
    print('All data-output is complete!')

    num = np.arange(0, len(nl.main()), 1)
    magnitude_list = []
    for i in num:
        time, input_signal = import_input_data(csv_save_path + '/input.csv')
        time, output_signal = import_output_data(csv_save_path + '/output-' + str(i) + '.csv')
        check_aliasing(output_signal)
        print(str(i) + 'finished')
        magnitude = calculate_transfer_function(input_signal, output_signal)
        magnitude_list.append(magnitude)

    frequency = scipy.fftpack.fftfreq(int(duration/time_step), time_step)[:int(duration/time_step) // 2]
    magnitude_list.append(frequency)

    print('All transfer functions here!')
    save_transfer_function(csv_save_path, magnitude_list)

    endtime = datetime.datetime.now()
    time = endtime - starttime
    print('runtime =', time)
  
    
if __name__ == '__main__':
    duration = 3
    time_step = 1E-6

    threshold_default = 1E-5
    window_width_default = 5

    parameter_analysis_path = sys.argv[-1]
    sequence = sys.argv[-2]

    main(parameter_analysis_path, sequence)