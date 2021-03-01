from scipy.fft import fft
from scipy import signal

import matplotlib.pyplot as plt
import datetime
import numpy as np
import scipy.fftpack
import math
import csv
import os


def aliasing_check(path_input, path_output):

    with open(path_output, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column2 = [row['x_disp'] for row in reader]
        x_disp = [float(i) for i in column2]
        x_disp.reverse()                                                            # reverse the output array, because i wanna find the oscillation end point.
        output = []
        s = 0
        for i in x_disp:
            s = s + 1
            output.append(i)
            if 1000000 < s < 5000000:                                                # Search range 0~4s
                a = x_disp[s-8000]                                                  # 8000 is a minimum Oscillation frequency as my prediction.
                b = x_disp[s]
                if a/b < 0:                                                         # the tiny wave form is like a sinus wave, so if two values(have a period distance) have opposite sign,
                    break                                                           # that means there is a wave form.

    oscillation_end = 5-len(output)*1E-6                                            # transform the oscillation end time.
    print(len(output))
    print('Oscillation ends at ' + str(oscillation_end) + 's')
    print('output signal length is ', int(5E6-len(output)))

    with open(path_input, 'rt', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        column2 = [row['force'] for row in reader]
        excitation = [float(i) for i in column2]
        input = []
        s = 0
        for i in excitation:
            s = s + 1
            input.append(i)
            if s > 1:
                if i == 0:
                    break

        print('input signal length is ', len(input))

    print('dft length is ', len(x_disp))

    if len(x_disp) >= len(input) + len(output) - 1:
        print('DFT-Length N >= L{h} + L{input} - 1, no aliasing!')


def main():
    aliasing_check('C:/Users/ZZY/Desktop/input.csv', 'C:/Users/ZZY/Desktop/x-Dis-5s.csv')


if __name__ == '__main__':
    main()
