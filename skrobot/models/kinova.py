from cached_property import cached_property

from skrobot.data import kinova_urdfpath
from skrobot.model import RobotModel
from skrobot.models.urdf import RobotModelFromURDF


class Kinova(RobotModelFromURDF):

    def __init__(self, *args, **kwargs):
        super(Kinova, self).__init__(*args, **kwargs)
        #self.reset_pose()

    @cached_property
    def default_urdf_path(self):
        return kinova_urdfpath()

    def reset_pose(self):
        angle_vector = [
            0.0,
            0.26179938,
            3.14159265,
            -2.26892802,
            0.0,
            0.95993108,
            1.57079632
        ]
        for joint, angle in zip(self.rarm.joint_list, angle_vector):
            joint.joint_angle(angle)
        return self.angle_vector()

    @cached_property
    def rarm(self):
        link_names = ['base_link',
                      'shoulder_link',
                      'half_arm_1_link',
                      'half_arm_2_link',
                      'forearm_link',
                      'spherical_wrist_1_link',
                      'spherical_wrist_2_link',
                      'bracelet_link']
        joint_names = ['joint_1',
                       'joint_2',
                       'joint_3',
                       'joint_4',
                       'joint_5',
                       'joint_6',
                       'joint_7']
        links = [getattr(self, n) for n in link_names]
        joints = [getattr(self, n) for n in joint_names]
        model = RobotModel(link_list=links, joint_list=joints)
        model.end_coords = self.end_effector_link
        return model
