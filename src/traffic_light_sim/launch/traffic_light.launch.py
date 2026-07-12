import os
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'traffic_light_sim'
    pkg_share = get_package_share_directory(pkg_name)
    pkg_prefix = get_package_prefix(pkg_name)

    # Configuração de caminhos para o Gazebo Harmonic encontrar os arquivos
    model_path = os.path.join(pkg_share, 'models')
    plugin_path = os.path.join(pkg_prefix, 'lib')

    set_env_models = SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=model_path)
    set_env_plugins = SetEnvironmentVariable(name='GZ_SIM_SYSTEM_PLUGIN_PATH', value=plugin_path)

    # Inicia o Gazebo em um mundo vazio para testar (com Verbosidade 4)
    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', '-v', '4', 'empty.sdf'],
        output='screen'
    )

    # Spawn do Semáforo
    spawn_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'meu_semaforo',
            '-file', os.path.join(model_path, 'traffic_light', 'model.sdf'),
            '-x', '2.0', '-y', '0.0', '-z', '0.0'
        ],
        output='screen',
    )

    return LaunchDescription([
        set_env_models,
        set_env_plugins,
        gz_sim,
        spawn_node
    ])