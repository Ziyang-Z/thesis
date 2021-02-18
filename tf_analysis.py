from matplotlib import pyplot as plt
from scipy.fft import fft
from scipy import signal

import matplotlib
import datetime
import numpy as np
import scipy.fftpack
import math
import csv
import os


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

    delta_t = 1E-6
    T = 5
    N = int(T / delta_t)

    Frequency = scipy.fftpack.fftfreq(N, delta_t)[:N // 2]

    dis_fft = fft(dis_x)                                    # output data dft.

    force_fft = fft(force)                                  # input data dft.

    tf = np.divide(dis_fft, force_fft)                      # Transfer function's calculation: tf = dis_dft/force_dft.
    magnitude = np.abs(tf[0:N // 2])
    # im = np.imag(tf)
    # re = np.real(tf)
    # phase = np.arctan2(im, re)
    return Frequency, magnitude


def arithmetic_sequence(meshSize):
    d = (0.1/meshSize + 1)**2
    a1 = 1 + (0.1/meshSize + 1)*(0.1/meshSize/2)
    n = 1.45/meshSize + 1
    an = a1 + (n - 1)*d
    m = int(1.45 / meshSize // 100)                         # output required on 146 points
    nodes = np.arange(int(a1), int(an+1), int(m*d))
    position = []
    for i in nodes:
        num = format((i-a1)/d/m*0.01, '.2f')
        position.append(num)
    return nodes, position


def tf_set(meshSize, path_csv):
    starttime = datetime.datetime.now()
    print(starttime)
    num, position = arithmetic_sequence(meshSize)
    output_csv_name = []

    for i in num:
        file_name = 'x-Dis-' + str(i) + '.csv'
        output_csv_name.append(file_name)
        output_csv_name.reverse()                                                   # reverse the list

    # =============================================================================
    # the observed line is evenly divided into 145 parts, so we will have 146 observed points.
    # abaqus sorted the number of nodes in a reverse order, so i use reverse() command to fix it.
    # =============================================================================

    Magnitude = []
    s = 0
    for j in output_csv_name:
        s = s + 1
        print('Transfer function at ' + str((s - 1) * 0.01) + 'm calculation starts!')
        f, mag = transfer_function(path_csv + '/' + 'input.csv',
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


def specific_node_tf(path, n, timestep, timeperiod):
    with open(path, 'rt', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for i, rows in enumerate(reader):
            if i == n:
                row = rows
        print(len(row))
        mag_s = [float(i) for i in row]
    print('Position at:' + str(n*0.01) + 'm')   # tell the x-position of the observed point.

    delta_t = timestep
    T = timeperiod
    N = int(T / delta_t)

    Frequency = scipy.fftpack.fftfreq(N, delta_t)[:N // 2]
    return Frequency, mag_s


def plot_tf(X, magnitude, pos, color, title):
    plt.subplot(pos)
    plt.plot(X, magnitude, linewidth=1.0, color=color, label=title)
    plt.xscale('log')
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlabel('Frequency(Hz)', fontsize=18)
    plt.ylabel('Magnitude', fontsize=18)
    plt.legend(loc='upper right', fontsize=20)
    # plt.legend(loc='upper right', fontsize=20)
    # plt.subplot(122)
    # plt.plot(X, phase, linewidth=1.0, color='brown')
    # plt.xticks(fontsize=15)
    # plt.yticks(fontsize=15)
    # plt.xlabel('Frequency(Hz)', fontsize=18)
    # plt.ylabel('Phase', fontsize=18)


def action(path, G, n, pos, color, title):
    X, Y = transfer_function(path + 'input.csv', path + 'x-Dis-'+str(G) + '-' + str(n) + '.csv')
    plot_tf(X, Y, pos, color, title)


# action('C:/Users/ZZY/Desktop/', 0, 0.00, 121, 'brown', 'noG')
# action('C:/Users/ZZY/Desktop/', 25, 0.00, 121, 'yellowgreen', '25')
# action('C:/Users/ZZY/Desktop/', 125, 0.00, 121, 'deepskyblue', '125')
# action('C:/Users/ZZY/Desktop/', 225, 0.00, 121, 'm', '225')
# action('C:/Users/ZZY/Desktop/', 325, 0.00, 121, 'crimson', '325')
#
# action('C:/Users/ZZY/Desktop/', 0, 1.45, 111, 'brown', 'noG')
# action('C:/Users/ZZY/Desktop/', 25, 1.45, 111, 'yellowgreen', '25')
# action('C:/Users/ZZY/Desktop/', 125, 1.45, 111, 'deepskyblue', '125')
# action('C:/Users/ZZY/Desktop/', 225, 1.45, 111, 'm', '225')
# action('C:/Users/ZZY/Desktop/', 325, 1.45, 111, 'crimson', '325')
# plt.show()

# tf_set(0.005, '/home/zhangzia/Schreibtisch/studienarbeit/0.005/csvfile_425G')

# X, Y = specific_node_tf('/home/zhangzia/Schreibtisch/studienarbeit/0.005/csvfile_325G/tf.csv', 1, 1E-6, 5)
# plot_tf(X, Y, 111, 'brown', '1')

action('C:/Users/ZZY/Desktop/', 0, 1.45, 111, 'brown', 'noG')
action('C:/Users/ZZY/Desktop/', 325, 1.45, 111, 'm', '325')
action('C:/Users/ZZY/Desktop/', 425, 1.45, 111, 'crimson', '425')
plt.show()