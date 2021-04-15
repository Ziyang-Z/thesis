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
    with open(path, 'rt', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for i, rows in enumerate(reader):
            if i == node:
                row = rows
                data = [float(i) for i in row]
    return data


def func(x, k, a, b):
    # return k * np.sqrt(x) + b
    # return k*x + b
    # return k*np.exp(a*x) + b
    # return k*np.exp(-a*x) + b
    return k*a**x + b


def curve_fitting(xdata, ydata):
    popt, _ = curve_fit(func, xdata, ydata)
    print('the coefficients are ', popt)
    return popt


def plot(x, y, coe):
    fig, ax = plt.subplots()
    ax.plot(x, y, label='Original curve')
    y1 = func(x, coe[0], coe[1], coe[2])
    ax.plot(x, y1, label='Fitted curve')
    ax.set_ylabel('Amplitude', fontsize=20)
    ax.set_title('fitting_coefficient', fontsize=20)
    ax.set_xlabel('pr (normalization)', fontsize=20)
    ax.grid(True)
    ax.legend(fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)


def main(path):
    x_value = import_data(path, 0)
    x_value = list(map(lambda x: x/x_value[0], x_value))            # standardization
    print('x data are ', x_value)
    y_value = import_data(path, 1)                                # 0 is for frequency, 1 is for amplitude.
    print('y data are ', y_value)
    f_ave = sum(y_value)/len(y_value)
    print("average frequency is ", f_ave)

    coe = curve_fitting(x_value, y_value)
    y_fitting = func(np.array(x_value), coe[0], coe[1], coe[2])
    # print('the fitted y data are', y_fitting)
    error_rate = (y_value - y_fitting)/y_value
    average = sum(np.abs(error_rate)) / len(error_rate)
    # print('the error rate is like ', error_rate)
    print('the average error rate is ', average)

    y_value_ave = sum(y_value)/len(y_value)
    sstot = sum(list(map(lambda x: (x-y_value_ave)**2, y_value)))
    e = (y_value-y_fitting)
    ssres = sum(list(map(lambda x: x**2, e)))
    r2 = 1 - ssres/sstot
    print(r2)

    plot(np.array(x_value), np.array(y_value), coe)
    plt.show()


if __name__ == '__main__':
    path_csv = 'C:/Users/ZZY/Desktop/size_agg/medium/medium_f5_data.csv'

    main(path_csv)
