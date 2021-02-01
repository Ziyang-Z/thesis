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


r = 5E-3
N = r
# 0. 001 is to ensure that the value '1.45-2*r' can also be chosen, because the domain of arrange is [start, stop)
L = 1.45 - 2*r + 0.0001
D = 0.1 - 2*r + 0.0001
Lstart = 0.01
Dstart = 0.01


def get_arg(a, b):
    delta_x = float(a)
    delta_y = float(b)
    delta_z = float(b)
    return delta_x, delta_y, delta_z


def generate_grid(delta_x, delta_y, delta_z):
    grdi_list = []
    x = [round(i, 2) for i in np.arange(Lstart, L, delta_x)]
    y = [round(i, 2) for i in np.arange(Dstart, D, delta_y)]
    z = [round(i, 2) for i in np.arange(Dstart, D, delta_z)]
    for x_point in x:
        for y_point in y:
            for z_point in z:
                dx = random.uniform(x_point - N, x_point + N)
                dy = random.uniform(y_point - N, y_point + N)
                dz = random.uniform(z_point - N, z_point + N)
                grdi_list.append((dx, dy, dz))
    return grdi_list


def collide_check(a, b):
    if Lstart - N < r:
        raise Exception("Error: gravels out of the boundary at YZ-plane! Modify 'Lstart' again!")
    if Dstart - N < r:
        raise Exception("Error: gravels out of the boundary at rectangular-plane! Modify 'Dstart' again!")
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
def material_properties_concrete(density, ym, pr):
    mdb.models['Model-1'].Material(name='concrete')
    mdb.models['Model-1'].materials['concrete'].Density(table=((density,),))
    mdb.models['Model-1'].materials['concrete'].Elastic(table=((ym, pr),))
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
def material_properties_gravel(density, ym, pr):
    mdb.models['Model-1'].Material(name='gravel')
    mdb.models['Model-1'].materials['gravel'].Density(table=((density,),))
    mdb.models['Model-1'].materials['gravel'].Elastic(table=((ym, pr),))
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
        mdb.models['Model-1'].EmbeddedRegion(name='Constraint-' + str(s),
                                                 embeddedRegion=region1, hostRegion=None, weightFactorTolerance=1e-06,
                                                 absoluteTolerance=0.0, fractionalTolerance=0.05, toleranceMethod=BOTH)


# Mesh for ConcreteBeam
def apply_mesh_concrete(meshSize):
    p = mdb.models['Model-1'].parts['Concrete']
    e = p.edges
    pickedEdges = e.findAt(((0.0, 0.1, 0.05), ))         # upper Edge
    p.PartitionEdgeByParam(edges=pickedEdges, parameter=0.5)
    p = mdb.models['Model-1'].parts['Concrete']
    e = p.edges
    pickedEdges = e.findAt(((1.45, 0.1, 0.05), ))        # upper Edge
    p.PartitionEdgeByParam(edges=pickedEdges, parameter=0.5)
    p = mdb.models['Model-1'].parts['Concrete']
    e = p.edges
    pickedEdges = e.findAt(((0.0, 0.025, 0.1), ))        # right
    p.PartitionEdgeByParam(edges=pickedEdges, parameter=0.5)
    p = mdb.models['Model-1'].parts['Concrete']
    e = p.edges
    pickedEdges = e.findAt(((0.0, 0.025, 0.0), ))        # left
    p.PartitionEdgeByParam(edges=pickedEdges, parameter=0.5)
    p = mdb.models['Model-1'].parts['Concrete']
    f = p.faces
    pickedFaces = f.findAt(((0.0, 0.033333, 0.066667), ))
    v, e, d = p.vertices, p.edges, p.datums
    p.PartitionFaceByShortestPath(point1=v.findAt(coordinates=(0.0, 0.05, 0.1)),
        point2=v.findAt(coordinates=(0.0, 0.05, 0.0)), faces=pickedFaces)
    p = mdb.models['Model-1'].parts['Concrete']
    f = p.faces
    pickedFaces = f.findAt(((0.0, 0.083333, 0.016667), ))
    v1, e1, d1 = p.vertices, p.edges, p.datums
    p.PartitionFaceByShortestPath(point1=v1.findAt(coordinates=(0.0, 0.1, 0.05)),
        faces=pickedFaces, point2=p.InterestingPoint(edge=e1.findAt(
        coordinates=(0.0, 0.05, 0.025)), rule=MIDDLE))
    p = mdb.models['Model-1'].parts['Concrete']
    e = p.edges
    pickedEdges = e.findAt(((1.45, 0.075, 0.0), ))
    p.PartitionEdgeByParam(edges=pickedEdges, parameter=0.5)
    p = mdb.models['Model-1'].parts['Concrete']
    e = p.edges
    pickedEdges = e.findAt(((1.45, 0.075, 0.1), ))
    p.PartitionEdgeByParam(edges=pickedEdges, parameter=0.5)
    p = mdb.models['Model-1'].parts['Concrete']
    f = p.faces
    pickedFaces = f.findAt(((1.45, 0.066667, 0.066667), ))
    v, e, d = p.vertices, p.edges, p.datums
    p.PartitionFaceByShortestPath(point1=v.findAt(coordinates=(1.45, 0.05, 0.1)),
        point2=v.findAt(coordinates=(1.45, 0.05, 0)), faces=pickedFaces)
    p = mdb.models['Model-1'].parts['Concrete']
    f = p.faces
    pickedFaces = f.findAt(((1.45, 0.083333, 0.083333), ))
    v, e, d = p.vertices, p.edges, p.datums
    p.PartitionFaceByShortestPath(point1=v.findAt(coordinates=(1.45, 0.1, 0.05)),
        faces=pickedFaces, point2=p.InterestingPoint(edge=e.findAt(
        coordinates=(1.45, 0.05, 0.075)), rule=MIDDLE))
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
                                               timeIncrementationMethod=FIXED_USER_DEFINED_INC,timePeriod=5,
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


