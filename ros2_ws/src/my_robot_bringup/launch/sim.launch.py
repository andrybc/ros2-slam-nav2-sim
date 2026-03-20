from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    world = LaunchConfiguration('world')

    world_arg = DeclareLaunchArgument(
        'world',
        default_value=PathJoinSubstitution([
            FindPackageShare('my_robot_sim'),
            'worlds',
            'small_room.sdf'
        ]),
        description='Full path to the world file'
    )

    robot_description_content = ParameterValue(
        Command([
            'xacro ',
            PathJoinSubstitution([
                FindPackageShare('my_robot_description'),
                'urdf',
                'my_robot.urdf.xacro'
            ])
        ]),
        value_type=str
    )

    robot_description = {
        'robot_description': robot_description_content
    }

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ),
        launch_arguments={
            'gz_args': ['-r ', world]
        }.items()
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )


    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'my_robot',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.05'
        ],
        output='screen'
    )

    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model'
        ],
        output='screen'
    )

    delayed_spawn = TimerAction(
        period=2.0,
        actions=[spawn_robot]
    )

    return LaunchDescription([
        world_arg,
        gazebo,
        robot_state_publisher_node,
        delayed_spawn,
        bridge_node
    ])