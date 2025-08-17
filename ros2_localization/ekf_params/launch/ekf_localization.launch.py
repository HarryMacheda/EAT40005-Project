from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    ekf_params = os.path.join(
        os.path.expanduser('~'),
        'turtlebot3_ws', 'src', 'ekf_params', 'params', 'ekf_localization.yaml'
    )
    
    return LaunchDescription([
        Node(
            package='robot_localization',  # <- use robot_localization here
            executable='ekf_node',         # <- the EKF node provided by the package
            name='ekf_filter_node',
            output='screen',
            parameters=[ekf_params]
        )
    ])

