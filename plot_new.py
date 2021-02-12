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


def dft_input_calculation(path, timestep, timeperiod):
    time, force = import_input_data(path)
    delta_t = timestep
    T = timeperiod
    N = int(T / delta_t)
    X = scipy.fftpack.fftfreq(N, delta_t)[:N // 2]
    y_fft = fft(force)
    y_dft = 2.0 / N * np.abs(y_fft[0:N // 2])
    y_dft[0] = 1.0 / N * np.abs(y_fft[0])                  # Y(k=0) is not multiplied by 2.0.
    return X, y_dft


def dft_calculation(path, timestep, timeperiod):
    time, dis_x = import_output_data(path)
    delta_t = timestep
    T = timeperiod
    N = int(T / delta_t)
    X = scipy.fftpack.fftfreq(N, delta_t)[:N // 2]
    y_fft = fft(dis_x)
    y_dft = 2.0 / N * np.abs(y_fft[0:N // 2])
    y_dft[0] = 1.0 / N * np.abs(y_fft[0])                  # Y(k=0) is not multiplied by 2.0.
    return X, y_dft


def dft_dB_transform(path, timestep, timeperiod):
    time, dis_x = import_output_data(path)
    delta_t = timestep
    T = timeperiod
    N = int(T / delta_t)
    X = scipy.fftpack.fftfreq(N, delta_t)[:N // 2]
    y_fft = fft(dis_x)
    y_dft = 2.0 / N * np.abs(y_fft[0:N // 2])
    y_dft[0] = 1.0 / N * np.abs(y_fft[0])
    y_dB = []
    for i in y_dft:
        dB = 20*math.log10(i)
        y_dB.append(dB)                                   # yl is dB = 20*lg(dis_x)
    return X, y_dB


def transfer_function(path_input, path_output, timestep, timeperiod):
    time, dis_x = import_output_data(path_output)
    time, force = import_input_data(path_input)

    delta_t = timestep
    T = timeperiod
    N = int(T / delta_t)

    X = scipy.fftpack.fftfreq(N, delta_t)[:N // 2]

    dis_fft = fft(dis_x)                                    # output data dft.
    dis_dft = 2.0 / N * np.abs(dis_fft[0:N // 2])
    dis_dft[0] = 1.0 / N * np.abs(dis_fft[0])

    force_fft = fft(force)                                  # input data dft.
    force_dft = 2.0 / N * np.abs(force_fft[0:N // 2])
    force_dft[0] = 1.0 / N * np.abs(force_fft[0])

    tf = np.divide(dis_fft, force_fft)
    # tf = []
    # for i, j in zip(dis_fft, force_fft):                         # Transfer function's calculation: tf = dis_dft/force_dft.
    #     h = i/j
    #     tf.append(h)
    # im = np.imag(tf)
    # re = np.real(tf)
    # magnitude = []
    # for k, l in zip(im, re):
    magnitude = 2.0 / N * np.abs(tf[0:N // 2])
    # mag_dB = 20*math.log10(mag)
    # magnitude.append(mag_dB)
    # phase = np.arctan2(im, re)
    return X, magnitude


def plot_tf(X, magnitude):
    plt.subplot(121)
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


def plot_input_signal(X, Y):
    plt.plot(X, Y, linewidth=1.0, color='brown', label='Impact force')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.xlabel('Time(s)', fontsize=20)
    plt.ylabel('y-force(N)', fontsize=20)
    plt.legend(loc='upper right', fontsize=20)
    plt.grid()


def plot_displacement1(X, Y):
    fig, ax = plt.subplots()
    ax.plot(X, Y)

    ax.set(xlabel='time (s)', ylabel='displacement (m)',
           title='HOR')
    ax.grid()
    plt.show()


def plot_displacement(X, Y, position, title, color):
    plt.subplot(position)
    plt.plot(X, Y, linewidth=1.0, color=color, label=title)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.xlabel('Time(s)', fontsize=20)
    plt.ylabel('x-Displacement(m)', fontsize=20)
    plt.legend(loc='upper right', fontsize=20)
    plt.grid()


def plot_dft(X, Y, position, title, color):
    plt.subplot(position)
    plt.plot(X, Y, linewidth=1.0, color=color, label=title)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlabel('Frequency(Hz)', fontsize=18)
    plt.ylabel('Amplitude', fontsize=18)
    plt.legend(loc='upper right', fontsize=20)


def plot_difference(path1, path2, color, title):
    time, dis_x = import_csv_data(path1)
    time1, dis_x1 = import_csv_data(path2)
    difference = np.subtract(dis_x, dis_x1)
    plt.plot(time, difference, color=color, label=title)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlabel('Time(s)', fontsize=18)
    plt.ylabel('Displacement(m)', fontsize=18)
    plt.legend(loc='upper right', fontsize=20)
    plt.grid()


# X, Y = import_output_data("C:/Users/ZZY/Desktop/725Gs.csv")
# plot_displacement(X, Y, 131, 'displacement', 'brown')
# X, Y = dft_calculation("C:/Users/ZZY/Desktop/725Gs.csv", 1E-6, 5)
# plot_dft(X, Y, 132, 'dft', 'brown')
# X, Y = dft_dB_transform("C:/Users/ZZY/Desktop/725Gs.csv", 1E-6, 5)
# plot_dft(X, Y, 133, 'dft-dB', 'brown')

# X, Y = import_output_data("C:/Users/ZZY/Desktop/0.008.csv")
# plot_displacement(X, Y, 111, 'displacement', 'brown')
# X, Y = dft_calculation("C:/Users/ZZY/Desktop/0.008.csv", 1E-6, 5)
# plot_displacement(X, Y, 111, 'dft', 'brown')

# X, Y = dft_input_calculation('C:/Users/ZZY/Desktop/database/input.csv', 1E-6, 5)
# plot_dft(X, Y, 111, 'inputsignal', 'brown')

X, Magnitude = transfer_function('C:/Users/ZZY/Desktop/database/input.csv', 'C:/Users/ZZY/Desktop/database/x-Dis-4.csv', 1E-6, 5)
plot_tf(X, Magnitude)

# X, Y = dft_calculation('C:/Users/ZZY/Desktop/0.008.csv', 1E-6, 5)
# plot_dft(X, Y, 111, 'dft', 'brown')
#
plt.show()


