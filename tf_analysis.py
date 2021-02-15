from matplotlib import pyplot as plt
from scipy.fft import fft
from scipy import signal

import matplotlib
import numpy as np
import scipy.fftpack
import math
import csv


# Read input data from csv file.
def import_input_data(path):
    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column1 = [row['time_step'] for row in reader]
        time = []
        for i in column1:
            j = float(i)
            time.append(j)
    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column2 = [row['force'] for row in reader]
        force = []
        for k in column2:
            l = float(k)
            force.append(l)
    return time, force


# Read output data from csv file.
def import_output_data(path):
    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column1 = [row['time_step'] for row in reader]
        time = []
        for i in column1:
            j = float(i)
            time.append(j)
    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column2 = [row['x_disp'] for row in reader]
        dis_x = []
        for k in column2:
            l = float(k)
            dis_x.append(l)
        # for row in reader:
        #     data_time_step.append(float(row['time_step']))
        #     data_dis_x.append(float(row['x_disp']))
    return time, dis_x


def transfer_function(path_input, path_output):
    time, dis_x = import_output_data(path_output)
    time, force = import_input_data(path_input)

    dis_fft = fft(dis_x)                                    # output data dft.

    force_fft = fft(force)                                  # input data dft.

    tf = np.divide(dis_fft, force_fft)                      # Transfer function's calculation: tf = dis_dft/force_dft.
    magnitude = np.abs(tf[0:N // 2])
    # im = np.imag(tf)
    # re = np.real(tf)
    # phase = np.arctan2(im, re)
    return X, magnitude


def arithmetic_sequence(meshSize):
    d = (0.1/meshSize + 1)**2
    a1 = 1 + (0.1/meshSize + 1)*(0.1/meshSize/2)
    n = 1.45/meshSize + 1
    an = a1 + (n - 1)*d
    m = int(1.45 / meshSize // 100)                         # output required on 146 points
    nodes = np.arange(int(a1), int(an+1), int(m*d))
    HOR_num = []
    for i in nodes:
        num = format((i-a1)/d/m*0.01, '.2f')
        HOR_num.append(num)
    return nodes, HOR_num


# =============================================================================
# the observed line  is evenly divided into 145 parts, so we will have 146 observed points.
# =============================================================================

def tf_set(meshSize, path_csv, n, timestep, timeperiod):
    num, HOR_num = arithmetic_sequence(meshSize)
    output_file = []
    Magnitude = []
    for i in num:
        file_name = 'x-Dis-' + str(i) + '.csv'
        output_file.append(file_name)

    for j in output_file:
        X, mag = transfer_function(path_csv + 'input.csv',
                                   path_csv + str(j))
        Magnitude.append(mag)
        print(len(Magnitude))

    delta_t = timestep
    T = timeperiod
    N = int(T / delta_t)

    Frequency = scipy.fftpack.fftfreq(N, delta_t)[:N // 2]

    # =============================================================================
    # the observed line is evenly divided into 145 parts, so we will have 146 observed points.
    # abaqus sorted the number of nodes in a reverse order, so if we wanna point at 0.01m,
    # we specify n=1 (n=0.01*100) ->[145-n]-> [144] this slice is what we wanna.
    # =============================================================================

    Mag_analysis = Magnitude[145-n]
    print('Position at:' + HOR_num[n] + 'm')   # tell the x-position of the observed point.
    return Frequency, Mag_analysis


def plot_tf(X, magnitude):
    plt.subplot(111)
    plt.plot(X, magnitude, linewidth=1.0, color='brown')
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlabel('Frequency(Hz)', fontsize=18)
    plt.ylabel('Magnitude', fontsize=18)
    # plt.legend(loc='upper right', fontsize=20)
    # plt.subplot(122)
    # plt.plot(X, phase, linewidth=1.0, color='brown')
    # plt.xticks(fontsize=15)
    # plt.yticks(fontsize=15)
    # plt.xlabel('Frequency(Hz)', fontsize=18)
    # plt.ylabel('Phase', fontsize=18)


path = '/home/zhangzia/Schreibtisch/studienarbeit/0.005/csvfile'
X, Y = tf_set(0.005, path, 70, 1E-6, 5)
plot_tf(X, Y)
plt.show()