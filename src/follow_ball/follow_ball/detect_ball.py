import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import math

class LidarAngleRange(Node):
    def __init__(self):
        super().__init__('lidar_angle_range')
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.target_angle = None
        self.is_aligned = False  

    def scan_callback(self, msg):
        valid_angles_deg = []
        for i, distance in enumerate(msg.ranges):
            if not math.isinf(distance) and not math.isnan(distance):
                angle_rad = msg.angle_min + i * msg.angle_increment
                angle_deg = math.degrees(angle_rad)
                valid_angles_deg.append(angle_deg)

        twist = Twist()

        if valid_angles_deg:
            min_angle = min(valid_angles_deg)
            max_angle = max(valid_angles_deg)
            self.get_logger().info(f"Valid LIDAR Data Range: {min_angle:.2f}° to {max_angle:.2f}°")

            centre_angle = (min_angle + max_angle) / 2.0
            self.target_angle = (centre_angle + 360) % 360
            if self.target_angle > 180:
                self.target_angle -= 360

            centre_angle_rad = math.radians(centre_angle)
            centre_angle_index = int((centre_angle_rad - msg.angle_min) / msg.angle_increment)
            centre_angle_index = max(0, min(centre_angle_index, len(msg.ranges) - 1))
            front_distance = msg.ranges[centre_angle_index]

            self.get_logger().info(f"Front Distance: {front_distance:.2f} m")

            if front_distance > 2.5:
                if abs(self.target_angle) > 10.0:
                    twist.angular.z = 0.5 if self.target_angle > 0 else -0.5
                    twist.linear.x = 0.0
                    self.is_aligned = False
                else:
                    twist.angular.z = 0.0
                    twist.linear.x = 0.2
                    self.is_aligned = True
            else:
                twist.angular.z = 0.0
                if front_distance > 0.5:
                    twist.linear.x = 0.2
                else:
                    twist.linear.x = 0.0
                    self.is_aligned = False


            self.get_logger().info(f"Aligned Status: {self.is_aligned}")
            self.cmd_pub.publish(twist)

        else:
            self.get_logger().warn("No valid LIDAR data in current scan. Robot will stop.")
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.cmd_pub.publish(twist)
            self.target_angle = None
            self.is_aligned = False

def main(args=None):
    rclpy.init(args=args)
    node = LidarAngleRange()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
