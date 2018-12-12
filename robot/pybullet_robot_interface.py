import importlib

import numpy as np

from robot.math import quaternion2rpy
from robot.math import matrix2quaternion
from robot.robot_model import LinearJoint
from robot.robot_model import RotationalJoint


_available = False
_import_checked = False
p = None


def _check_available():
    global _available
    global _import_checked
    global p
    if not _import_checked:
        try:
            p = importlib.import_module('pybullet')
        except (ImportError, TypeError):
            _available = False
        finally:
            _import_checked = True
            _available = True
    if not _available:
        raise ImportError('pybullet is not installed on your environment, '
                          'so nothing will be drawn at this time. '
                          'Please install pybullet.\n\n'
                          '  $ pip install pybullet\n')


class PybulletRobotInterface(object):

    def __init__(self, robot, urdf_path=None, use_fixed_base=False,
                 connect=1, *args, **kwargs):
        _check_available()
        super(PybulletRobotInterface, self).__init__(*args, **kwargs)
        if urdf_path is None:
            if robot.urdf_path is not None:
                urdf_path = robot.urdf_path
            else:
                raise ValueError('urdf_path should be given.')
        self.robot = robot
        if connect == 2:
            p.connect(connect)
        elif connect == 1:
            try:
                p.connect(connect)
            except Exception as e:
                print(e)
        self.robot_id = p.loadURDF(urdf_path, [0, 0, 0],
                                   useFixedBase=use_fixed_base)

        self.load_bullet()
        self.realtime_simualtion = False

    @staticmethod
    def available():
        _check_available()
        return _available

    def load_bullet(self):
        joint_num = p.getNumJoints(self.robot_id)
        joint_ids = [None] * joint_num
        joint_name_to_joint_id = {}
        for i in range(len(joint_ids)):
            joint_name = p.getJointInfo(self.robot_id, i)[1]
            try:
                idx = self.robot.joint_names.index(joint_name.decode('utf-8'))
            except ValueError:
                continue
            if idx != -1:
                joint_ids[idx] = i
                joint_name_to_joint_id[joint_name.decode('utf-8')] = i
            else:
                joint_name_to_joint_id[joint_name.decode('utf-8')] = idx
        self.joint_ids = joint_ids
        self.joint_name_to_joint_id = joint_name_to_joint_id

        self.force = 200
        self.max_velcity = 1.0
        self.position_gain = 0.1
        self.target_velocity = 0.0
        self.velocity_gain = 0.1

    def angle_vector(self, angle_vector=None, realtime_simualtion=None):
        if realtime_simualtion is not None and isinstance(realtime_simualtion, bool):
            self.realtime_simualtion = realtime_simualtion

        if self.robot_id is None:
            return self.robot.angle_vector()
        if angle_vector is None:
            angle_vector = self.robot.angle_vector()

        for i, (joint, angle) in enumerate(zip(self.robot.joint_list, angle_vector)):
            idx = self.joint_name_to_joint_id[joint.name]

            joint = self.robot.joint_list[i]
            if isinstance(joint, RotationalJoint):
                angle = np.deg2rad(angle)
            elif isinstance(joint, LinearJoint):
                angle = 0.001 * angle
            else:
                raise ValueError('{} is not supported'.
                                 format(type(joint)))
            if self.realtime_simualtion is False:
                p.resetJointState(self.robot_id, idx, angle)

            p.setJointMotorControl2(bodyIndex=self.robot_id,
                                    jointIndex=idx,
                                    controlMode=p.POSITION_CONTROL,
                                    targetPosition=angle,
                                    targetVelocity=self.target_velocity,
                                    force=self.force,
                                    positionGain=self.position_gain,
                                    velocityGain=self.velocity_gain,
                                    maxVelocity=self.max_velcity)

        return angle_vector

    def wait_interpolation(self, thresh=0.05):
        while True:
            p.stepSimulation()
            wait = False
            for idx in self.joint_ids:
                if idx is None:
                    continue
                _, velocity, _, _ = p.getJointState(self.robot_id,
                                                    idx)
                if abs(velocity) > thresh:
                    wait = True
            if wait is False:
                break
        return True

    def sync(self):
        if self.robot_id is None:
            return self.angle_vector()

        for idx, joint in zip(self.joint_ids, self.robot.joint_list):
            if idx is None:
                continue
            joint_state = p.getJointState(self.robot_id,
                                          idx)
            joint.joint_angle(np.rad2deg(joint_state[0]))
        pos, orientation = p.getBasePositionAndOrientation(self.robot_id)
        rpy, _ = quaternion2rpy([orientation[3], orientation[0],
                                 orientation[1], orientation[2]])
        self.robot.root_link.newcoords(np.array([rpy[0], rpy[1], rpy[2]]),
                                       pos=pos)
        return self.angle_vector()


remove_user_item_indices = []


def draw(c):
    coord = c.copy_worldcoords()
    orientation = matrix2quaternion(coord.worldrot())
    orientation = np.array([orientation[1],
                            orientation[2],
                            orientation[3],
                            orientation[0]])
    createPoseMarker(c.worldpos(),
                     orientation,
                     lineWidth=4,
                     lineLength=2)


def flush():
    global remove_user_item_indices
    for idx in remove_user_item_indices:
        p.removeUserDebugItem(idx)
    remove_user_item_indices = []


def createPoseMarker(position=np.array([0, 0, 0]),
                     orientation=np.array([0, 0, 0, 1]),
                     text="",
                     xColor=np.array([1, 0, 0]),
                     yColor=np.array([0, 1, 0]),
                     zColor=np.array([0, 0, 1]),
                     textColor=np.array([0, 0, 0]),
                     lineLength=0.1,
                     lineWidth=1,
                     textSize=1,
                     textPosition=np.array([0, 0, 0.1]),
                     textOrientation=None,
                     lifeTime=0,
                     parentObjectUniqueId=-1,
                     parentLinkIndex=-1,
                     physicsClientId=0):
    """

    Create a pose marker that identifies a position and orientation
    in space with 3 colored lines.

    """

    global remove_user_item_indices
    pts = np.array([[0, 0, 0], [lineLength, 0, 0], [
                   0, lineLength, 0], [0, 0, lineLength]])
    rotIdentity = np.array([0, 0, 0, 1])
    po, _ = p.multiplyTransforms(position, orientation, pts[0, :], rotIdentity)
    px, _ = p.multiplyTransforms(position, orientation, pts[1, :], rotIdentity)
    py, _ = p.multiplyTransforms(position, orientation, pts[2, :], rotIdentity)
    pz, _ = p.multiplyTransforms(position, orientation, pts[3, :], rotIdentity)
    idx = p.addUserDebugLine(po, px, xColor, lineWidth, lifeTime,
                             parentObjectUniqueId, parentLinkIndex,
                             physicsClientId)
    remove_user_item_indices.append(idx)
    idx = p.addUserDebugLine(po, py, yColor, lineWidth, lifeTime,
                             parentObjectUniqueId, parentLinkIndex,
                             physicsClientId)
    remove_user_item_indices.append(idx)
    idx = p.addUserDebugLine(po, pz, zColor, lineWidth, lifeTime,
                             parentObjectUniqueId, parentLinkIndex,
                             physicsClientId)
    remove_user_item_indices.append(idx)
    if textOrientation is None:
        textOrientation = orientation
    idx = p.addUserDebugText(text, [0, 0, 0.1], textColorRGB=textColor,
                             textSize=textSize,
                             parentObjectUniqueId=parentObjectUniqueId,
                             parentLinkIndex=parentLinkIndex,
                             physicsClientId=physicsClientId)
    remove_user_item_indices.append(idx)
