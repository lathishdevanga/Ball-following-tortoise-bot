#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Get URDF path
    pkg_share = get_package_share_directory('my_robot_description')
    sdf_path = os.path.join(pkg_share, 'sdf', 'my_robot.sdf')

    # Load URDF contents
    with open(sdf_path, 'r') as sdf_file:
        robot_description = sdf_file.read()

    # Robot state publisher
    robot_state_pub = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen'
    )

    # Joint state publisher (optional, if your robot has joints)
    joint_state_pub = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'
    )

    # Spawn robot into already running Gazebo Harmonic world
    spawn_entity = ExecuteProcess(
        cmd=[
            'ros2', 'run', 'ros_gz_sim', 'create',
            '-name', 'tortoisebot',
            '-file', sdf_path,
            '-x', '0.0', '-y', '0.0', '-z', '0.2'
        ],
        output='screen'
    )

    # ROS-Gazebo bridge (TF + Clock)
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist'
        ],
        output='screen'
    )


    return LaunchDescription([
        robot_state_pub,
        joint_state_pub,
        spawn_entity,
        bridge_node
    ])
