import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # 1. Definir o nome do pacote e caminhos básicos
    pkg_name = 'robocar_bot_description'
    
    # 2. Buscar o arquivo Xacro/URDF principal do robô
    # NOTA: Ajuste o nome abaixo para o arquivo real que você copiou (ex: turtlebot3_burger.urdf.xacro)
    xacro_file = os.path.join(get_package_share_directory(pkg_name), 'urdf', 'turtlebot3_burger.urdf')
    
    # Processar o arquivo xacro para converter em string URDF pura
    robot_description_raw = xacro.process_file(xacro_file).toxml()

    # 3. Configurar os Nós do ROS2
    
    # Robot State Publisher (publica os links e as transformações tf estáticas do robô)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_raw}]
    )

    # Joint State Publisher GUI (cria a janela com os controles deslizantes para as rodas)
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen'
    )

    # RViz2 (o display visualizador)
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        # O argumento abaixo faz o RViz iniciar sem nenhuma config, limpo
        arguments=[]
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])