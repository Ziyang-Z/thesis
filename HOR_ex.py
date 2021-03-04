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
import datetime
import math
import os


# =============================================================================
# this python file is for Hostory data exporting, which are exported into csv files.
# =============================================================================
mesh_size_girder = 0.01
path_csv_storage = os.path.abspath('csv')
path_job = os.path.abspath('Job-1.odb')


def line_node_list(mesh_size):
    d = (width_girder/mesh_size + 1)**2
    a1 = 1 + (width_girder/mesh_size + 1)*(width_girder/mesh_size/2)
    n = length_girder/mesh_size + 1
    an = a1 + (n - 1)*d
    m = int(length_girder / mesh_size // 100)  # output required on 100 points, or near to 100 points
    nodes = np.arange(int(a1), int(an+1), int(m*d))
    print(nodes)
    return nodes


def test_node_list():
    d = (width_girder / 0.01 + 1) ** 2
    a1 = [37, 41, 81, 85]
    n = length_girder / 0.01 + 1
    an = []
    for i in a1:
        x = i + (n - 1) * d
        an.append(i)
        an.append(int(x))

    a1 = [34, 78]
    n = [49, 98]
    for i in a1:
        for j in n:
            x = i + (j - 1) * d
            an.append(int(x))

    a1 = [4, 8, 114, 118]
    n = [49, 98]
    for i in a1:
        for j in n:
            x = i + (j - 1) * d
            an.append(int(x))
    an.sort()
    print(an)
    # an.reverse()
    return an


def write_data_csv(mesh_size, loc_job, loc_empty, type=''):
    an = test_node_list()

    path = loc_job
    odb = session.openOdb(name=(path))
    step1 = odb.steps['Step-1']

    num = line_node_list(mesh_size)

    force_node = num[-48]
    region = step1.historyRegions['Node CONCRETE-1.' + str(force_node)]
    input_Data = region.historyOutputs['CF2'].data

    print('Data output starts!')
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

    if type == 'export_146':
        for i in num:
            region = step1.historyRegions['Node CONCRETE-1.' + str(i)]
            # region = step1.historyRegions.items()
            u1_data = region.historyOutputs['U1'].data

            path = loc_empty
            file = 'x-Dis-' + str(i) + '.csv'
            with open(os.path.join(path, file), 'w') as csv.file:
                pass

            path = loc_empty + '/' + file
            file1 = open(path, 'wb')
            writer = csv.writer(file1, dialect='excel')
            writer.writerow(["time_step", "x_disp"])

            for row in u1_data:
                writer.writerow(row)
            print("Write data sucessful")
            file1.close()

    if type == 'export_20':
        for i in an:
            region = step1.historyRegions['Node CONCRETE-1.' + str(i)]
            u1_data = region.historyOutputs['U1'].data

            path = loc_empty
            file = 'x-Dis-' + str(i) + '.csv'
            with open(os.path.join(path, file), 'w') as csv.file:
                pass

            path = loc_empty + '/' + file
            file1 = open(path, 'wb')
            writer = csv.writer(file1, dialect='excel')
            writer.writerow(["time_step", "x_disp"])

            for row in u1_data:
                writer.writerow(row)
            print("Write data sucessful")
            file1.close()


def hor_export(mesh_size):
    starttime = datetime.datetime.now()
    write_data_csv(mesh_size,
                   path_job,
                   path_csv_storage,
                   type='export_20')
    print('All data output is complete!')
    endtime = datetime.datetime.now()
    time = endtime - starttime
    print('runtime =', time)


hor_export(mesh_size_girder)

