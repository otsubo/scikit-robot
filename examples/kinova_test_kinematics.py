#!/usr/bin/env python
import time

import skrobot
import numpy as np

robot = skrobot.models.Kinova()
robot.reset_pose()
viewer = skrobot.viewers.TrimeshSceneViewer(resolution=(640, 480))
viewer.add(robot)
plane = skrobot.model.Box(
extents=(2, 2, 0.01), face_colors=(1.0, 1.0, 1.0))
viewer.add(plane)
viewer.set_camera(angles=[np.deg2rad(45), 0, 0], distance=4)
viewer.show()

import ipdb; ipdb.set_trace()
target_coords = skrobot.coordinates.Coordinates([0.5, 0.0, 0.5], [1.57, 0, 1.57])
robot.rarm.inverse_kinematics(target_coords)
viewer.redraw()
target_coords = skrobot.coordinates.Coordinates([0.3, 0.3, 0.5], [0.0, 0, 3.14])
robot.rarm.inverse_kinematics(target_coords)
viewer.redraw()
target_coords = skrobot.coordinates.Coordinates([0.3, 0.0, 0.3], [0.0, 1.57, 1.57])
robot.rarm.inverse_kinematics(target_coords)
viewer.redraw()
