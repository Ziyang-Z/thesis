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
import csv
import random
import math
import sys
import os

import abq_node_list as nl


def generate_grid(delta_x, delta_y, delta_z):
    grid_list = []
    x = [round(i, 2) for i in np.arange(grid_left_limit_length, grid_right_limit_length, delta_x)]
    y = [round(i, 2) for i in np.arange(grid_left_limit_width, grid_right_limit_width, delta_y)]
    z = [round(i, 2) for i in np.arange(grid_left_limit_depth, grid_right_limit_depth, delta_z)]
    for x_point in x:
        for y_point in y:
            for z_point in z:
                dx = random.uniform(x_point - noise_radius, x_point + noise_radius)
                dy = random.uniform(y_point - noise_radius, y_point + noise_radius)
                dz = random.uniform(z_point - noise_radius, z_point + noise_radius)
                grid_list.append((dx, dy, dz))
    return grid_list


def collide_check():
    if grid_left_limit_length - noise_radius < radius_gravel:
        raise Exception("Error: gravels out of the boundary at YZ-plane! Modify 'grid_left_limit_length' again!")
    if grid_left_limit_depth - noise_radius < radius_gravel:
        raise Exception("Error: gravels out of the boundary at rectangular-plane! Modify 'grid_left_limit_depth' again!")
    else:
        print('Feasible at the boundary!')
        delta_x = float(delta_x_gravel)
        delta_z = float(delta_yz_gravel)
        if delta_x - 2*noise_radius < 2*radius_gravel:
            raise Exception("Error: the gravels may get collide in x-direction! Modify 'delta_x' again!")
        if delta_z - 2*noise_radius < 2*radius_gravel:
            raise Exception("Error: the gravels may get collide in y- or z-direction! Modify 'delta_y' again!")
            # noise_radius = 0.99 * (delta_z - 2 * radius_gravel) / 2
        else:
            print("'noise_radius' is feasible for the further functions!")


# create concrete part/ 3D sketching
def create_girder(length, width, depth):
    mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=5.0)  # this will create the 2d planar sheet for sketching
    mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(0.0, 0.0), point2=(length, width))  # sketching is done
    mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Concrete', type=DEFORMABLE_BODY)  # making it 3d
    mdb.models['Model-1'].parts['Concrete'].BaseSolidExtrude(depth=depth, sketch=mdb.models['Model-1'].sketches[
        '__profile__'])  # extruding based on the depth value and making it a solid
    del mdb.models['Model-1'].sketches['__profile__']
    mdb.models['Model-1'].rootAssembly.Instance(name='Concrete-1', part=mdb.models['Model-1'].parts['Concrete'],
                                                dependent=ON)


def create_aggregate(radius):
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
def insert_aggregates():
    s = 0
    for i in np.array(grid_list):
        s = s+1
        mdb.models['Model-1'].rootAssembly.Instance(name='Gravel_' + str(s), part=mdb.models['Model-1'].parts['Gravel'], dependent=ON)
        mdb.models['Model-1'].rootAssembly.translate(instanceList=('Gravel_' + str(s),), vector=tuple(i))

    a = mdb.models['Model-1'].rootAssembly
    s = 0
    for i in np.array(grid_list):
        s = s+1
        c = a.instances['Gravel_' + str(s)].cells
        cells = c.findAt(((tuple(i)),))
        region1 = a.Set(cells=cells, name='gravel' + str(s))
        a = mdb.models['Model-1'].rootAssembly
        region2 = a.instances['Concrete-1'].sets['Set-1']
        mdb.models['Model-1'].EmbeddedRegion(name='Constraint-' + str(s),
                                             embeddedRegion=region1, hostRegion=region2,
                                             weightFactorTolerance=1e-06, absoluteTolerance=0.0,
                                             fractionalTolerance=0.05, toleranceMethod=BOTH)


# Mesh for ConcreteBeam
def mesh_model(mesh_size_girder, mesh_size_aggregate):
    p = mdb.models['Model-1'].parts['Concrete']
    p.seedPart(size=mesh_size_girder, deviationFactor=0.1, minSizeFactor=0.1)
    p = mdb.models['Model-1'].parts['Concrete']
    p.generateMesh()

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
    mdb.models['Model-1'].parts['Gravel'].seedPart(size=mesh_size_aggregate, deviationFactor=0.1, minSizeFactor=0.1)
    mdb.models['Model-1'].parts['Gravel'].generateMesh()


