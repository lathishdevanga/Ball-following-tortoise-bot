import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
import csv

class CmdVelRecorder(Node):
    def __init__(self):
        super().__init__('cmd_vel_recorder')

        # Subscribe to the /cmd_vel topic
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.listener_callback,
            10
        )

        self.start_time = time.time()
        self.recorded_data = []

        self.get_logger().info('Recording /cmd_vel... Press Ctrl+C to stop and save.')

    def listener_callback(self, msg):
        # Save timestamped velocity data
        timestamp = time.time() - self.start_time
        self.recorded_data.append((
            timestamp,
            msg.linear.x, msg.linear.y, msg.linear.z,
            msg.angular.x, msg.angular.y, msg.angular.z
        ))

    def save_to_csv(self, filename='cmd_vel_log.csv'):
        # Save all recorded data to a CSV
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['time', 'linear_x', 'linear_y', 'linear_z', 'angular_x', 'angular_y', 'angular_z'])
            for row in self.recorded_data:
                writer.writerow(row)

        self.get_logger().info(f'[✔] Saved to {filename}')

def main(args=None):
    rclpy.init(args=args)
    node = CmdVelRecorder()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('[⏹] Interrupted. Saving CSV...')
        node.save_to_csv()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
