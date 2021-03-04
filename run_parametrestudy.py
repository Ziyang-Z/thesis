from matplotlib import pyplot as plt
import subprocess
import datetime
import time
import sys
import os
import tf_storage as tfs
import excitation as ex

if __name__ == "__main__":

    starttime = datetime.datetime.now()

    # for parametre_value in parametre:

    ex.main()
    subprocess.run(['/prog/abaqus/2020/bin/abaqus', 'cae', 'noGUI=abs_simu.py', '--', str(1)])
    subprocess.run('/prog/abaqus/2020/bin/abaqus interactive job=Job-1.inp mp_mode=threads parallel=domain cpus=32 domains=32',
                   shell=True, check=True)
    subprocess.run('/prog/abaqus/2020/bin/abaqus cae noGUI=HOR_ex.py', shell=True, check=True)
    tfs.main()

    endtime = datetime.datetime.now()
    print('runtime =', endtime - starttime)
