# -*- coding: utf-8 -*-


import numpy as np
from scipy import fft
import os
import warnings
import csv

path_csv = os.getcwd()
time_step = 1E-6
max_frequency_of_interest = 80000
simulationtime = 3


def generate_impulse_excitation():

# =============================================================================
# csvpath:                    Full Filepath to save .txt-File with Time-History of Impulse-Input
# time_step:              Sampling period [s]
# simulationtime:             Total duration of the whole excitation signal [s]
# max_frequency_of_interest:  To be specified in [Hz] -> determines pulsewidth
# =============================================================================
    
    # Create HalfSine Impulse

    # PulseFrequency = (2/3) of max_frequency_of_interest to have decent signal energy
    # and create same first zero crossing as for rectangle impulse
    pulse_frequency = max_frequency_of_interest*(2/3)
    pulse_duration = 1/(2*pulse_frequency)
    time = np.arange(0, simulationtime, time_step)
    t_pulse = np.arange(0, pulse_duration, time_step)
    print(len(t_pulse))

    if len(t_pulse) < 10:
        warnings.warn("Less than 10 samples for Impulse. Consider decreasing time_step")
    impulse = np.sin(np.pi*2*pulse_frequency*t_pulse)                       # create the waveform (impact force)
    zeroline = np.zeros(len(time)-len(t_pulse))                            # after the force all zero.
    excitation = np.concatenate((impulse, zeroline))                        # concatenation of the two array.

    return time, excitation


def write_excitation_csv(time, input_excitation):
    array = list(zip(time, input_excitation))                                    # write excitation into a csv file.
    path = path_csv
    file = 'excitation.csv'
    with open(os.path.join(path, file), 'w') as csv.file:
        pass

    path = path_csv + '/' + file
    file1 = open(path, 'w', newline='')
    writer = csv.writer(file1, dialect='excel')
    writer.writerow(["time_step", "force"])

    for row in array:
        writer.writerow(row)
    file1.close()


def main():
    time, input_excitation = generate_impulse_excitation()
    write_excitation_csv(time, input_excitation)


if __name__ == '__main__':
    main()
