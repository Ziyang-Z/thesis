from matplotlib import pyplot as plt
from scipy.fft import fft
import numpy as np
import scipy.fftpack
import math
import csv


def import_csv_data(path):
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


def dft_calculation(path, timestep, timeperiod):
    time, dis_x = import_csv_data(path)
    delta_t = timestep
    T = timeperiod
    N = int(T / delta_t)
    X = scipy.fftpack.fftfreq(N, delta_t)[:N // 2]
    y_fft = fft(dis_x)
    y_dft = 2.0 / N * np.abs(y_fft[0:N // 2])
    return X, y_dft


def dft_dB_transform(path, timestep, timeperiod):
    time, dis_x = import_csv_data(path)
    delta_t = timestep
    T = timeperiod
    N = int(T / delta_t)
    X = scipy.fftpack.fftfreq(N, delta_t)[:N // 2]
    y_fft = fft(dis_x)
    y_dft = 2.0 / N * np.abs(y_fft[0:N // 2])
    y_dB = []
    for i in y_dft:
        dB = 20*math.log10(i)
        y_dB.append(dB)                           # yl is dB = 20*lg(dis_x)
    return X, y_dB


def plot_displacement(X, Y, position, title, color):
    plt.subplot(position)
    plt.plot(X, Y, linewidth=1.0, color=color, label=title)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.xlabel('Time(s)', fontsize=20)
    plt.ylabel('x-Displacement(m)', fontsize=20)
    plt.legend(loc='upper right', fontsize=20)
    plt.grid()
    # plt.legend()


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


# X, Y = import_csv_data("C:/Users/ZZY/Desktop/725Gs.csv")
# plot_displacement(X, Y, 131, 'displacement', 'brown')
# X, Y = dft_calculation("C:/Users/ZZY/Desktop/725Gs.csv", 1E-6, 5)
# plot_dft(X, Y, 132, 'dft', 'brown')
# X, Y = dft_dB_transform("C:/Users/ZZY/Desktop/725Gs.csv", 1E-6, 5)
# plot_dft(X, Y, 133, 'dft-dB', 'brown')

X, Y = import_csv_data("C:/Users/ZZY/Desktop/0.008.csv")
plot_displacement(X, Y, 111, 'displacement', 'brown')

plt.show()


