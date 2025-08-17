import socket
import time
import json

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion
import math
from builtin_interfaces.msg import Time

def yaw_to_quaternion(yaw):
    # Converts yaw angle (radians) to quaternion (x,y,z,w)
    qz = math.sin(yaw / 2.0)
    qw = math.cos(yaw / 2.0)
    return Quaternion(x=0.0, y=0.0, z=qz, w=qw)

class OdomReceiverNode(Node):
    def __init__(self):
        super().__init__('odom_receiver_node')
        self.declare_parameter('server_ip', '192.168.68.104')
        self.declare_parameter('server_port', 50052)
        self.server_ip = self.get_parameter('server_ip').get_parameter_value().string_value
        self.server_port = self.get_parameter('server_port').get_parameter_value().integer_value

        self.publisher_ = self.create_publisher(Odometry, '/odom', 10)

        self.client_socket = None
        self.buffer = ""

        self.connect()
        self.timer = self.create_timer(0.01, self.receive_data)  # 100Hz timer

    def connect(self):
        while True:
            try:
                self.get_logger().info(f"Trying to connect to {self.server_ip}:{self.server_port}...")
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.server_ip, self.server_port))
                self.client_socket.setblocking(False)
                self.get_logger().info("Connected.")
                break
            except (ConnectionRefusedError, OSError) as e:
                self.get_logger().warn(f"Connection failed: {e}. Retrying in 1 second...")
                time.sleep(1)

    def receive_data(self):
        try:
            data = self.client_socket.recv(4096)
            if data:
                self.buffer += data.decode('utf-8')
                self.process_buffer()
        except BlockingIOError:
            pass  # no data yet
        except (ConnectionResetError, OSError):
            self.get_logger().warn("Connection lost. Reconnecting...")
            self.connect()
            self.buffer = ""

    def process_buffer(self):
        while True:
            try:
                obj, index = json.JSONDecoder().raw_decode(self.buffer)
                self.buffer = self.buffer[index:].lstrip()
                self.publish_odom(obj)
            except json.JSONDecodeError:
                # Incomplete JSON, wait for more data
                break

    def publish_odom(self, data):
        # Create Odometry message from data dictionary
        odom_msg = Odometry()

        # Parse timestamp from string, assuming format "YYYY-MM-DD HH:MM:SS.sss"
        # ROS2 time needs seconds and nanoseconds
        try:
            timestamp_str = data.get('timestamp')
            import datetime
            dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
            secs = int(dt.timestamp())
            nsecs = int(dt.microsecond * 1000)
            odom_msg.header.stamp = Time(sec=secs, nanosec=nsecs)
        except Exception as e:
            self.get_logger().warn(f"Failed to parse timestamp '{timestamp_str}': {e}")
            # Use current time if fail
            odom_msg.header.stamp = self.get_clock().now().to_msg()

        odom_msg.header.frame_id = "odom"
        odom_msg.child_frame_id = "base_link"

        # Fill pose (position)
        odom_msg.pose.pose.position.x = float(data.get('x', 0.0))
        odom_msg.pose.pose.position.y = float(data.get('y', 0.0))
        odom_msg.pose.pose.position.z = 0.0

        # Yaw (rotation around Z axis)
        yaw_deg = float(data.get('yaw', 0.0))
        yaw_rad = math.radians(yaw_deg)
        odom_msg.pose.pose.orientation = yaw_to_quaternion(yaw_rad)

        # Velocity not provided, set zero
        odom_msg.twist.twist.linear.x = 0.0
        odom_msg.twist.twist.linear.y = 0.0
        odom_msg.twist.twist.angular.z = 0.0

        self.publisher_.publish(odom_msg)
        self.get_logger().debug(f"Published odom: x={odom_msg.pose.pose.position.x}, y={odom_msg.pose.pose.position.y}, yaw={yaw_deg}")

def main(args=None):
    rclpy.init(args=args)
    node = OdomReceiverNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