def apply_analysisstep(duration, timeincrement):
    mdb.models['Model-1'].ExplicitDynamicsStep(name='Step-1', previous='Initial',
                                               timeIncrementationMethod=FIXED_USER_DEFINED_INC, timePeriod=duration,
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
    
    
def read_excitation(excitation_file_path):
    with open(excitation_file_path, 'rt') as csv_file:
        reader = csv.DictReader(csv_file)
        time = []
        force = []
        for row in reader:
            time.append(float(row['time_step']))
            force.append(float(row['force']))
    data = list(zip(time, force))
        
    return data


def apply_amplitude(excitation_file_path):
    data = read_excitation(excitation_file_path)
    mdb.models['Model-1'].TabularAmplitude(name='Amp-1',
                                           timeSpan=STEP,
                                           smooth=SOLVER_DEFAULT,
                                           data=data)


def apply_load(Load):
    force_node = nl.set_force_node()
    p = mdb.models['Model-1'].parts['Concrete']
    n = p.nodes
    nodes = n[force_node-1:force_node]
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


def define_history_output():
    num = nl.main()
    print('the selected nodes are ', num)
    print(len(num))
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

    regionDef = mdb.models['Model-1'].rootAssembly.allInstances['Concrete-1'].sets['force']
    mdb.models['Model-1'].HistoryOutputRequest(name='Input', createStepName='Step-1',
                                               variables=('CF2', ), frequency=1,
                                               region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)


def write_input_file(n):
    mdb.Job(name='Job-' + str(n), model='Model-1', type=ANALYSIS, resultsFormat=ODB)
    mdb.jobs['Job-' + str(n)].writeInput(consistencyChecking=OFF)
    mdb.jobs['Job-' + str(n)].waitForCompletion()


def main(n):
    create_girder(length_girder, width_girder, depth_girder)
    create_aggregate(radius_gravel)

    material_properties_concrete(density_girder, youngs_modulus_girder, poissons_ratio_girder, alpha_damping_girder, beta_damping_girder)
    material_properties_gravel(density_gravel, youngs_modulus_gravel, poissons_ratio_gravel)

    if aggregates_insert:
        insert_aggregates()
        print('this is the analysis of the concrete with aggregates')
    else:
        print('this is the analysis of the concrete only')

    mesh_model(mesh_size_girder, mesh_size_aggregate)

    apply_analysisstep(duration, time_step)
    apply_boundary_conditions()

    apply_amplitude(path_excitation)

    apply_load(load)
    define_history_output()
    write_input_file(n)


if __name__ == '__main__':
    mesh_size_girder = 0.01
    length_girder = 1.45
    width_girder = 0.10
    depth_girder = 0.10
    density_girder = 2400.0
    youngs_modulus_girder = 3E10
    poissons_ratio_girder = 0.20
    alpha_damping_girder = 12.5651
    beta_damping_girder = 1.273E-8

    radius_gravel = 0.005
    mesh_size_aggregate = 0.002
    delta_x_gravel = 0.110
    delta_y_gravel = 0.02
    delta_z_gravel = 0.02
    density_gravel = 2860
    youngs_modulus_gravel = 5E10
    poissons_ratio_gravel = 0.30

    noise_radius = radius_gravel
    grid_right_limit_length = 1.35 - 2*radius_gravel + 0.0001
    grid_right_limit_width = 0.1 - 2*radius_gravel + 0.0001
    grid_right_limit_depth = 0.1 - 2*radius_gravel + 0.0001
    grid_left_limit_length = 0.01
    grid_left_limit_width = 0.01
    grid_left_limit_depth = 0.01

    time_step = 1E-6
    duration = 3
    load = -1000

    path_excitation = os.path.abspath('excitation.csv')

    # call the parameters.
    parameter = sys.argv[-1]
    parameter = parameter.strip("[]").split(",")
    key = parameter[0].strip("'")
    print(key)
    value = list(map(float, parameter[1:]))
    print(value)
    parameter_dict = {}
    parameter_dict[key] = value
    print(parameter_dict)

    aggregates_insert = bool(sys.argv[-2])
    if aggregates_insert:
        # to fix the position of the aggregates, create the grid only once at first.
        grid_list = generate_grid(delta_x_gravel, delta_y_gravel, delta_y_gravel)
        collide_check()
        sum_aggregates = len(grid_list)
        print("the number of the aggregates is ", sum_aggregates)
    else:
        print("no aggregates!")

    if 'load' == key:
        s = 1
        for i in parameter_dict[key]:
            load = i
            print('the parameter under analysis is load, value is ', load)
            main(s)
            s = s + 1

    elif 'youngs_modulus' == key:
        s = 1
        for i in parameter_dict[key]:
            youngs_modulus_gravel = i
            print('the parameter under analysis is youngs_modulus, value is ', youngs_modulus_gravel)
            main(s)
            s = s + 1

    elif 'size_aggregate' == key:
        s = 1
        for i in parameter_dict[key]:
            radius_gravel = i/2
            print('the parameter under analysis is size_aggregate, value is ', radius_gravel)
            main(s)
            s = s + 1