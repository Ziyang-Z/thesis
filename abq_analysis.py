import numpy as np
import subprocess
import datetime
import numpy
import sys
import os

import excitation as ex


if __name__ == "__main__":

    starttime = datetime.datetime.now()

    ex.main()

    parameter_switcher = {
        "youngs_modulus": ["youngs_modulus", 40E9, 40.5E9, 41E9, 41.5E9, 42E9],
        "load": ["load", -1, -10, -100, -1000],
        "size_aggregate": ["size_aggregate", 5, 6, 7, 8, 9, 10]
    }

    print("which parameter you want to analyze.")
    key_parameter = "youngs_modulus"
    print(key_parameter)

    subprocess.run(['/prog/abaqus/2020/bin/abaqus', 'cae', 'noGUI=abq_generate_model.py', '--', str(parameter_switcher[key_parameter][0:])])
    num = np.arange(1, len(parameter_switcher["youngs_modulus"][1:]) + 1, 1)
    for i in num:
        subprocess.run('/prog/abaqus/2020/bin/abaqus interactive job=Job-' + str(i) + '.inp mp_mode=threads parallel=domain cpus=32 domains=32',
                       shell=True, check=True)
    subprocess.run(['/prog/abaqus/2020/bin/abaqus', 'cae', 'noGUI=abq_result_export.py', '--', str(parameter_switcher[key_parameter][0:])])

    endtime = datetime.datetime.now()
    print('runtime =', endtime - starttime)