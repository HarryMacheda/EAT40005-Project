from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    map_file = os.path.join(
        os.path.expanduser('~'),
        'turtlebot3_ws/maps/testMap.yaml'
    )
    
    return LaunchDescription([
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{'yaml_filename': map_file}]
        )
    ])

