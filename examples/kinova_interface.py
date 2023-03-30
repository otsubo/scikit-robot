#!/usr/bin/env python
import time

import skrobot
import numpy as np

def create_coords(x, y, z, roll, pitch, yaw):
    return skrobot.coordinates.Coordinates([x, y, z], [roll, pitch, yaw])

def solve_ik(robot, target):
    return robot.rarm.inverse_kinematics(target)

def add_sugar_box():
    sugar_box = skrobot.model.Box(
        extents=(0.038, 0.089, 0.175), face_colors=(0.3, 0.3, 0.0))
    sugar_box.translate(np.array([0.5, 0.0, 0.175/2]))
    viewer.add(sugar_box)
    viewer.redraw()

def add_cracker_box():
    cracker_box = skrobot.model.Box(
        extents=(0.06, 0.15, 0.21), face_colors=(0.3, 0.0, 0.0))
    cracker_box.translate(np.array([0.5, 0.2, 0.21/2]))
    viewer.add(cracker_box)
    viewer.redraw()

def sample_motion():
    add_sugar_box()
    add_cracker_box()
    target = create_coords(0.5, 0.2, 0.3, 3.14, 0, 3.14)
    robot.rarm.inverse_kinematics(target, rotation_axis=True)
    viewer.redraw()
    print("update robot pose")
    input()
    robot.rarm.move_end_pos([0, 0, 0.3], 'world')
    viewer.redraw()
    print("moveing above the object")
    input()
    ri.angle_vector(av=robot.angle_vector(), time=3.0)
    robot.rarm.move_end_pos([0, 0, -0.3], 'world')
    viewer.redraw()
    print("reaching the object")
    input()
    ri.angle_vector(av=robot.angle_vector(), time=3.0)
    robot.rarm.move_end_pos([0, 0, 0.1], 'world')
    viewer.redraw()
    print("picking up the object")
    input()
    ri.angle_vector(av=robot.angle_vector(), time=3.0)
    robot.reset_pose()
    viewer.redraw()
    print("moveing to the initial pose")
    input()
    ri.angle_vector(av=robot.angle_vector(), time=3.0)

robot = skrobot.models.Kinova()
ri = skrobot.interfaces.ros.KinovaROSRobotInterface(robot=robot,
                                                    joint_states_topic="/my_gen3/joint_states")
robot.reset_pose()
viewer = skrobot.viewers.TrimeshSceneViewer(resolution=(640, 480))
viewer.add(robot)
plane = skrobot.model.Box(
extents=(2, 2, 0.01), face_colors=(1.0, 1.0, 1.0))
viewer.add(plane)
viewer.set_camera(angles=[np.deg2rad(45), 0, 0], distance=4)
viewer.show()

import IPython; IPython.embed()
