from matplotlib import pyplot as plt
import os
import subprocess
import sys
import numpy
import time
import pathlib
import csv
import plot_new as pl


if __name__ == "__main__":
    # directory = pathlib.Path(os.getcwd())   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # script = directory / "withG.py"

    # X, Y = pl.import_input_data('C:/Users/ZZY/Desktop/database/input.csv')
    # pl.plot_input_signal(X, Y)
    # plt.show()

    # Run Abaqus (noGUI)
    # subprocess.run('abaqus cae noGUI=script.py', shell=True, check=True)
    # subprocess.run('abaqus cae noGUI=HOR_ex.py', shell=True, check=True)

    subprocess.run('/prog/abaqus/2020/bin/abaqus  cae noGUI=script.py', shell=True, check=True)





