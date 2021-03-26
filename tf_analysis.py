from scipy.fft import fft
from scipy.signal import find_peaks

import matplotlib.pyplot as plt
import datetime
import numpy as np
import scipy.fftpack
import math
import csv
import os

import abq_node_list as nl

# =============================================================================
# this python file is for plotting the diagrams, for example: transfer function,
# displacement and input signal.
# =============================================================================

duration = 3
time_step = 1E-6


# =============================================================================
# import the in- and output data from the existed csv file
# =============================================================================
def import_input_signal(path):
    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        time = []
        force = []
        for row in reader:
            time.append(float(row['time_step']))
            force.append(float(row['force']))

    return time, excitation


def import_output_signal(path):
    with open(path, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        time = []
        dis_y = []
        for row in reader:
            time.append(float(row['time_step']))
            dis_y.append(float(row['y_disp']))

    return time, dis_y


# ==================================================================================
# import the transfer function that we want at specific nodes, because the transfers
# functions are saved in the csv files by rows from node 0 to node 29(totally 30 nodes)
# and the last row is the frequency value.
# =============================================================================
def import_specific_node_tf(path, node):
    with open(path, 'rt', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        num = len(nl.main())
        for i, rows in enumerate(reader):
            if i == node:
                row = rows
                amplitude = [float(i) for i in row]

            if i == num:
                row = rows
                frequency = [float(i) for i in row]
                frequency = np.array(frequency)
    return frequency, amplitude


def calculate_dB(signal):
    signal_dB = list(map(lambda x: 20 * math.log10(x), signal))
    return signal_dB


def plot_tf(X, Y, node_position, description):
    fig, ax = plt.subplots()
    # make a little extra space between the subplots
    fig.subplots_adjust(hspace=0.5)
    for y in Y:
        ax.plot(X, y[0:-1], label=str(y[-1]))
        plt.title('at node_' + str(node_position) + ', parameter:' + description)
    ax.set_xlabel('Frequency(Hz)', fontsize=20)
    ax.set_ylabel('Magnitude', fontsize=20)
    ax.grid(True)
    ax.legend()
    plt.xscale('log')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)


# ==========================================================================================================
# i chose a specific frequency range here, which could be low or high frequency and there are peaks in this
# range. Find the peak we wanna analyze (specify the minimal height of the peak to locate the peak we want),
# use the frequency of this peak, analyze all the tf at this frequency.
# ==========================================================================================================
def specific_frequency_analysis(f, mag, path_array, node_pos, frequency_range_low, frequency_range_high, height_min):
    frequency_low = np.where(f == frequency_range_low)[0][0]
    frequency_high = np.where(f == frequency_range_high)[0][0]
    print(frequency_low)
    print(frequency_high)

    peaks = find_peaks(mag[0][frequency_low:frequency_high], height=height_min)
    print(peaks)
    specific_frequency = peaks[0][0]
    print(specific_frequency)

    peak_amplitude = []
    for i in path_array:
        f, mag = import_specific_node_tf(i, [node_pos])
        amp = mag[0][specific_frequency]
        peak_amplitude.append(amp)
    print(peak_amplitude)
    peak_frequency = 0
    return peak_frequency, peak_amplitude


def peak_analysis(path_array, node_pos, frequency_range_low, frequency_range_high, height_min):
    peak_amplitude = []
    peak_frequency = []

    for i in path_array:
        print(i)
        f, mag = import_specific_node_tf('C:/Users/ZZY/Desktop/tf_'+str(i)+'.csv', node_pos)

        frequency_low = np.where(f == frequency_range_low)[0][0]
        frequency_high = np.where(f == frequency_range_high)[0][0]
        print(frequency_low)
        print(frequency_high)

        peaks = find_peaks(mag[frequency_low:frequency_high], height=height_min)
        print(peaks)
        key = 'peak_heights'
        peak_height = list(peaks[1][key])[0]
        print('magnitude of peaks is ', peak_height)

        pos = f[frequency_low:frequency_high][peaks[0]][0]
        print('f position is ', pos)

        peak_amplitude.append(peak_height)
        peak_frequency.append(pos)
    print(peak_amplitude)
    print(peak_frequency)

    return peak_frequency, peak_amplitude


def plot_peak(x, peak_frequency, peak_amplitude, node_pos, parameter, type=''):
    if type == 'peaks':
        fig, ax = plt.subplots(2, 1)
        # make a little extra space between the subplots
        fig.subplots_adjust(hspace=0.5)

        ax[0].plot(x, peak_frequency)
        # ax[0].set_xlim(0, 0.0005)
        ax[0].set_xlabel(parameter, fontsize=20)
        ax[0].set_ylabel('frequency(Hz)', fontsize=20)
        ax[0].grid(True)
        plt.title("the peak frequency and magnitude on different " + parameter + " at " + str(node_pos*0.1+0.05) + "m!")
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)

        ax[1].plot(x, peak_amplitude)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        ax[1].set_xlabel(parameter, fontsize=20)
        ax[1].set_ylabel('magnitude', fontsize=20)

    if type == 'specific frequency':
        fig, ax = plt.subplots()
        ax.plot(x, peak_amplitude)
        # ax[0].set_xlim(0, 0.0005)
        ax.set_xlabel(parameter, fontsize=20)
        ax.set_ylabel('magnitude', fontsize=20)
        ax.grid(True)
        plt.title("the amplitude on specific frequency on different " + parameter)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)


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


