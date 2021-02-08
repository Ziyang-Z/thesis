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
import numpy as np
import random
import math
import sys
import os


# define noise center point area, r is the radius of this area, equal to the gravel's radius

r = 5E-3

# define noise area, N is the radius of noise area

N = r

# Length, depth, width describe the geometric parameter of the gravel grid
# 0. 001 is to ensure that the value '1.45-2*r' can also be chosen, because the domain of arrange is [start, stop)
# Depth is equal to width

Length = 1.45 - 2*r + 0.0001
Depth = 0.1 - 2*r + 0.0001
Length_start = 0.01
Depth_start = 0.01


def get_arg(a, b):
    delta_x = float(a)
    delta_y = float(b)
    delta_z = float(b)
    return delta_x, delta_y, delta_z


def generate_grid(delta_x, delta_y, delta_z):
    grdi_list = []
    x = [round(i, 2) for i in np.arange(Length_start, Length, delta_x)]
    y = [round(i, 2) for i in np.arange(Depth_start, Depth, delta_y)]
    z = [round(i, 2) for i in np.arange(Depth_start, Depth, delta_z)]
    for x_point in x:
        for y_point in y:
            for z_point in z:
                dx = random.uniform(x_point - N, x_point + N)
                dy = random.uniform(y_point - N, y_point + N)
                dz = random.uniform(z_point - N, z_point + N)
                grdi_list.append((dx, dy, dz))
    return grdi_list


def collide_check(a, b):
    if Length_start - N < r:
        raise Exception("Error: gravels out of the boundary at YZ-plane! Modify 'Length_start' again!")
    if Depth_start - N < r:
        raise Exception("Error: gravels out of the boundary at rectangular-plane! Modify 'Depth_start' again!")
    else:
        print('Feasible at the boundary!')
        delta_x, delta_y, delta_z = get_arg(a, b)
        if delta_x - 2*N < 2*r:
            raise Exception("Error: the gravels may get collide in x-direction! Modify 'a' again!")
        if delta_z - 2*N < 2*r:
            raise Exception("Error: the gravels may get collide in y- or z-direction! Modify 'b' again!")
            # N = 0.99 * (delta_z - 2 * r) / 2
        else:
            print("'N' is feasible for the further functions!")


session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)


def set_work_directory(path):
    os.chdir(path)


# create concrete part/ 3D sketching
def create_concrete_part(length, width, depth):
    mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=5.0)  # this will create the 2d planar sheet for sketching
    mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(0.0, 0.0), point2=(length, width))  # sketching is done
    mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Concrete', type=DEFORMABLE_BODY)  # making it 3d
    mdb.models['Model-1'].parts['Concrete'].BaseSolidExtrude(depth=depth, sketch=mdb.models['Model-1'].sketches[
        '__profile__'])  # extruding based on the depth value and making it a solid
    del mdb.models['Model-1'].sketches['__profile__']


def create_gravel_part(radius):
    # create gravel part/ 3D sketching
    mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=1.0)  # for drawing the sketch ie semi circle
    mdb.models['Model-1'].sketches['__profile__'].ConstructionLine(point1=(0.0, -5E-2), point2=(0.0, 5E-2))  # construction line for revolving the semi circle
    mdb.models['Model-1'].sketches['__profile__'].FixedConstraint(entity=mdb.models['Model-1'].sketches['__profile__'].geometry[2])
    mdb.models['Model-1'].sketches['__profile__'].ArcByCenterEnds(center=(0.0, 0.0), direction=CLOCKWISE,
                                                                  point1=(0.0, -radius),
                                                                  point2=(0.0, radius))  # Generating the arc
    mdb.models['Model-1'].sketches['__profile__'].Line(point1=(0.0, -radius),
                                                       point2=(0.0, radius))  # Closing the arc to create semi circle
    mdb.models['Model-1'].sketches['__profile__'].VerticalConstraint(entity=mdb.models['Model-1'].sketches['__profile__'].geometry[4])
    mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Gravel', type=DEFORMABLE_BODY)  # Setting the type and dimensionality of the sketch ie it should be 3d
    mdb.models['Model-1'].parts['Gravel'].BaseSolidRevolve(angle=360.0, flipRevolveDirection=OFF, sketch=mdb.models['Model-1'].sketches['__profile__'])  # Revolving the geometry
    del mdb.models['Model-1'].sketches['__profile__']  # delete the sketch


