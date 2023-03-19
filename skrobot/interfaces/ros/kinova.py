import actionlib
import control_msgs.msg

from .base import ROSRobotInterfaceBase



class KinovaROSRobotInterface(ROSRobotInterfaceBase):

    def __init__(self, *args, **kwargs):
        super(KinovaROSRobotInterface, self).__init__(*args, **kwargs)


    @property
    def rarm_controller(self):
        return dict(
            controller_type='rarm_controller',
            controller_action='/my_gen3/gen3_joint_trajectory_controller/follow_joint_trajectory',  # NOQA
            controller_state='/my_gen3/gen3_joint_trajectory_controller/state',
            action_type=control_msgs.msg.FollowJointTrajectoryAction,
            joint_names=[j.name for j in self.robot.rarm.joint_list],
        )

    def default_controller(self):
        return [self.rarm_controller]