# ==========================================================================================================
# i chose a specific frequency range here, which could be low or high frequency and there are peaks in this
# range. Find the peak and plot them by parameters.
# ==========================================================================================================
def position_analysis(f, mag, frequency_min, frequency_max, height_min):
    frequency_low = int(np.where(f == frequency_min)[0][0])
    frequency_high = int(np.where(f == frequency_max)[0][0])
    print(frequency_low)
    print(frequency_high)

    peaks = find_peaks(mag[frequency_low:frequency_high], height=height_min)
    print(peaks)
    key = 'peak_heights'
    peak_height = list(peaks[1][key])
    print('magnitude of peaks is ', peak_height)
    pos = f[frequency_low:frequency_high][peaks[0]]
    print('f position is ', pos)
    return peak_height


def plot_position(X, Y, label, description):
    fig, ax = plt.subplots()
    # make a little extra space between the subplots
    fig.subplots_adjust(hspace=0.5)
    s = 0
    for y in Y:
        ax.plot(X, y, label=str(label[s]))
        s += 1
    ax.set_xlabel('Position along the girder(m)', fontsize=20)
    ax.set_ylabel('Magnitude', fontsize=20)
    ax.grid(True)
    ax.legend()
    plt.title(description)
    # plt.xscale('log')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)


def main_position_analysis(file_path, frequency_min, frequency_max, height_min):
    node_sum = len(nl.main())
    node_range = np.arange(0, node_sum, 2)
    position_array = list(map(lambda x: x/2*0.1+0.05, node_range))
    amplitude_position_array = []
    # frequency_position_array = []
    for path in file_path[0:-1]:
        amplitude_position = []
        # frequency_position = []
        for num in node_range:
            f, mag = import_specific_node_tf('C:/Users/ZZY/Desktop/tf_'+str(path)+'.csv', num)
            peak_height = position_analysis(f, mag, frequency_min, frequency_max, height_min)
            amplitude_position.append(peak_height)
            # frequency_position.append(frequency)
        amplitude_position_array.append(amplitude_position)
        # frequency_position_array.append(frequency_position)
    for i in np.arange(0, len(amplitude_position_array[0][0]), 1):
        amplitude_position_peak = []
        for array in amplitude_position_array:
            register = list(map(lambda x: x[i], array))
            amplitude_position_peak.append(register)
            print(amplitude_position_peak)
        plot_position(position_array, amplitude_position_peak, file_path,
                      file_path[-1]+',frequency range:'+str(frequency_min)+'~'+str(frequency_max)+'Hz')
    # amplitude_position_peak = []
    # for array in amplitude_position_array:
    #     register = list(map(lambda x: x[0], array))
    #     amplitude_position_peak.append(register)
    #     print(amplitude_position_peak)
    # plot_position(position_array, amplitude_position_peak, file_path, 0)


def main_signal_analysis(path_signal_array, type=''):
    for i in path_signal_array:
        if type == 'input':
            time, signal = import_input_signal(i)
            frequency, magnitude = calculate_dft(signal)
            plot_signal(time, signal, frequency, magnitude)

        if type == 'output':
            time, signal = import_output_signal(i)
            frequency, magnitude = calculate_dft(signal)
            plot_signal(time, signal, frequency, magnitude)
    plt.show()


def main_tf_analysis(path_array, node_array):
    for i in node_array:
        x_data = []
        y_data = []
        y_dB_data = []
        for j in path_array[0:-1]:
            X, Y = import_specific_node_tf('C:/Users/ZZY/Desktop/tf_'+str(j)+'.csv', i)
            y_dB = calculate_dB(Y)
            y_dB.append(j)
            Y.append(j)
            y_data.append(Y)
            y_dB_data.append(y_dB)
            x_data.append(X)
        plot_tf(x_data[0], y_data, i, path_array[-1])
        plot_tf(x_data[0], y_dB_data, i, path_array[-1])


def main_peaks(path_array, node_pos, frequency_range_low, frequency_range_high, height_min):
    peak_frequency, peak_amplitude = peak_analysis(path_array[0:-1], node_pos,
                                                   frequency_range_low, frequency_range_high, height_min)
    plot_peak(parameter_range, peak_frequency, peak_amplitude, node_pos, path_array[-1], type='peaks')
    plt.show()


if __name__ == '__main__':
    path_signal = 'C:/Users/ZZY/Desktop/halfsine.csv'

    path_array1 = [601, 602, 603, 604, 605, 606, 'size:0.006, evenly, number of aggregates:0~500']
    path_array2 = [5E9, 8E9, 11E9, 14E9, 17E9, 20E9, "young's modulus of girder (step:3E9)"]

    parameter_range = path_array1[:6]

    node_array = [5]
    lower_frequency = 0
    upper_frequency = 10**2
    min_height_peak = 2*10**-9

    # main_tf_analysis(path_array2, node_array)

    main_position_analysis(path_array2, lower_frequency, upper_frequency, min_height_peak)
    # main_signal_analysis(['C:/Users/ZZY/Desktop/output-29.csv'], type='output')
    # main_signal_analysis(['C:/Users/ZZY/Desktop/output-28.csv'], type='output')
    # main_peaks(path_array1, 11, lower_frequency, upper_frequency, min_height_peak)
    plt.show()



