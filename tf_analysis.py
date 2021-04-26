from scipy.fft import fft
from scipy.signal import find_peaks

import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import numpy as np
import scipy.fftpack
import pickle
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


def specify_parameter_range(start, end, step_size):
    if end < start:
        raise Exception("Endpoint has to be larger or equal to the starting point")
    if step_size <= 0:
        raise Exception("step_size has to be positive")

    parameter_range = [round(i, 3) for i in list(np.linspace(start, end, math.ceil(((end - start) / step_size) + 1)))]
    return parameter_range


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
        num = len(nl.main(length_girder))
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


def plot_tf(X, Y, description, pic_name):
    fig, ax = plt.subplots()
    fig.set_size_inches(15, 8)
    for y in Y:
        ax.plot(X, y[0:-1], label=str(y[-1]))
    head_title = description
    plt.title(head_title)
    if 'dB' in pic_name:
        ax.set_ylim(-400, -50)
    else:
        ax.set_ylim(-1E-6, 2E-5)
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


def peak_analysis(path_array, first_value, node_pos, frequency_range_low, frequency_range_high, height_min):
    key = list(path_array.keys())
    peak_amplitude = []
    peak_frequency = []
    for second_value in path_array[key[0]][:-1]:
        # description = key[0] + '_' + str(second_value) + '_' + key[1] + '_' + str(first_value)
        description = key[0] + '_' + str(second_value)
        f, mag = import_specific_node_tf('C:/Users/ZZY/Desktop/'+description+'.csv',
                                         node_pos)

        frequency_low = np.where(f == frequency_range_low)[0][0]
        frequency_high = np.where(f == frequency_range_high)[0][0]
        print('the lower frequency position in the array is: ', frequency_low)
        print('the upper frequency position in the array is: ', frequency_high)

        peaks = find_peaks(mag[frequency_low:frequency_high], height=height_min)
        print('the chosen peak situation is: ', peaks)

        # peak_height = max(list(peaks[1]['peak_heights']))
        # peak_height_pos = np.argmax(list(peaks[1]['peak_heights']))
        # print(peak_height_pos)
        # print('magnitude of peaks is ', peak_height)
        #
        # pos = f[frequency_low:frequency_high][peaks[0]][peak_height_pos]
        # print('f position is ', pos)

        peak_height = list(peaks[1]['peak_heights'])
        print('magnitude of peaks is ', peak_height)

        pos = f[frequency_low:frequency_high][peaks[0]]
        print('f position is ', pos)

        peak_amplitude.append(peak_height)
        peak_frequency.append(pos)

    return peak_frequency, peak_amplitude


def plot_peak(x, peak_frequency, peak_amplitude, node_pos, parameter, sequence):
    fig, ax = plt.subplots(2, 1)
    # make a little extra space between the subplots
    fig.subplots_adjust(hspace=0.5)

    ax[0].plot(x, peak_frequency)
    # ax[0].set_xlim(0, 0.0005)
    ax[0].set_xlabel(parameter, fontsize=20)
    ax[0].set_ylabel('frequency(Hz)', fontsize=20)
    ax[0].grid(True)
    plt.title("No."+str(sequence+1)+" peak frequency and magnitude on different "
              + parameter + " at " + str(node_pos/2*0.1+0.05) + "m!")
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)

    ax[1].plot(x, peak_amplitude)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    ax[1].set_xlabel(parameter, fontsize=20)
    ax[1].set_ylabel('magnitude', fontsize=20)


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


def save_detail(path, detail_list, value_range):
    path_csv = path
    with open(path_csv, 'wt') as csv.file:
        pass

    file = open(path_csv, 'wt', newline='')
    writer = csv.writer(file, dialect='excel')
    first_row = list(map(float, value_range))
    writer.writerow(first_row)

    for row in detail_list:
        writer.writerow(row)
    file.close()


