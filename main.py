import os
import subprocess
import sys
import numpy
import time
import pathlib
import csv


def abaqus_noGUI(name):
    argument = 'noGUI=' + str(name)
    subprocess.run(['abaqus', 'cae', argument], shell=True, check=True)


if __name__ == "__main__":
    # directory = pathlib.Path(os.getcwd())
    # script = directory / "withG.py"

    # Run Abaqus (noGUI)
    subprocess.run('/prog/abaqus/2020/bin/abaqus cae noGUI=plot.py', shell=True, check=True)


    # subprocess.run('/prog/abaqus/2020/bin/abaqus  cae noGUI=plot.py', shell=True, check=True)





