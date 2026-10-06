import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('amr_sim')
    world = os.path.join(pkg, 'worlds', 'warehouse.sdf')
    robot_description = xacro.process_file(
        os.path.join(pkg, 'urdf', 'amr.urdf.xacro')).toxml()

    gz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': ['-r ', LaunchConfiguration('gz_flags'), ' ', world]}.items())

    rsp = Node(package='robot_state_publisher', executable='robot_state_publisher',
               parameters=[{'robot_description': robot_description,
                            'use_sim_time': True}])

    spawn = Node(package='ros_gz_sim', executable='create',
                 arguments=['-topic', 'robot_description', '-name', 'amr',
                            '-x', '0', '-y', '0', '-z', '0.15'])

    bridge = Node(package='ros_gz_bridge', executable='parameter_bridge',
                  arguments=[
                      '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                      '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                      '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                      '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
                      '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
                      '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                  ])

    gz_flags = DeclareLaunchArgument(
        'gz_flags', default_value='', description='extra gz sim flags, e.g. "-s" for headless')

    return LaunchDescription([gz_flags, gz, rsp, spawn, bridge])
