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


def arithmetic_sequence(meshSize):
    d = (0.1/meshSize + 1)**2
    a1 = 1 + (0.1/meshSize + 1)*(0.1/meshSize/2)
    n = 1.45/meshSize + 1
    an = a1 + (n - 1)*d
    m = int(1.45 / meshSize // 100)  # output required on 100 points, or near to 100 points
    nodes = np.arange(int(a1), int(an+1), int(m*d))
    return nodes


def test_node():
    d = (0.1 / 0.01 + 1) ** 2
    a1 = [37, 41, 81, 85]
    n = 1.45 / 0.01 + 1
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
    # an.reverse()
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


def transfer_function(path_input, path_output):
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
    return magnitude


def tf_set(meshSize, path_csv, type=''):
    starttime = datetime.datetime.now()
    print(starttime)

    num1 = arithmetic_sequence(meshSize)
    num2 = test_node()
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

    # =============================================================================
    # the observed line is evenly divided into 145 parts, so we will have 146 observed points.
    # abaqus sorted the number of nodes in a reverse order, so i use reverse() command to fix it.
    # =============================================================================

    Magnitude = []
    s = 0
    for j in output_csv_name:
        s = s + 1
        print('Transfer function at ' + str((s - 1) * 0.01) + 'm calculation starts!')
        mag = transfer_function(path_csv + '/' + 'input.csv',
                                   path_csv + '/' + str(j))
        Magnitude.append(mag)
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
    for row in Magnitude:
        s = s + 1
        writer.writerow(row)
        print('Transfer function at ' + str((s-1)*0.01) + 'm output sucessful!')
    file1.close()
    print('All tf data output finished!')
    endtime = datetime.datetime.now()
    print(endtime)
    print('calculation time is ', endtime - starttime)


def calculation(file_name):
    starttime = datetime.datetime.now()
    tf_set(0.01, '/home/zhangzia/Schreibtisch/studienarbeit/investigation/G_size/' + file_name + '/csv', type='export_20')
    endtime = datetime.datetime.now()
    time = endtime - starttime
    print('runtime =', time)
