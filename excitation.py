# -*- coding: utf-8 -*-


import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import os
import warnings
 

def generate_impulse_excitation(path_csv, timeincrement, simulationtime, max_frequency_of_interest, typ="halfsine", plot="on"):

# =============================================================================
# csvpath:                    Full Filepath to save .txt-File with Time-History of Impulse-Input
# timeincrement:              Sampling period [s]
# simulationtime:             Total duration of the whole excitation signal [s]
# max_frequency_of_interest:  To be specified in [Hz] -> determines pulsewidth
# typ:                        Keywords are "halfsine" or "rectangle"
# plot:                       Set to "on" for visualization
# =============================================================================
    
    # Create HalfSine Impulse
    if typ == "halfsine":
        
        # PulseFrequency = (2/3) of max_frequency_of_interest to have decent signal energy
        # and create same first zero crossing as for rectangle impulse
        pulse_frequency = max_frequency_of_interest*(2/3)
        pulse_duration = 1/(2*pulse_frequency)
        t_ges = np.arange(0, simulationtime, timeincrement)
        t_pulse = np.arange(0, pulse_duration, timeincrement)
        
        if len(t_pulse) < 20:
            warnings.warn("Less than 20 samples for Impulse. Consider decreasing timeincrement")
        impulse = np.sin(np.pi*2*pulse_frequency*t_pulse)                       # create the waveform (impact force)
        zeroline = np.zeros(len(t_ges)-len(t_pulse))                            # after the force all zero.
        excitation = np.concatenate((impulse, zeroline))                        # concatenation of the two array.
        if plot == "on":
            fig, ax = plt.subplots(2, 1)
            ax[0].plot(t_ges, excitation)
            dft_exc = fft(excitation)
            dft_exc[0] = dft_exc[0]*0.5
            magnitude = 2/len(dft_exc)*np.abs(dft_exc[0:len(dft_exc)//2])
            freq_oneside = fftfreq(len(dft_exc), timeincrement)[0:len(dft_exc)//2]
            ax[1].plot(freq_oneside, magnitude)

        array = list(zip(t_ges, excitation))                                    # write excitation into a csv file.
        path = path_csv
        file = 'excitation.csv'
        with open(os.path.join(path, file), 'w') as csv.file:
            pass

        path = path_csv + '/' + file
        file1 = open(path, 'wb')
        writer = csv.writer(file1, dialect='excel')
        writer.writerow(["time", "excitation"])

        for row in array:
            writer.writerow(row)
        file1.close()

        with open(path, 'rt', encoding="utf-8") as csv_file:                    # read excitation from the csv file.
            reader = csv.DictReader(csv_file)
            column1 = [row['time'] for row in reader]
            t_ges = [float(i) for i in column1]
        with open(path, 'rt', encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            column2 = [row['excitation'] for row in reader]
            excitation = [float(i) for i in column2]

        return t_ges, excitation
    
    if typ=="rectangle":
        
        # PulseDuration = Inverse of max_frequency_of_interest; Factor 2 to have decent signalenergy
        pulse_duration=1/(max_frequency_of_interest*2)
        t_ges=np.arange(0,simulationtime,timeincrement)
        t_pulse=np.arange(0,pulse_duration,timeincrement)
        if len(t_pulse) < 20:
            warnings.warn("Less than 20 samples for Impulse. Consider decreasing timeincrement")
        impulse=np.ones(len(t_pulse))
        impulse[0]=0.5
        impulse[-1]=0.5
        zeroline=np.zeros(len(t_ges)-len(t_pulse)-1)
        excitation=np.concatenate((np.array([0]),impulse,zeroline))
        if plot=="on":
            fig, ax = plt.subplots(2,1)
            ax[0].plot(t_ges,excitation)
            dft_exc=fft(excitation)
            dft_exc[0]=dft_exc[0]*0.5
            magnitude=2/len(dft_exc)*np.abs(dft_exc[0:len(dft_exc)//2])
            freq_oneside=fftfreq(len(dft_exc),timeincrement)[0:len(dft_exc)//2]
            ax[1].plot(freq_oneside,magnitude)
        csvfile=os.path.join(csvpath,"input.txt")
        np.savetxt(csvfile, np.transpose(np.array([t_ges, excitation])))
        return t_ges,excitation
        

def main():
    path_for_csv = ""
    delta_t = 1E-6
    max_freq = 50000
    duration = 0.5
    
    generate_impulse_excitation(path_for_csv, delta_t, duration, max_freq, typ="halfsine")
    
    
if __name__ == "__main__":
    main()

