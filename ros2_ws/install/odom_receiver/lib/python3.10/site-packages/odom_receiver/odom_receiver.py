import socket
import time
import json
import math
import datetime

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion
from builtin_interfaces.msg import Time


def yaw_to_quaternion(yaw):
    qz = math.sin(yaw / 2.0)
    qw = math.cos(yaw / 2.0)
    return Quaternion(x=0.0, y=0.0, z=qz, w=qw)


class OdomReceiverNode(Node):
    def __init__(self):
        super().__init__('odom_receiver_node')
        self.declare_parameter('server_ip', '192.168.68.106')
        self.declare_parameter('server_port', 50052)
        self.server_ip = self.get_parameter('server_ip').get_parameter_value().string_value
        self.server_port = self.get_parameter('server_port').get_parameter_value().integer_value

        self.publisher_ = self.create_publisher(Odometry, '/odom', 10)

        self.client_socket = None
        self.buffer = ""

        self.connect()
        self.timer = self.create_timer(0.01, self.receive_data)

        # Open CSV file once, append mode
        self.csv_file_path = "temi_position_data.csv"
        # Write header if file empty
        try:
            with open(self.csv_file_path, "a") as f:
                if f.tell() == 0:
                    f.write("timestamp,x,y,yaw,tilt,status\n")
        except Exception as e:
            self.get_logger().warn(f"Failed to initialize CSV file: {e}")

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
                decoded_data = data.decode('utf-8')
                self.get_logger().info(f"Received raw data: {decoded_data}")  # Debug print
                self.buffer += decoded_data
                self.process_buffer()
            else:
                # Server closed connection gracefully
                self.get_logger().error("Server closed connection. Shutting down node.")
                rclpy.shutdown()
                exit(0)
        except BlockingIOError:
            pass
        except (ConnectionResetError, OSError) as e:
            self.get_logger().error(f"Connection lost ({e}). Shutting down node.")
            rclpy.shutdown()
            exit(0)

    def process_buffer(self):
        while True:
            try:
                obj, index = json.JSONDecoder().raw_decode(self.buffer)
                self.buffer = self.buffer[index:].lstrip()
                self.publish_odom(obj)
                self.save_to_file(obj)
            except json.JSONDecodeError:
                break

    def publish_odom(self, data):
        odom_msg = Odometry()

        try:
            timestamp_str = data.get('timestamp')
            dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
            secs = int(dt.timestamp())
            nsecs = int(dt.microsecond * 1000)
            odom_msg.header.stamp = Time(sec=secs, nanosec=nsecs)
        except Exception as e:
            self.get_logger().warn(f"Failed to parse timestamp '{timestamp_str}': {e}")
            odom_msg.header.stamp = self.get_clock().now().to_msg()

        odom_msg.header.frame_id = "odom"
        odom_msg.child_frame_id = "base_link"

        odom_msg.pose.pose.position.x = float(data.get('x', 0.0))
        odom_msg.pose.pose.position.y = float(data.get('y', 0.0))
        odom_msg.pose.pose.position.z = 0.0

        yaw_deg = float(data.get('yaw', 0.0))
        yaw_rad = math.radians(yaw_deg)
        odom_msg.pose.pose.orientation = yaw_to_quaternion(yaw_rad)

        odom_msg.twist.twist.linear.x = 0.0
        odom_msg.twist.twist.linear.y = 0.0
        odom_msg.twist.twist.angular.z = 0.0

        self.publisher_.publish(odom_msg)
        self.get_logger().debug(f"Published odom: x={odom_msg.pose.pose.position.x}, y={odom_msg.pose.pose.position.y}, yaw={yaw_deg}")

    def save_to_file(self, data):
        try:
            with open(self.csv_file_path, "a") as f:
                # Sanitize status to avoid commas breaking CSV
                status = data.get('status', '').replace(',', ';')
                f.write(f"{data.get('timestamp')},{data.get('x')},{data.get('y')},"
                        f"{data.get('yaw')},{data.get('tilt')},{status}\n")
        except Exception as e:
            self.get_logger().warn(f"Error saving to file: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = OdomReceiverNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

