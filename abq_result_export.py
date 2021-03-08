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


# =============================================================================
# this python file is for Hostory data exporting, which are exported into csv files.
# =============================================================================
mesh_size_girder = 0.01
width_girder = 0.10
length_girder = 1.45

duration = 3
time_step = 1E-6

thr = 1E-5
window_width = 5


def line_node_list(mesh_size):
    d = (width_girder/mesh_size + 1)**2
    a1 = 1 + (width_girder/mesh_size + 1)*(width_girder/mesh_size/2)
    n = length_girder/mesh_size + 1
    an = a1 + (n - 1)*d
    m = int(length_girder / mesh_size // 100)  # output required on 100 points, or near to 100 points
    nodes = np.arange(int(a1), int(an+1), int(m*d))
    nodes = nodes[::-1]
    print(nodes)
    return nodes


def create_folder(n):
    a = os.getcwd()
    os.mkdir(a + '/csv-' + str(n))
    path_csv_storage = os.path.abspath('csv-' + str(n))
    return path_csv_storage


def save_output_data_csv(n, mesh_size, path_csv_storage):
    path = os.path.abspath('Job-' + str(n) + '.odb')
    odb = session.openOdb(name=path)
    step1 = odb.steps['Step-1']

    num = line_node_list(mesh_size)

    force_node = num[48]
    region = step1.historyRegions['Node CONCRETE-1.' + str(force_node)]
    input_Data = region.historyOutputs['CF2'].data

    print('Data output starts!')
    path_csv = path_csv_storage
    file = 'input.csv'
    with open(os.path.join(path_csv, file), 'w') as csv.file:
        pass

    path = path_csv + '/' + file
    file1 = open(path, 'wb')
    writer = csv.writer(file1, dialect='excel')
    writer.writerow(["time_step", "force"])

    for row in input_Data:
        writer.writerow(row)
    print("Write data sucessful")
    file1.close()

    s = 0
    num1 = num[41:56]
    num2 = num[-15:]
    num = np.concatenate((num1, num2))
    for i in num:
        region = step1.historyRegions['Node CONCRETE-1.' + str(i)]
        # region = step1.historyRegions.items()
        u1_data = region.historyOutputs['U1'].data

        path_csv = path_csv_storage
        file = 'output-' + str(s) + '.csv'
        with open(os.path.join(path_csv, file), 'w') as csv.file:
            pass

        path = path_csv + '/' + file
        file1 = open(path, 'wb')
        writer = csv.writer(file1, dialect='excel')
        writer.writerow(["time_step", "x_disp"])

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
        dis_x = []
        for row in reader:
            time.append(float(row['time_step']))
            dis_x.append(float(row['x_disp']))

    return time, dis_x


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
    for i in abs_output_signal[
             mag_end_position - 2 * window_width - 1:mag_end_position]:
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


def save_transfer_function(path_csv_storage, magnitude_list):
    print('Writing tfs into csvfile starts!')
    path_csv = path_csv_storage
    file = 'tf.csv'
    with open(os.path.join(path_csv, file), 'w') as csv.file:
        pass

    path = path_csv + '/' + file
    file1 = open(path, 'w')
    writer = csv.writer(file1, dialect='excel')

    s = 0
    for row in magnitude_list:
        s = s + 1
        writer.writerow(row)
        print("Transfer function's writting finished!")
    file1.close()
    print("All transfer functions' data output finished!")


def main(n):

    starttime = datetime.datetime.now()
    path_csv_storage = create_folder(n)
    save_output_data_csv(n, mesh_size_girder, path_csv_storage)
    print('All data-output is complete!')

    num = np.arange(0, len(line_node_list(mesh_size_girder)), 1)
    magnitude_list = []
    for i in num:
        time, input_signal = import_input_data(path_csv_storage + '/input.csv')
        time, output_signal = import_output_data(path_csv_storage + '/output-' + str(i) + '.csv')
        check_aliasing(output_signal)
        magnitude = calculate_transfer_function(input_signal, output_signal)
        magnitude_list.append(magnitude)

    frequency = scipy.fftpack.fftfreq(int(duration/time_step), time_step)[:int(duration/time_step) // 2]
    magnitude_list.append(frequency)

    print('All transfer functions here!')
    save_transfer_function(path_csv_storage, magnitude_list)

    endtime = datetime.datetime.now()
    time = endtime - starttime
    print('runtime =', time)
  
    
if __name__ == '__main__':
    parameter = sys.argv[-1]
    parameter = parameter.strip("[]").split(",")
    key = parameter[0].strip("'")
    print(key)
    value = list(map(float, parameter[1:]))

    for i in np.arange(1, len(value) + 1, 1):
        main(i)