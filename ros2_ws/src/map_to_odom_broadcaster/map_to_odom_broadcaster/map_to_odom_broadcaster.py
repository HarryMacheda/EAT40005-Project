#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import math
import time

class DynamicMapToOdomPublisher(Node):
    def __init__(self):
        super().__init__('dynamic_map_to_odom')
        self.broadcaster = TransformBroadcaster(self)
        self.start_time = time.time()
        self.timer = self.create_timer(0.05, self.broadcast_transform)

    def broadcast_transform(self):
        now = self.get_clock().now().to_msg()
        elapsed = time.time() - self.start_time

        t = TransformStamped()
        t.header.stamp = now
        t.header.frame_id = 'map'
        t.child_frame_id = 'odom'
        
        # No rotation
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        self.broadcaster.sendTransform(t)
        self.get_logger().info(f'Published map → odom: x={t.transform.translation.x:.2f}, y={t.transform.translation.y:.2f}')

def main():
    rclpy.init()
    node = DynamicMapToOdomPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
