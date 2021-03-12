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
length_girder = 1.45
width_girder = 0.10
mesh_size_girder = 0.01

duration = 3
time_step = 1E-6

thr = 1E-5
window_width = 5


def create_folder(parameter_value):
    path_current = os.getcwd()
    os.mkdir(path_current + '/csv-' + str(parameter_value))
    csv_save_path = os.path.abspath('csv-' + str(parameter_value))
    return csv_save_path


def save_output_data_csv(csv_save_path):
    path = os.path.abspath('Analysis.odb')
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

    # path = path_current + '/' + file
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
        with open(os.path.join(path_csv, file), 'w') as csv.file:
            pass

        # path = path_current + '/' + file
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
    output_length = int(duration / time_step)

    abs_output_signal = np.abs(output_signal)
    mag_max_position = np.argmax(abs_output_signal)  # 1) Locate the maximum magnitude of the absolute output signal
    print(mag_max_position)
    mag_max = max(abs_output_signal)
    print(mag_max)

    energy_max_list = []
    for i in abs_output_signal[mag_max_position - window_width:mag_max_position + window_width + 1]:
        energy = i ** 2
        energy_max_list.append(energy)
    energy_max = sum(energy_max_list)
    print(energy_max)

    mag_end_position = output_length
    print(mag_end_position)
    mag_end = output_signal[mag_end_position]
    print(mag_end)

    energy_end_list = []
    for i in abs_output_signal[mag_end_position - 2 * window_width - 1:mag_end_position]:
        energy = i ** 2
        energy_end_list.append(energy)
    energy_end = sum(energy_end_list)
    print(energy_end)

    print(energy_end / energy_max)

    if energy_end / energy_max < thr:
        print("No aliasing occurs!!!")
    else:
        raise Exception("Error: Aliasing occurs on signal " + str(j) + "!!!")


def calculate_transfer_function(input_signal, output_signal):
    output_fft = fft(output_signal)                                                    # output data dft.
    output_fft[0] = output_fft[0] * 0.5

    input_fft = fft(input_signal)                                                      # input data dft.
    input_fft[0] = input_fft[0] * 0.5

    tf = np.divide(output_fft, input_fft)                                              # Transfer function's calculation: tf = dis_dft/force_dft.
    magnitude = np.abs(tf[0:len(output_fft) // 2])
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

    path = path_csv + '/' + file
    file1 = open(path, 'w')
    writer = csv.writer(file1, dialect='excel')

    for row in magnitude_list:
        writer.writerow(row)
        print("Transfer function's writting finished!")
    file1.close()
    print("All transfer functions' data output finished!")


def main(parameter_analysis_name, parameter_value):

    starttime = datetime.datetime.now()
    path_odb = os.path.abspath(parameter_analysis_name)
    os.chdir(path_odb)

    csv_save_path = create_folder(parameter_value)
    save_output_data_csv(csv_save_path)
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
    parameter = sys.argv[-1]
    parameter = parameter.strip("[]").split(" ")

    key_parameter = sys.argv[-2]
    parameter_list = list(map(float, parameter))

    for value in parameter_list:
        main(key_parameter + '-' + str(value), value)