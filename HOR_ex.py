from abaqus import *
from abaqusConstants import *
import __main__

from part import *
from section import *
from material import *
from assembly import *
from mesh import *
from step import *
from interaction import *
from load import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
from odbAccess import *
import csv
import numpy as np


def arithmetic_sequence(meshSize):
    d = (0.1/meshSize + 1)**2
    a1 = 1 + (0.1/meshSize + 1)*(0.1/meshSize/2)
    n = 1.45/meshSize + 1
    an = a1 + (n - 1)*d
    nodes = np.arange(int(a1), int(an), int(d))
    return nodes


def write_data_csv(meshSize, loc_job, loc_empty):
    path = loc_job
    odb = session.openOdb(name=(path))
    step1 = odb.steps['Step-1']

    num = arithmetic_sequence(meshSize)

    force_node = num[-9]
    region = step1.historyRegions['Node CONCRETE-1.' + str(force_node)]
    input_Data = region.historyOutputs['CF2'].data

    path = loc_empty
    file = 'input.csv'
    with open(os.path.join(path, file), 'w') as csv.file:
        pass

    path = loc_empty + '/' + file
    file1 = open(path, 'wb')
    writer = csv.writer(file1, dialect='excel')
    writer.writerow(["time_step", "force"])

    for row in input_Data:
        writer.writerow(row)
    print("Write data sucessful")
    file1.close()

    for i in num:
        region = step1.historyRegions['Node CONCRETE-1.' + str(i)]
        # region = step1.historyRegions.items()
        u1Data = region.historyOutputs['U1'].data

        path = loc_empty
        file = 'x-Dis-' + str(i) + '.csv'
        with open(os.path.join(path, file), 'w') as csv.file:
            pass

        path = loc_empty + '/' + file
        file1 = open(path, 'wb')
        writer = csv.writer(file1, dialect='excel')
        writer.writerow(["time_step", "x_disp"])

        for row in u1Data:
            writer.writerow(row)
        print("Write data sucessful")
        file1.close()


write_data_csv(0.05, 'C:/temp/Job-1.odb', 'C:/Users/ZZY/Desktop/database')
# code = arithmetic_sequence(0.05)
# print(code)