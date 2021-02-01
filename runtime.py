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
from xyPlot import *
from connectorBehavior import *
from odbAccess import *
import numpy as np
import random
import math
import csv
import sys
import os


session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)


# create concrete part/ 3D sketching
def create_concrete_part():
    mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                            sheetSize=5.0)  # this will create the 2d planar sheet for sketching
    mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(0.0, 0.0), point2=(1.45, 0.1))  # sketching is done
    mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Concrete', type=DEFORMABLE_BODY)  # making it 3d
    mdb.models['Model-1'].parts['Concrete'].BaseSolidExtrude(depth=0.1, sketch=mdb.models['Model-1'].sketches[
        '__profile__'])  # extruding based on the depth value and making it a solid
    del mdb.models['Model-1'].sketches['__profile__']


# Define material properties of Concrete
def material_properties_concrete():
    mdb.models['Model-1'].Material(name='concrete')
    mdb.models['Model-1'].materials['concrete'].Density(table=((2500.0,),))
    mdb.models['Model-1'].materials['concrete'].Elastic(table=((30000000000.0, 0.20),))
    mdb.models['Model-1'].HomogeneousSolidSection(name='concrete', material='concrete', thickness=None)
    region = mdb.models['Model-1'].parts['Concrete'].Set(
        cells=mdb.models['Model-1'].parts['Concrete'].cells.getSequenceFromMask(mask=('[#1 ]',), ), name='Set-1')
    mdb.models['Model-1'].parts['Concrete'].SectionAssignment(region=region,
                                                              sectionName='concrete',
                                                              offset=0.0,
                                                              offsetType=MIDDLE_SURFACE,
                                                              offsetField='',
                                                              thicknessAssignment=FROM_SECTION)


def mesh_concrete():
    p = mdb.models['Model-1'].parts['Concrete']
    p.seedPart(size=0.01, deviationFactor=1E-4, minSizeFactor=1E-4)
    p = mdb.models['Model-1'].parts['Concrete']
    p.generateMesh()
    a = mdb.models['Model-1'].rootAssembly
    a.regenerate()


def create_analysisstep():
    mdb.models['Model-1'].ExplicitDynamicsStep(name='Step-1', previous='Initial', timePeriod=3,
                                               timeIncrementationMethod=FIXED_USER_DEFINED_INC, userDefinedInc=2E-6,
                                               nlgeom=OFF, improvedDtMethod=ON)


def apply_amplitude():
    mdb.models['Model-1'].TabularAmplitude(name='Amp-1',
                                           timeSpan=STEP,
                                           smooth=SOLVER_DEFAULT,
                                           data=((0.0, 0.0), (0.001, 1000.0), (0.001001, 0.0), (3.0, 0.0)))


def apply_load():
    mdb.models['Model-1'].rootAssembly.Instance(name='Concrete-1', part=mdb.models['Model-1'].parts['Concrete'], dependent=ON)
    a = mdb.models['Model-1'].rootAssembly
    v1 = a.instances['Concrete-1'].vertices
    verts1 = v1.getSequenceFromMask(mask=('[#4 ]',), )
    region = a.Set(vertices=verts1, name='Set-1')
    mdb.models['Model-1'].ConcentratedForce(name='Load-1', createStepName='Step-1',
                                            region=region, cf2=-1, amplitude='Amp-1',
                                            distributionType=UNIFORM, field='',
                                            localCsys=None)


def arithmetic_sequence(meshSize):
    d = (0.1/meshSize + 1)**2
    a1 = 1 + (0.1/meshSize + 1)*(0.1/meshSize/2)
    n = 1.45/meshSize + 1
    an = a1 + (n - 1)*d
    nodes = np.arange(int(a1), int(an), int(d))
    return nodes


def nodes(meshSize):
    num = arithmetic_sequence(meshSize)
    p = mdb.models['Model-1'].parts['Concrete']
    n = p.nodes
    for i in num:
        node = n[i-1: i]
        p = mdb.models['Model-1'].parts['Concrete']
        p.Set(nodes=node, name='HOR' + str(i))
        regionDef = mdb.models['Model-1'].rootAssembly.allInstances['Concrete-1'].sets['HOR' + str(i)]
        mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-' + str(i),
                                                   createStepName='Step-1', variables=('U1', 'U2', 'U3'), frequency=1,
                                                   region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)

# def nodes():
#     # nodes = np.arange(4, 266, 9)
#     # print(nodes)
#     # s = 0
#     # for i in nodes:
#     #     s = s + 1
#     #       N = n[str(i-1): str(i)]
#     N = "mdb.models['Model-1'].parts['Concrete'].nodes[" + str(3) + ':' + str(4) + ']'
#     # print(N)
#     node = N
#     p = mdb.models['Model-1'].parts['Concrete']
#     p.Set(nodes=node, name='HOR')


# def nodes():
#     nodes = np.arange(4, 266, 9)
#     print(nodes)
#     # Nodes = []
#     p = mdb.models['Model-1'].parts['Concrete']
#     n = p.nodes
#     node = n[3:4]
#     # for i in nodes:
#     #     p = mdb.models['Model-1'].parts['Concrete']
#     #     n = p.nodes
#     #     N = str(n) + '[' + str(i-1) + ':' + str(i) + ']'
#     #     # print(N)
#     #     Nodes.append(N)
#     return node


# def history_output():
#     # Nodes = nodes()
#     # str1 = '+'
#     # str2 = tuple(str1)
#     # node = str2.join(tuple(Nodes))
#     # p = mdb.models['Model-1'].parts['Concrete']
#     # p.Set(nodes=node, name='HOR')
#     regionDef = mdb.models['Model-1'].rootAssembly.allInstances['Concrete-1'].sets['HOR']
#     mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-2',
#                                                createStepName='Step-1', variables=('U1', 'U2', 'U3'), frequency=1,
#                                                region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)


def submit_job():
    mdb.Job(name='Job-1', model='Model-1', description='', type=ANALYSIS,
            atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=80,
            memoryUnits=PERCENTAGE, explicitPrecision=SINGLE,
            nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF,
            contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='',
            resultsFormat=ODB)
            # , parallelizationMethodExplicit=DOMAIN, numDomains=8,
            # activateLoadBalancing=False, multiprocessingMode=THREADS, numCpus=8)
    mdb.jobs['Job-1'].submit(consistencyChecking=OFF)
    mdb.jobs['Job-1'].waitForCompletion()


def write_data_csv(meshSize, loc_job, loc_empty):
    path = loc_job
    odb = session.openOdb(name=(path))
    step1 = odb.steps['Step-1']
    num = arithmetic_sequence(meshSize)
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


if __name__ == "__main__":
    start = time.time()
    create_concrete_part()
    material_properties_concrete()
    mesh_concrete()
    create_analysisstep()
    apply_amplitude()
    apply_load()
    nodes(0.05)
    submit_job()
    write_data_csv(0.05,
                   '/home/zhangzia/Schreibtisch/studienarbeit/practice',
                   '/home/zhangzia/Schreibtisch/studienarbeit/practice/csv')

