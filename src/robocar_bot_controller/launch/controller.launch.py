import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    pkg_rosbot_controller = get_package_share_directory('robocar_bot_controller')

    # Argumento para saber qual robô estamos controlando
    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='robocar_bot',
        description='robocar_bot'
    )
    robot_name = LaunchConfiguration('robot_name')

    # 1. Spawner do Joint State Broadcaster
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
        parameters=[{"use_sim_time": True}],
    )

    # Caminhos absolutos para os YAMLs (evita FileNotFoundError)
    diff_yaml = os.path.join(pkg_rosbot_controller, "config", "robocar_bot_controller.yaml")

    # 2A. Spawner do controlador do rosbotdiff (somente se robot_name == rosbotdiff)
    diff_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "robocar_bot_controller",
            "--param-file", diff_yaml,
        ],
        parameters=[{"use_sim_time": True}],
        condition=IfCondition(PythonExpression(["'", robot_name, "' == 'robocar_bot'"]))
    )

    return LaunchDescription([
        robot_name_arg,
        joint_state_broadcaster_spawner,
        diff_controller_spawner,
    ])