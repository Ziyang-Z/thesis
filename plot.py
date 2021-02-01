import csv
import numpy as np
from scipy.fft import fft
import math
import scipy.fftpack
from matplotlib import pyplot as plt


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


def plot_displacement(path, position, title, color):
    time, dis_x = import_csv_data(path)
    plt.subplot(position)
    plt.plot(time, dis_x, linewidth=1.0, color=color, label=title)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.xlabel('Time(s)', fontsize=20)
    plt.ylabel('x-Displacement(m)', fontsize=20)
    plt.legend(loc='upper right', fontsize=20)
    plt.grid()
    # plt.legend()
    plt.show()


def plot_dft(path, position, title, color):
    plt.plot(X, y_dft, linewidth=1.0, color=color, label=title)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlabel('Frequency(Hz)', fontsize=18)
    plt.ylabel('Amplitude', fontsize=18)
    plt.legend(loc='upper right', fontsize=20)
    plt.show()


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
    plt.show()


# plot_displacement("C:/Users/ZZY/Desktop/wtoutG.csv", 111, 'no aggregate', 'brown')
# plot_displacement("C:/Users/ZZY/Desktop/Marble.csv", 111, 'aggregate Marble', 'darkcyan')
# plot_displacement("C:/Users/ZZY/Desktop/SBS.csv", 111, 'aggregate SBS', 'orange')
# plot_displacement("C:/Users/ZZY/Desktop/sameM.csv", 111, 'same material', 'slategray')
# plot_displacement("C:/Users/ZZY/Desktop/725Gs.csv", 111, '725 aggregates', 'slategray')


# plot_dft("C:/Users/ZZY/Desktop/Studienarbeit/22_Jan/wtoutG.csv", 111, 'no aggregate', 'brown')
# plot_dft("C:/Users/ZZY/Desktop/Studienarbeit/22_Jan/Marble.csv", 111, 'aggregate Marble', 'darkcyan')
# plot_dft("C:/Users/ZZY/Desktop/725Gs.csv", 111, '725 aggregates', 'orange')
# plot_dft("C:/Users/ZZY/Desktop/sameM.csv", 111, 'same material', 'slategray')


# plot_difference("C:/Users/ZZY/Desktop/wtoutG.csv", "C:/Users/ZZY/Desktop/sameM.csv", 'cornflowerblue', 'no aggregates and same material')
# plot_difference("C:/Users/ZZY/Desktop/wtoutG.csv", "C:/Users/ZZY/Desktop/Marble.csv", 'brown', 'no aggregates and marble')


# plt.show()

# historyRegion.keys()