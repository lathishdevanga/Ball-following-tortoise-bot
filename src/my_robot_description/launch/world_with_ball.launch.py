import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Get the package directory
    pkg_dir = get_package_share_directory('my_robot_description')
    world_file = os.path.join(os.path.expanduser('~/task3/task2/ros2_ws/src/my_robot_description/worlds'), 'world_with_ball.sdf')
    
    return LaunchDescription([
        # Launch Gazebo with the world file
        ExecuteProcess(
            cmd=['gz', 'sim', world_file, '-v', '4'],
            output='screen'
        ),
        
        # Bridge between Gazebo and ROS2
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
            output='screen'
        ),
    ])