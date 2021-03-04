from matplotlib import pyplot as plt
from scipy.fft import fft
import scipy.fftpack
import matplotlib
import numpy as np
import csv
import datetime
import math
import os


# =============================================================================
# This code is for the calculation and storage of the transfer functions.
# =============================================================================
mesh_size = 0.01
length_girder = 1.45
width_girder = 0.10
path_csv_storage = os.path.abspath('csv')


def line_node_list():
    d = (width_girder/mesh_size + 1)**2
    a1 = 1 + (width_girder/mesh_size + 1)*(width_girder/mesh_size/2)
    n = length_girder/mesh_size + 1
    an = a1 + (n - 1)*d
    m = int(length_girder / mesh_size // 100)  # output required on 100 points, or near to 100 points
    nodes = np.arange(int(a1), int(an+1), int(m*d))
    return nodes


def test_node_list():
    d = (width_girder / mesh_size + 1) ** 2
    a1 = [37, 41, 81, 85]
    n = length_girder / mesh_size + 1
    an = []
    for i in a1:
        x = i + (n - 1) * d
        an.append(i)
        an.append(int(x))

    a1 = [34, 78]
    n = [49, 98]
    for i in a1:
        for j in n:
            x = i + (j - 1) * d
            an.append(int(x))

    a1 = [4, 8, 114, 118]
    n = [49, 98]
    for i in a1:
        for j in n:
            x = i + (j - 1) * d
            an.append(int(x))
    an.sort()
    return an


# Read input data from csv file.
def import_input_data(path):
    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column1 = [row['time_step'] for row in reader]
        time = [float(i) for i in column1]

    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column2 = [row['force'] for row in reader]
        force = [float(i) for i in column2]

    return time, force


# Read output data from csv file.
def import_output_data(path):
    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column1 = [row['time_step'] for row in reader]
        time = [float(i) for i in column1]

    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column2 = [row['x_disp'] for row in reader]
        dis_x = [float(i) for i in column2]

    return time, dis_x


def calculate_transfer_function(path_input, path_output):
    time, dis_x = import_output_data(path_output)
    time, force = import_input_data(path_input)

    dis_fft = fft(dis_x)                                    # output data dft.
    dis_fft[0] = dis_fft[0]*0.5

    force_fft = fft(force)                                  # input data dft.
    force_fft[0] = force_fft[0]*0.5

    tf = np.divide(dis_fft, force_fft)                      # Transfer function's calculation: tf = dis_dft/force_dft.
    magnitude = np.abs(tf[0:len(dis_fft) // 2])
    # im = np.imag(tf)
    # re = np.real(tf)
    # phase = np.arctan2(im, re)
    return dis_x, magnitude


def store_transfer_function(path_csv, type=''):
    starttime = datetime.datetime.now()
    print(starttime)

    num1 = line_node_list()
    num2 = test_node_list()
    output_csv_name = []

    if type == 'export_146':
        for i in num1:
            file_name = 'x-Dis-' + str(i) + '.csv'
            output_csv_name.append(file_name)
            output_csv_name.reverse()
    if type == 'export_20':
        for i in num2:
            file_name = 'x-Dis-' + str(i) + '.csv'
            output_csv_name.append(file_name)
            output_csv_name.reverse()

    magnitude = []
    s = 0
    for j in output_csv_name:
        s = s + 1
        print('Transfer function at calculation starts!')
        x_disp, mag = calculate_transfer_function(path_csv + '/' + 'input.csv',
                                                  path_csv + '/' + str(j))
        
        output_length = int(duration / time_step)
        output_signal = x_disp

        abs_output_signal = np.abs(output_signal)
        mag_max_position = np.argmax(abs_output_signal)  # 1) Locate the maximum magnitude of the absolute output signal
        print(mag_max_position)
        mag_max = max(abs_output_signal)
        print(mag_max)

        window_width = 5

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
        for i in abs_output_signal[
                 mag_end_position - 2 * window_width - 1:mag_end_position]:
            energy = i ** 2
            energy_end_list.append(energy)
        energy_end = sum(energy_end_list)
        print(energy_end)

        thr = 1E-5
        print(energy_end / energy_max)

        if energy_end / energy_max < thr:
            print("No aliasing occurs!!!")
        else:
            raise Exception("Error: Aliasing occurs on signal " + str(j) + "!!!")
        
        magnitude.append(mag)
    print('All tfs here!')

    print('Writing tfs into csvfile starts!')
    path = path_csv
    file = 'tf.csv'
    with open(os.path.join(path, file), 'w') as csv.file:
        pass

    path = path_csv + '/' + file
    file1 = open(path, 'w')
    writer = csv.writer(file1, dialect='excel')

    s = 0
    for row in magnitude:
        s = s + 1
        writer.writerow(row)
        print('Transfer function output sucessful!')
    file1.close()
    print('All tf data output finished!')
    endtime = datetime.datetime.now()
    print(endtime)
    print('calculation time is ', endtime - starttime)


def main():
    starttime = datetime.datetime.now()
    store_transfer_function(path_csv_storage, type='export_20')
    endtime = datetime.datetime.now()
    time = endtime - starttime
    print('runtime =', time)

