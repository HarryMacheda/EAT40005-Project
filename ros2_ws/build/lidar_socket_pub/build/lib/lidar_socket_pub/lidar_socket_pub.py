import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Header

import socket
import json
import math

class LidarSocketServer(Node):
    def __init__(self):
        super().__init__('lidar_socket_server')

        # ROS publisher
        self.publisher_ = self.create_publisher(LaserScan, 'scan', 10)

        # Scan parameters
        self.frame_id = 'laser_frame'
        self.angle_increment = 1.0  # degrees
        self.range_min = 0.05       # meters
        self.range_max = 6.0        # meters
        self.num_readings = int(360 / self.angle_increment)

        # Data buffers
        self.ranges_buffer = [float('inf')] * self.num_readings
        self.received_angles = set()
        self.buffer = ""

        # Socket server setup
        self.server_ip = "192.168.68.107"
        #self.server_ip = "0.0.0.0"
        self.server_port = 50056
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(1)
        self.get_logger().info(f"Server listening on {self.server_ip}:{self.server_port}...")

        self.client_socket, client_addr = self.server_socket.accept()
        self.client_socket.setblocking(False)
        self.get_logger().info(f"Connection established with {client_addr}")

        # Timer to poll socket frequently
        self.timer = self.create_timer(0.01, self.receive_and_buffer_data)

        # The threshold of valid readings needed to publish
        self.valid_readings_threshold = 300  # e.g., require 300 valid angles out of 360

    def receive_data(self):
        try:
            data = self.client_socket.recv(4096)
            if data:
                self.buffer += data.decode("utf-8")
        except BlockingIOError:
            pass  # No data yet

    def parse_points(self):
        points = []
        while True:
            try:
                obj, index = json.JSONDecoder().raw_decode(self.buffer)
                self.buffer = self.buffer[index:].lstrip()

                #if obj.get("distance", 0.0) == 0.0 or obj.get("quality", 0) == 0:
                    #continue

                points.append(obj)
            except json.JSONDecodeError:
                break
        return points

    def receive_and_buffer_data(self):
        self.receive_data()
        points = self.parse_points()

        for point in points:
            angle = int(point['theta']) % 360
            distance_m = point['distance'] / 1000.0

            # Debugging: Print each angle and distance being added to the scan buffer
            if self.range_min <= distance_m <= self.range_max:
                self.ranges_buffer[angle] = distance_m
                self.received_angles.add(angle)
                self.get_logger().debug(f"Added angle {angle} with distance {distance_m}m")

        # If sufficient valid data is received, publish the scan
        if len(self.received_angles) >= self.valid_readings_threshold:
            self.publish_scan()
            self.ranges_buffer = [float('inf')] * self.num_readings
            self.received_angles.clear()

    def publish_scan(self):
        scan_msg = LaserScan()
        scan_msg.header = Header()
        scan_msg.header.stamp = self.get_clock().now().to_msg()
        scan_msg.header.frame_id = self.frame_id

        scan_msg.angle_min = 0.0
        scan_msg.angle_max = 2 * math.pi
        scan_msg.angle_increment = math.radians(self.angle_increment)
        scan_msg.time_increment = 0.0
        scan_msg.scan_time = 0.1  # estimate
        scan_msg.range_min = self.range_min
        scan_msg.range_max = self.range_max
        scan_msg.ranges = self.ranges_buffer
        scan_msg.intensities = []

        self.publisher_.publish(scan_msg)
        self.get_logger().info("✅ Published LaserScan with sufficient data")

def main(args=None):
    rclpy.init(args=args)
    node = LidarSocketServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

