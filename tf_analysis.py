from scipy.fft import fft
from scipy import signal

import matplotlib.pyplot as plt
import datetime
import numpy as np
import scipy.fftpack
import math
import csv
import os

# =============================================================================
# this python file is for plotting the diagrams, for example: transfer function,
# displacement and input signal.
# =============================================================================


def plot_excitation(path):
    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column1 = [row['time_step'] for row in reader]
        time = [float(i) for i in column1]

    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column2 = [row['force'] for row in reader]
        excitation = [float(i) for i in column2]

    fig, ax = plt.subplots(2, 1)
    # make a little extra space between the subplots
    fig.subplots_adjust(hspace=0.5)

    ax[0].plot(time, excitation)
    ax[0].set_xlim(0, 0.0005)
    ax[0].set_xlabel('time(s)', fontsize=20)
    ax[0].set_ylabel('force(N)', fontsize=20)
    ax[0].grid(True)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    # plt.legend(loc='upper right', fontsize=20)

    dft_exc = fft(excitation)
    dft_exc[0] = dft_exc[0]*0.5
    magnitude = 2/len(dft_exc)*np.abs(dft_exc[0:len(dft_exc)//2])
    freq_oneside = scipy.fftpack.fftfreq(len(dft_exc), 1E-6)[0:len(dft_exc) // 2]
    ax[1].plot(freq_oneside, magnitude, label='dB')
    # ax[1].set_xlim(10**3, 10**6)
    plt.xscale('log')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    ax[1].set_ylabel('CSD (db)')
    ax[1].set_xlabel('frequency(Hz)', fontsize=20)
    ax[1].set_ylabel('magnitude(dB)', fontsize=20)
    ax[1].legend(loc='upper right', fontsize=20)


def specific_node_tf(path, n, timestep, timeperiod):
    with open(path, 'rt', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        Mag = []
        for i, rows in enumerate(reader):
            for j in n:
                if i == j:
                    row = rows
                    mag_s = [float(i) for i in row]
                    Mag.append(mag_s)
                    # print('Position at:' + str(n*0.01) + 'm')   # tell the x-position of the observed point.

    delta_t = timestep
    T = timeperiod
    N = int(T / delta_t)

    Frequency = scipy.fftpack.fftfreq(N, delta_t)[:N // 2]

    return Frequency, Mag


def plot_tf(X, magnitude, n, pos, color, title, type=''):
    plt.subplot(pos)
    plt.plot(X, magnitude, linewidth=1.0, color=color, label=title)
    plt.xscale('log')
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.title(label='Transfer function at ' + str(n*0.01) + 'm.')
    plt.xlabel('Frequency(Hz)', fontsize=15)
    plt.ylabel('Magnitude', fontsize=15)
    if type == 'Amp':
        plt.legend(loc='upper right', fontsize=12)
    if type == 'Amp_dB':
        plt.legend(loc='lower left', fontsize=12)


def plot_specific_tf(path, n, color, title, duration, type=''):
    X, Y = specific_node_tf(path, n, 1E-6, duration)
    s = 0
    if type == 'Amp':
        for i in n:
            Amp = Y[s]
            plot_tf(X, Amp, i, '23' + str(s+1), color, title, type='Amp')
            s = s + 1
    if type == 'Amp_dB':
        for i in n:
            Amp = Y[s]
            Amp_dB = []
            for j in Amp:
                dB = 20 * math.log10(j)
                Amp_dB.append(dB)
            plot_tf(X, Amp_dB, i, '23' + str(s + 1 + 3), color, title, type='Amp_dB')
            s = s + 1


def plot_displacement1(path):
    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column1 = [row['time_step'] for row in reader]
        time = [float(i) for i in column1]

    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column2 = [row['x_disp'] for row in reader]
        x_disp = [float(i) for i in column2]

    fig, ax = plt.subplots()
    ax.plot(time, x_disp)

    ax.set(xlabel='time (s)', ylabel='displacement (m)',
           title='HOR')
    ax.grid()
    plt.show()


def plot_displacement(path, position, title, color):
    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column1 = [row['time_step'] for row in reader]
        time = [float(i) for i in column1]

    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column2 = [row['x_disp'] for row in reader]
        x_disp = [float(i) for i in column2]
    plt.subplot(position)
    plt.plot(time, x_disp, linewidth=1.0, color=color, label=title)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.xlabel('Time(s)', fontsize=20)
    plt.ylabel('x-Displacement(m)', fontsize=20)
    plt.legend(loc='upper right', fontsize=20)
    plt.grid()


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


starttime = datetime.datetime.now()
print(starttime)

plot_specific_tf('C:/Users/ZZY/Desktop/tf_2s.csv', [4, 8, 16], 'green', '2s', 2)
plot_specific_tf('C:/Users/ZZY/Desktop/tf_5s.csv', [4, 8, 16], 'orange', '5s', 2)

# plt.subplots_adjust(wspace=0.15, hspace=0.40)
# plot_displacement1('C:/Users/ZZY/Desktop/x-Dis-2s.csv')
# plot_displacement1('C:/Users/ZZY/Desktop/x-Dis-5s.csv')
# plot_displacement('C:/Users/ZZY/Desktop/x-Dis-7.csv',111,'7','brown')
# plot_displacement('C:/Users/ZZY/Desktop/x-Dis-6.csv',111,'6','blue')
# plot_displacement('C:/Users/ZZY/Desktop/x-Dis-5.csv',111,'5','orange')
# plot_displacement('C:/Users/ZZY/Desktop/x-Dis-4.csv',111,'4','green')
#
plot_excitation('C:/Users/ZZY/Desktop/excitation.csv')
# plot_excitation('C:/Users/ZZY/Desktop/input_halfsine.csv')
plt.show()

endtime = datetime.datetime.now()
print('runtime =', endtime - starttime)
