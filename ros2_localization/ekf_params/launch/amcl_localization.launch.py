from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    map_file = os.path.expanduser('~/turtlebot3_ws/maps/testMap.yaml')

    return LaunchDescription([
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'odom_topic': '/odom',           # or '/odometry/filtered' if using EKF
                'base_frame_id': 'base_link',
                'odom_frame_id': 'odom',
                'scan_topic': '/scan',
                'min_particles': 500,
                'max_particles': 2000,
                'initial_pose': {'x': 0.0, 'y': 0.0, 'theta': 0.0},
                'map': map_file
            }]
        )
    ])

