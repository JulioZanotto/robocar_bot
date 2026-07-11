import os
from pathlib import Path
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Definição de Caminhos
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_rosbot_description = get_package_share_directory('robocar_bot_description')

    # Caminho para a pasta de mundos dentro do pacote
    worlds_pkg_path = os.path.join(pkg_rosbot_description, 'worlds')

    # CORREÇÃO DOS MESHES: Aponta para o diretório 'parent' (geralmente /install)
    gz_resource_path = str(Path(pkg_rosbot_description).parent.resolve())

    # 2. Argumentos de Interface
    robot_name_arg = DeclareLaunchArgument(
        'robot_name', default_value='robocar_bot',
        description='Escolha o robô: robocar_bot'
    )

    world_arg = DeclareLaunchArgument(
        'world', default_value='empty.sdf',
        description='Mundo a carregar (ex: empty.sdf)'
    )

    # 3. Variáveis de Ambiente
    # Concatenamos o caminho do pacote, o caminho dos mundos e o caminho do Blender
    # O Gazebo vai procurar arquivos em todos esses diretórios
    set_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[gz_resource_path, ':', worlds_pkg_path]
    )

    # 4. Processamento do Robô (URDF/XACRO)
    robot_model_path = PathJoinSubstitution([
        pkg_rosbot_description, 'urdf', 
        [LaunchConfiguration('robot_name'), '.urdf']
    ])

    robot_description = Command(['xacro ', robot_model_path])

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }]
    )

    # 5. Gazebo Sim
    # Usamos PathJoinSubstitution para que o Gazebo receba o caminho COMPLETO do mundo
    world_full_path = PathJoinSubstitution([worlds_pkg_path, LaunchConfiguration('world')])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': [world_full_path, ' -r -v 1']
        }.items(),
    )

    # 6. Spawn do Robô
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-name', LaunchConfiguration('robot_name'),
            '-topic', 'robot_description',
            '-x', '0.0', '-y', '0.0', '-z', '0.1',
        ]
    )

    # APLICAÇÃO DO TIMER: O robô só nasce 7 segundos após o Gazebo iniciar
    # Isso evita o erro "Parent not found" e o crash de renderização (SegFault)
    delayed_spawn_robot = TimerAction(
        period=7.0,
        actions=[spawn_robot]
    )

    # 7. Pontes de Comunicação (Bridges)
    # Ponte para Sensores (Laser, IMU, Camera Info, PointCloud)
    bridge_params = os.path.join(pkg_rosbot_description, 'config', 'gz_bridge.yaml')
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_params}],
        output='screen'
    )

    # Ponte de Imagem (Otimizada para transporte de vídeo)
    ros_gz_image_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/camera/image'],
        output='screen'
    )

    return LaunchDescription([
        set_resource_path,
        robot_name_arg,
        world_arg,
        node_robot_state_publisher,
        gazebo,
        delayed_spawn_robot,
        ros_gz_bridge,
        ros_gz_image_bridge
    ])