def main_position_analysis(file_path, frequency_min, frequency_max, height_min):
    node_sum = len(nl.main())
    node_range = np.arange(0, node_sum, 2)
    position_array = list(map(lambda x: x/2*0.1+0.05, node_range))
    amplitude_position_array = []

    key = list(file_path.keys())
    for path in file_path[key[0]][0:-1]:
        amplitude_position = []
        # frequency_position = []
        for num in node_range:
            f, mag = import_specific_node_tf('C:/Users/ZZY/Desktop/' + key[0]+'_'+str(path)+'.csv', num)
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

    # # frequency_position_array = []
    # for path in file_path[0:-1]:
    #     amplitude_position = []
    #     # frequency_position = []
    #     for num in node_range:
    #         f, mag = import_specific_node_tf('C:/Users/ZZY/Desktop/tf_'+str(path)+'.csv', num)
    #         peak_height = position_analysis(f, mag, frequency_min, frequency_max, height_min)
    #         amplitude_position.append(peak_height)
    #         # frequency_position.append(frequency)
    #     amplitude_position_array.append(amplitude_position)
    #     # frequency_position_array.append(frequency_position)
    # for i in np.arange(0, len(amplitude_position_array[0][0]), 1):
    #     amplitude_position_peak = []
    #     for array in amplitude_position_array:
    #         register = list(map(lambda x: x[i], array))
    #         amplitude_position_peak.append(register)
    #         print(amplitude_position_peak)
    #     plot_position(position_array, amplitude_position_peak, file_path,
    #                   file_path[-1]+',frequency range:'+str(frequency_min)+'~'+str(frequency_max)+'Hz')

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


def main_tf_analysis_single_loop(parameter_dict, node_array):
    key = list(parameter_dict.keys())
    for node in node_array:
        x_data = []
        y_data = []
        y_dB_data = []
        for value in parameter_dict[key[0]][:-1]:
            description = key[0]+'_'+str(value)
            X, Y = import_specific_node_tf('C:/Users/ZZY/Desktop/'+description+'.csv', node)
            y_dB = calculate_dB(Y)
            y_dB.append(value)
            Y.append(value)
            y_data.append(Y)
            y_dB_data.append(y_dB)
            x_data.append(X)
        picture_name = 'node_'+str(node)
        plot_tf(x_data[0], y_data, picture_name+'_'+parameter_dict[key[0]][-1], picture_name)
        plot_tf(x_data[0], y_dB_data, picture_name+'_'+parameter_dict[key[0]][-1], 'dB_'+picture_name)


def main_tf_analysis(parameter_dict, node_array):
    key = list(parameter_dict.keys())
    for first_value in parameter_dict[key[0]][:-1]:
        for node in node_array:
            x_data = []
            y_data = []
            y_dB_data = []
            for second_value in parameter_dict[key[1]][:-1]:
                description = key[0]+'_'+str(first_value)+'_'+key[1]+'_'+str(second_value)
                X, Y = import_specific_node_tf('C:/Users/ZZY/Desktop/'+description+'.csv', node)
                y_dB = calculate_dB(Y)
                y_dB.append(second_value)
                Y.append(second_value)
                y_data.append(Y)
                y_dB_data.append(y_dB)
                x_data.append(X)
            picture_name = 'node_'+str(node)+'_'+key[1]+'_'+str(first_value)
            plot_tf(x_data[0], y_data, picture_name+'_'+parameter_dict[key[1]][-1], picture_name)
            plot_tf(x_data[0], y_dB_data, picture_name+'_'+parameter_dict[key[1]][-1], 'dB_'+picture_name)