# Define material properties of Concrete
def material_properties_concrete(density, youngs_modulus, poissons_ratio, damping_alpha, damping_beta):
    mdb.models['Model-1'].Material(name='concrete')
    mdb.models['Model-1'].materials['concrete'].Density(table=((density,),))
    mdb.models['Model-1'].materials['concrete'].Elastic(table=((youngs_modulus, poissons_ratio),))
    mdb.models['Model-1'].materials['concrete'].Damping(alpha=damping_alpha, beta=damping_beta)
    mdb.models['Model-1'].HomogeneousSolidSection(name='concrete', material='concrete', thickness=None)
    p = mdb.models['Model-1'].parts['Concrete']
    c = p.cells
    cells = c.findAt(((0.725, 0.05, 0.05),))
    region = p.Set(cells=cells, name='Set-1')
    mdb.models['Model-1'].parts['Concrete'].SectionAssignment(region=region,
                                                              sectionName='concrete',
                                                              offset=0.0,
                                                              offsetType=MIDDLE_SURFACE,
                                                              offsetField='',
                                                              thicknessAssignment=FROM_SECTION)
    mdb.models['Model-1'].rootAssembly.Instance(name='Concrete-1', part=mdb.models['Model-1'].parts['Concrete'],
                                                dependent=ON)


# Define material properties of Gravel
def material_properties_gravel(density, youngs_modulus, poissons_ratio):
    mdb.models['Model-1'].Material(name='gravel')
    mdb.models['Model-1'].materials['gravel'].Density(table=((density,),))
    mdb.models['Model-1'].materials['gravel'].Elastic(table=((youngs_modulus, poissons_ratio),))
    mdb.models['Model-1'].HomogeneousSolidSection(name='gravel', material='gravel', thickness=None)
    region = mdb.models['Model-1'].parts['Gravel'].Set(cells=mdb.models['Model-1'].parts['Gravel'].cells.findAt(((0, 0, 0), ),), name='Set-1')
    mdb.models['Model-1'].parts['Gravel'].SectionAssignment(region=region,
                                                            sectionName='gravel',
                                                            offset=0.0,
                                                            offsetType=MIDDLE_SURFACE,
                                                            offsetField='',
                                                            thicknessAssignment=FROM_SECTION)


# Create instances and get holes by cutting
def apply_translate():
    s = 0
    for i in np.array(grid_list):
        s = s+1
        mdb.models['Model-1'].rootAssembly.Instance(name='Gravel_' + str(s), part=mdb.models['Model-1'].parts['Gravel'], dependent=ON)
        mdb.models['Model-1'].rootAssembly.translate(instanceList=('Gravel_' + str(s),), vector=tuple(i))


def embedded():
    a = mdb.models['Model-1'].rootAssembly
    s = 0
    for i in np.array(grid_list):
        s = s+1
        c = a.instances['Gravel_' + str(s)].cells
        cells = c.findAt(((tuple(i)),))
        region1 = a.Set(cells=cells, name='allG' + str(s))
        a = mdb.models['Model-1'].rootAssembly
        region2 = a.instances['Concrete-1'].sets['Set-1']
        mdb.models['Model-1'].EmbeddedRegion(name='Constraint-' + str(s),
                                             embeddedRegion=region1, hostRegion=region2,
                                             weightFactorTolerance=1e-06, absoluteTolerance=0.0,
                                             fractionalTolerance=0.05, toleranceMethod=BOTH)


