from scipy.fft import fft
from scipy.signal import find_peaks
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import numpy as np
import scipy.fftpack
import math
import csv
import os


def import_data(path, node):
    total = sum(1 for line in open(path))
    with open(path, 'rt', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for i, rows in enumerate(reader):
            if i == node:
                row = rows
                data = [float(i) for i in row]
    return data, total


def sine_function(x, k, a, b):
    return k*np.sin(a*x) + b


def square_root_function(x, k, a, b):
    return k * np.sqrt(x) + b


def linear_function(x, k, a, b):
    return k*x + b


def exponential_function(x, k, a, b):
    return k*np.exp(a*x) + b


def curve_fitting(function, xdata, ydata):
    coe, _ = curve_fit(function, xdata, ydata)
    print('the coefficients are ', coe)

    y_fitting = function(xdata, coe[0], coe[1], coe[2])
    error_rate = (ydata - y_fitting)/ydata
    average = sum(np.abs(error_rate)) / len(error_rate)
    print('the average error rate is ', average)

    y_value_ave = sum(ydata)/len(ydata)
    sstot = sum(list(map(lambda x: (x-y_value_ave)**2, ydata)))
    err = (ydata-y_fitting)
    ssres = sum(list(map(lambda x: x**2, err)))
    r2 = 1 - ssres/sstot
    print(r2)
    return coe, r2


def plot(x, y, function, coe):
    fig, ax = plt.subplots()
    ax.plot(x, y, label='Original curve')
    y_fitted = function(x, coe[0], coe[1], coe[2])
    ax.plot(x, y_fitted, label='Fitted curve')
    ax.set_ylabel('Amplitude', fontsize=20)
    ax.set_title('fitting_coefficient', fontsize=20)
    ax.set_xlabel('pr (normalization)', fontsize=20)
    ax.grid(True)
    ax.legend(fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)


def main(path, row_start):
    x_value, data_number = import_data(path, 0)
    x_value = list(map(lambda x: x/x_value[0], x_value))            # standardization
    print('x data are ', x_value)
    for i in np.arange(row_start, data_number, 2):
        y_value, none = import_data(path, i)
        print('y data are ', y_value)

        functions_array = [linear_function, square_root_function, exponential_function, sine_function]
        r2_default = 0
        sequence = 0
        for function in functions_array:
            sequence += 1
            try:
                coe, r2 = curve_fitting(function, np.array(x_value), np.array(y_value))
                if r2 >= r2_default:
                    R2 = r2
                    coefficient = coe
                    better_function = function
                    r2_default = r2
                if sequence == len(functions_array):
                    print("the better fitted function is ", better_function)
                    print("its coefficients are ", coefficient)
                    print("its R2 is ", R2)
                    plot(np.array(x_value), np.array(y_value), better_function, np.array(coefficient))
                    plt.show()

                else:
                    r2_default = r2
            except RuntimeError:
                print("this function don't fit our data: ", function)
                continue


if __name__ == '__main__':
    path_csv = 'C:/Users/ZZY/Desktop/pr_feiner/medium/medium_f2_data.csv'
    frequency_row = 1
    amplitude_row = 2
    main(path_csv, amplitude_row)
