from scipy.fft import fft
from scipy.signal import find_peaks

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

duration = 3
time_step = 1E-6


def import_input_signal(path):
    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column1 = [row['time_step'] for row in reader]
        time = [float(i) for i in column1]

    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column2 = [row['force'] for row in reader]
        excitation = [float(i) for i in column2]

    return time, excitation


def import_output_signal(path):
    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column1 = [row['time_step'] for row in reader]
        time = [float(i) for i in column1]

    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column2 = [row['x_disp'] for row in reader]
        x_disp = [float(i) for i in column2]

    return time, x_disp


def import_specific_node_tf(path, n):
    with open(path, 'rt', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        Mag = []
        for i, rows in enumerate(reader):
            for j in n:
                if i == j:
                    row = rows
                    mag_s = [float(i) for i in row]
                    Mag.append(mag_s)

    delta_t = time_step
    T = duration
    N = int(T / delta_t)

    Frequency = scipy.fftpack.fftfreq(N, delta_t)[:N // 2]

    return Frequency, Mag


def peaks(f, mag):
    for i in mag:
        peaks = find_peaks(i, height=2.5*10**-9)
        print(peaks)
        print(peaks[0])
        print(peaks[1])
        key = 'peak_heights'
        peak_height = list(peaks[1][key])
        print('magnitude of peaks is ', peak_height)
        print(peak_height[-1])
        pos = f[peaks[0]]
        print('f position is ', pos)
        print(pos[-1])


def calculate_dft(signal):
    dis_fft = fft(signal)                                    # output data dft.
    dis_fft[0] = dis_fft[0]*0.5
    magnitude = 2/len(dis_fft)*np.abs(dis_fft[0:len(dis_fft) // 2])

    frequency = scipy.fftpack.fftfreq(len(dis_fft), time_step)[:len(dis_fft) // 2]

    return frequency, magnitude


def plot_signal(time, signal, frequency, magnitude):
    fig, ax = plt.subplots(2, 1)
    # make a little extra space between the subplots
    fig.subplots_adjust(hspace=0.5)

    ax[0].plot(time, signal)
    # ax[0].set_xlim(0, 0.0005)
    ax[0].set_xlabel('time(s)', fontsize=20)
    ax[0].set_ylabel('force(N)', fontsize=20)
    ax[0].grid(True)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)

    ax[1].plot(frequency, magnitude)
    ax[1].set_xlim(10**1, 10**6)
    plt.xscale('log')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    ax[1].set_xlabel('frequency(Hz)', fontsize=20)
    ax[1].set_ylabel('magnitude', fontsize=20)


def plot_tf(X, magnitude, n, pos, color, title, type=''):
    plt.subplot(pos)
    plt.plot(X, magnitude, linewidth=1.0, color=color, alpha=0.4, label=title)
    plt.xscale('log')
    # plt.xlim(10**4, 10**5)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.title(label='Transfer function at ' + str(n*0.01) + 'm.')
    plt.xlabel('Frequency(Hz)', fontsize=15)
    plt.ylabel('Magnitude', fontsize=15)
    if type == 'Amp':
        plt.legend(loc='upper right', fontsize=12)
    if type == 'Amp_dB':
        plt.legend(loc='lower left', fontsize=12)


def plot_specific_tf(path, n, color, title, type=''):
    X, Y = import_specific_node_tf(path, n)
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


def plot_displacement(time, output, position, title, color):

    plt.subplot(position)
    plt.plot(time, output, linewidth=1.0, color=color, label=title)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.xlabel('Time(s)', fontsize=20)
    plt.ylabel('x-Displacement(m)', fontsize=20)
    plt.legend(loc='upper right', fontsize=20)
    plt.grid()


starttime = datetime.datetime.now()
print(starttime)

# plot_specific_tf('C:/Users/ZZY/Desktop/tf_5.5.csv', [4, 8, 16], 'blue', '5.5', type='Amp')
# plot_specific_tf('C:/Users/ZZY/Desktop/tf_5.4.csv', [4, 8, 16], 'limegreen', '5.4', type='Amp')
# plot_specific_tf('C:/Users/ZZY/Desktop/tf_5.3.csv', [4, 8, 16], 'darkmagenta', '5.3', type='Amp')
# plot_specific_tf('C:/Users/ZZY/Desktop/tf_5.2.csv', [4, 8, 16], 'red', '5.2', type='Amp')
# plot_specific_tf('C:/Users/ZZY/Desktop/tf_5.1.csv', [4, 8, 16], 'coral', '5.1', type='Amp')
# plot_specific_tf('C:/Users/ZZY/Desktop/tf_5.csv', [4, 8, 16], 'orange', '5', type='Amp')
# plot_specific_tf('C:/Users/ZZY/Desktop/tf_5.5.csv', [4, 8, 16], 'blue', '5.5', type='Amp_dB')
# plot_specific_tf('C:/Users/ZZY/Desktop/tf_5.4.csv', [4, 8, 16], 'limegreen', '5.4', type='Amp_dB')
# plot_specific_tf('C:/Users/ZZY/Desktop/tf_5.3.csv', [4, 8, 16], 'darkmagenta', '5.3', type='Amp_dB')
# plot_specific_tf('C:/Users/ZZY/Desktop/tf_5.2.csv', [4, 8, 16], 'red', '5.2', type='Amp_dB')
# plot_specific_tf('C:/Users/ZZY/Desktop/tf_5.1.csv', [4, 8, 16], 'coral', '5.1', type='Amp_dB')
# plot_specific_tf('C:/Users/ZZY/Desktop/tf_5.csv', [4, 8, 16], 'orange', '5', type='Amp_dB')

# plt.subplots_adjust(wspace=0.15, hspace=0.40)
# plot_displacement1('C:/Users/ZZY/Desktop/x-Dis.csv')
# plot_displacement1('C:/Users/ZZY/Desktop/x-Dis-5s.csv')
# plot_displacement('C:/Users/ZZY/Desktop/x-Dis-7.csv',111,'7','brown')
# plot_displacement('C:/Users/ZZY/Desktop/x-Dis-6.csv',111,'6','blue')
# plot_displacement('C:/Users/ZZY/Desktop/x-Dis-5.csv',111,'5','orange')
# plot_displacement('C:/Users/ZZY/Desktop/x-Dis-4.csv',111,'4','green')
#
# time, excitation = import_input_signal('C:/Users/ZZY/Desktop/halfsine.csv')
# plot_excitation()
# plot_excitation('C:/Users/ZZY/Desktop/input_halfsine.csv')

# time, signal = import_input_signal('C:/Users/ZZY/Desktop/input_sine.csv')
# frequency, magnitude = calculate_dft(signal)
# plot_signal(time, signal, frequency, magnitude)
#
# plt.show()

f, mag = import_specific_node_tf('C:/Users/ZZY/Desktop/tf_5.5.csv', [16])
peaks(f, mag)

# f, mag = import_specific_node_tf('C:/Users/ZZY/Desktop/tf_5.3.csv', [16])
# peaks(mag)

endtime = datetime.datetime.now()
print('runtime =', endtime - starttime)