# Mesh for ConcreteBeam
def apply_mesh_concrete(meshSize):
    p = mdb.models['Model-1'].parts['Concrete']
    p.seedPart(size=meshSize, deviationFactor=0.1, minSizeFactor=0.1)
    p = mdb.models['Model-1'].parts['Concrete']
    p.generateMesh()


# Mesh for Gravel
def apply_mesh_gravel(meshSize):
    mdb.models['Model-1'].parts['Gravel'].DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=0.0)
    mdb.models['Model-1'].parts['Gravel'].DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=0.0)
    mdb.models['Model-1'].parts['Gravel'].DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=0.0)
    mdb.models['Model-1'].parts['Gravel'].PartitionCellByDatumPlane(
        datumPlane=mdb.models['Model-1'].parts['Gravel'].datums[3],
        cells=mdb.models['Model-1'].parts['Gravel'].cells.getSequenceFromMask(mask=('[#1 ]',), ))
    mdb.models['Model-1'].parts['Gravel'].PartitionCellByDatumPlane(
        datumPlane=mdb.models['Model-1'].parts['Gravel'].datums[5],
        cells=mdb.models['Model-1'].parts['Gravel'].cells.getSequenceFromMask(mask=('[#3 ]',), ))
    mdb.models['Model-1'].parts['Gravel'].PartitionCellByDatumPlane(
        datumPlane=mdb.models['Model-1'].parts['Gravel'].datums[4],
        cells=mdb.models['Model-1'].parts['Gravel'].cells.getSequenceFromMask(mask=('[#f ]',), ))
    mdb.models['Model-1'].parts['Gravel'].seedPart(size=meshSize, deviationFactor=0.1, minSizeFactor=0.1)
    mdb.models['Model-1'].parts['Gravel'].generateMesh()


def apply_analysisstep(timeincrement):
    mdb.models['Model-1'].ExplicitDynamicsStep(name='Step-1', previous='Initial',
                                               timeIncrementationMethod=FIXED_USER_DEFINED_INC, timePeriod=5,
                                               userDefinedInc=timeincrement,
                                               nlgeom=OFF, improvedDtMethod=ON)


def apply_boundary_conditions():
    edges1 = mdb.models['Model-1'].rootAssembly.instances['Concrete-1'].edges.findAt(((0, 0, 0.05), ))
    region = mdb.models['Model-1'].rootAssembly.Set(edges=edges1, name='left')
    mdb.models['Model-1'].DisplacementBC(name='Left',
                                         createStepName='Initial', region=region, u1=SET, u2=SET, u3=SET,
                                         ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET,
                                         distributionType=UNIFORM, fieldName='', localCsys=None)
    edges1 = mdb.models['Model-1'].rootAssembly.instances['Concrete-1'].edges.findAt(((1.45, 0, 0.05),))
    region = mdb.models['Model-1'].rootAssembly.Set(edges=edges1, name='right')
    mdb.models['Model-1'].DisplacementBC(name='Right',
                                         createStepName='Initial', region=region, u1=UNSET, u2=SET, u3=SET,
                                         ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET,
                                         distributionType=UNIFORM, fieldName='', localCsys=None)


def apply_amplitude():
    mdb.models['Model-1'].TabularAmplitude(name='Amp-1',
                                           timeSpan=STEP,
                                           smooth=SOLVER_DEFAULT,
                                           data=((0.0, 0.0), (0.001, 1000.0), (0.001001, 0.0), (5.0, 0.0)))