def apply_load(Load):
    p = mdb.models['Model-1'].rootAssembly.instances['Concrete-1']
    region = mdb.models['Model-1'].rootAssembly.Set(vertices=p.vertices.findAt(((0, 0.05, 0.05), )), name='force')
    mdb.models['Model-1'].ConcentratedForce(name='Force',
                                            createStepName='Step-1',
                                            region=region,
                                            cf1=Load,
                                            amplitude='Amp-1',
                                            distributionType=UNIFORM,
                                            field='',
                                            localCsys=None)


def apply_history_output_request():
    p = mdb.models['Model-1'].rootAssembly.instances['Concrete-1']
    mdb.models['Model-1'].rootAssembly.Set(vertices=p.vertices.findAt(((1.45, 0.05, 0.05),)), name='displacement node')
    mdb.models['Model-1'].HistoryOutputRequest(name='node displacement',
                                               createStepName='Step-1',
                                               variables=('U1', 'U2', 'U3'),
                                               frequency=1,
                                               region=mdb.models['Model-1'].rootAssembly.sets['displacement node'],
                                               sectionPoints=DEFAULT,
                                               rebar=EXCLUDE)


def apply_job():
    mdb.Job(name='Job-1', model='Model-1', description='', type=ANALYSIS,
            atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
            memoryUnits=PERCENTAGE, explicitPrecision=SINGLE,
            nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF,
            contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='',
            resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, numDomains=8,
            activateLoadBalancing=False, multiprocessingMode=THREADS, numCpus=8)
    mdb.jobs['Job-1'].submit(consistencyChecking=OFF)
    mdb.jobs['Job-1'].waitForCompletion()


if __name__ == "__main__":
    create_concrete_part(1.45, 0.1, 0.1)
    create_gravel_part(5E-3)
    material_properties_concrete(2400.0, 3E10, 0.20)
    material_properties_gravel(2860.0, 7E10, 0.30)
    collide_check(0.05, 0.02)
    delta_x, delta_y, delta_z = get_arg(0.05, 0.02)
    grid_list = generate_grid(delta_x, delta_y, delta_z)
    G = len(grid_list)
    print(G)
    n = G
    apply_translate()
    embedded()
    apply_mesh_concrete(0.01)
    apply_mesh_gravel(0.002)
    apply_analysisstep(1E-6)
    apply_boundary_conditions()
    apply_amplitude()
    apply_load(1)
    apply_history_output_request()
    apply_job()