import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import csv
import time

class CmdVelReplayer(Node):
    def __init__(self):
        super().__init__('cmd_vel_replayer')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.cmds = []
        self.get_logger().info('Loading and replaying /cmd_vel...')
        self.load_csv('cmd_vel_log.csv')
        self.replay()

    def load_csv(self, filename):
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.cmds.append((
                    float(row['time']),
                    float(row['linear_x']),
                    float(row['linear_y']),
                    float(row['linear_z']),
                    float(row['angular_x']),
                    float(row['angular_y']),
                    float(row['angular_z'])
                ))

    def replay(self):
        start = time.time()
        for i, cmd in enumerate(self.cmds):
            delay = cmd[0] - (self.cmds[i - 1][0] if i > 0 else 0)
            time.sleep(delay)
            msg = Twist()
            msg.linear.x = cmd[1]
            msg.linear.y = cmd[2]
            msg.linear.z = cmd[3]
            msg.angular.x = cmd[4]
            msg.angular.y = cmd[5]
            msg.angular.z = cmd[6]
            self.publisher_.publish(msg)
        self.get_logger().info('Finished replaying')

def main(args=None):
    rclpy.init(args=args)
    node = CmdVelReplayer()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