def arithmetic_sequence(meshSize):
    d = (0.1/meshSize + 1)**2
    print('d =', d)
    a1 = 1 + (0.1/meshSize + 1)*(0.1/meshSize/2)
    print('a1 =', a1)
    n = 1.45/meshSize + 1
    print('n =', n)
    an = a1 + (n - 1)*d
    print('an =', an)
    m = int(1.45/meshSize//100)        # output required on 100 points, or near to 100 points
    nodes = np.arange(int(a1), int(an+1), int(m*d))
    print(nodes)
    D = len(nodes)
    print(D)
    return nodes


def apply_load(meshSize, Load):
    node_list = arithmetic_sequence(meshSize)
    fn = node_list[-48]          # the node near x=1/3*length(y=z=0.05)
    print(fn)
    p = mdb.models['Model-1'].parts['Concrete']
    n = p.nodes
    nodes = n[fn-1:fn]
    p.Set(nodes=nodes, name='force')
    a = mdb.models['Model-1'].rootAssembly
    region = a.instances['Concrete-1'].sets['force']
    mdb.models['Model-1'].ConcentratedForce(name='Force',
                                            createStepName='Step-1',
                                            region=region,
                                            cf2=Load,
                                            amplitude='Amp-1',
                                            distributionType=UNIFORM,
                                            field='',
                                            localCsys=None)


def apply_history_output_request(meshSize):
    num = arithmetic_sequence(meshSize)
    p = mdb.models['Model-1'].parts['Concrete']
    n = p.nodes
    for i in num:
        node = n[i - 1: i]
        p = mdb.models['Model-1'].parts['Concrete']
        p.Set(nodes=node, name='HOR' + str(i))
        regionDef = mdb.models['Model-1'].rootAssembly.allInstances['Concrete-1'].sets['HOR' + str(i)]
        mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-' + str(i),
                                                   createStepName='Step-1', variables=('U1', 'U2', 'U3'),
                                                   frequency=1,
                                                   region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
    del mdb.models['Model-1'].fieldOutputRequests['F-Output-1']
    del mdb.models['Model-1'].historyOutputRequests['H-Output-1']


def record_input_signal():
    regionDef = mdb.models['Model-1'].rootAssembly.allInstances['Concrete-1'].sets['force']
    mdb.models['Model-1'].HistoryOutputRequest(name='Input', createStepName='Step-1',
                                               variables=('CF2', ), frequency=1,
                                               region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)


def apply_job():
    mdb.Job(name='Job-1', model='Model-1', type=ANALYSIS, resultsFormat=ODB,
            parallelizationMethodExplicit=DOMAIN, numDomains=32,
            activateLoadBalancing=False, multiprocessingMode=THREADS, numCpus=32)
    # mdb.jobs['Job-1'].writeInput(consistencyChecking=OFF)
    mdb.jobs['Job-1'].submit(consistencyChecking=OFF)
    mdb.jobs['Job-1'].waitForCompletion()


if __name__ == "__main__":
    # set_work_directory(r"/home/zhangzia/Schreibtisch/studienarbeit/runtime")
    # create the girder with geometric parameter: length, width, depth.
    create_concrete_part(1.45, 0.1, 0.1)
    # radius of gravel
    create_gravel_part(5E-3)
    # modify the material properties of the girder: density, youngs_modulus, poissons_ratio, alpha and beta for damping.
    material_properties_concrete(2400.0, 3E10, 0.20, 7.1808, 0)
    # modify the material properties of the gravel: density, youngs_modulus, poissons_ratio.
    material_properties_gravel(2860.0, 7E10, 0.30)
    # gravel grid parameter: delta_x and delta_y.
    collide_check(2, 0.02)
    delta_x, delta_y, delta_z = get_arg(2, 0.02)
    grid_list = generate_grid(delta_x, delta_y, delta_z)
    G = len(grid_list)
    print(G)
    n = G
    apply_translate()
    embedded()
    # Mesh size
    apply_mesh_concrete(0.005)
    apply_mesh_gravel(0.002)
    # time increment
    apply_analysisstep(1E-6)
    apply_boundary_conditions()
    apply_amplitude()
    apply_load(0.005, -1)
    apply_history_output_request(0.005)
    record_input_signal()
    apply_job()
