import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # Caminhos para os outros pacotes
    pkg_description = get_package_share_directory('robocar_bot_description')
    pkg_controller = get_package_share_directory('robocar_bot_controller')

    # 1. Definição dos Argumentos Globais
    robot_name_arg = DeclareLaunchArgument(
        'robot_name', default_value='robocar_bot',
        description='Escolha o robô: robocar_bot'
    )

    # CORREÇÃO: Passando apenas o nome do arquivo SDF
    world_arg = DeclareLaunchArgument(
        'world', default_value='empty.sdf',
        description='Mundo do Gazebo'
    )

    # 2. Inclusão do Launch do Gazebo (que já faz o Spawn e as Bridges)
    # Obs: Verifique se o nome do arquivo que editamos na etapa anterior é realmente 'gazebo.launch.py'
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_description, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'robot_name': LaunchConfiguration('robot_name'),
            'world': LaunchConfiguration('world')
        }.items()
    )

    # 3. Inclusão do Launch do Controller
    controller_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_controller, 'launch', 'controller.launch.py')
        ),
        launch_arguments={
            'robot_name': LaunchConfiguration('robot_name')
        }.items()
    )

    # joystick_launch = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(pkg_controller, 'launch', 'joy_controller.launch.py')
    #     ),
    #     launch_arguments={
    #         'robot_name': LaunchConfiguration('robot_name')
    #     }.items()
    # )

    return LaunchDescription([
        robot_name_arg,
        world_arg,
        gazebo_launch,
        controller_launch,
        # joystick_launch
    ])