def main_peaks_detail_analysis(path_csv, parameter_array, node_pos, frequency_range_low, frequency_range_high, height_min):
    key = list(parameter_array.keys())
    peak_frequency_by_parameter, peak_amplitude_by_parameter = peak_analysis(parameter_array, parameter_array[key[0]][0], node_pos,
                                                   frequency_range_low, frequency_range_high, height_min)
    # the sub_arrays in these two arrays are the frequency or amplitude of
    # the peaks by different parameter value, so called '_by_parameter'.

    data_number = len(peak_amplitude_by_parameter[0])
    peak_amplitude_by_frequency = []
    for i in np.arange(0, data_number, 1):
        register_amp = list(map(lambda x: x[i], peak_amplitude_by_parameter))
        peak_amplitude_by_frequency.append(register_amp)
    print(peak_amplitude_by_frequency)
    peak_frequency_by_frequency = []
    for j in np.arange(0, data_number, 1):
        register_freq = list(map(lambda x: x[j], peak_frequency_by_parameter))
        peak_frequency_by_frequency.append(register_freq)
    print(peak_frequency_by_frequency)
    # the sub_array in these two arrays are the frequency or amplitude of
    # the peaks by different frequency range value, so called '_by_frequency'.

    peaks_number = len(peak_amplitude_by_frequency)
    print(peaks_number)
    peaks_detail = []
    for k in np.arange(0, peaks_number, 1):
        peaks_detail.append(peak_frequency_by_frequency[k])
        peaks_detail.append(peak_amplitude_by_frequency[k])
    print(peaks_detail)
    save_detail(path_csv, peaks_detail, parameter_array[key[0]][:-1])

    for l in np.arange(0, peaks_number, 1):
        plot_peak(parameter_array[key[0]][:-1], peak_frequency_by_frequency[l], peak_amplitude_by_frequency[l],
                  node_pos, parameter_array[key[0]][-1], l)
    plt.show()


if __name__ == '__main__':
    path_signal = 'C:/Users/ZZY/Desktop/halfsine.csv'
    length_girder = 1.45

    ym_dict = {"ym_a": [2E10, 3E10, 4E10, 5E10, 6E10, 7E10, "young's modulus of aggregates (step:1E10)"],
                      "ym_g": [5E9, 8E9, 11E9, 14E9, 17E9, 20E9, 23E9, 26E9, 29E9, 32E9, 35E9, 38E9,
                               "young's modulus of girder (step:3E9)"]
                      }

    poissons_ratio_girder_start = 0.08
    poissons_ratio_girder_end = 0.3
    poissons_ratio_girder_step = 0.005

    value_range = specify_parameter_range(poissons_ratio_girder_start, poissons_ratio_girder_end,
                                          poissons_ratio_girder_step)
    value_range.append("poisson's ratio of the girder (step:0.005)")
    pr_dict = {"pr": value_range}

    aggregates_dict = {"a_size": [5, "size of the aggregates (step:1mm diameter)"],
                       "num": [100, 200, 300, 400, 500, "number of the aggregates (step:100)"]}

    length_girder_start = 1.5
    length_girder_end = 1.7
    length_girder_step = 0.01
    length_range = specify_parameter_range(length_girder_start, length_girder_end,
                                          length_girder_step)
    length_range.append("length of the girder (step:1cm)")
    length_dict = {"len": length_range}

    spacing_dict = {"spacing": [1, 2, 3, 4, 5, 6, 7, 8, 9, "different spacing of aggregates"]}

    node_sum = len(nl.main(1.45))
    node_range = np.arange(0, node_sum, 2)
    node_array = [6]
    duration = 3

    lower_frequency = 0
    upper_frequency = 1.2*10**3
    min_height_peak = 0.5*10**-8

    # main_tf_analysis_single_loop(pr_dict, node_array)
    # main_tf_analysis(le, node_array)
    # main_position_analysis(pr_dict, lower_frequency, upper_frequency, min_height_peak)
    # main_signal_analysis(['C:/Users/ZZY/Desktop/output-29.csv'], type='output')
    main_peaks_detail_analysis('C:/Users/ZZY/Desktop/low_f_data.csv',
               spacing_dict, node_array[0], lower_frequency, upper_frequency, min_height_peak)
    plt.show()
