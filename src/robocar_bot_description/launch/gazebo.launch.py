import os
from pathlib import Path
from ament_index_python.packages import get_package_share_directory, get_package_prefix

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    robocar_bot_description = get_package_share_directory("robocar_bot_description")
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")
    
    # --- Paths do Semáforo ---
    tl_pkg_share = get_package_share_directory('traffic_light_sim')
    tl_pkg_prefix = get_package_prefix('traffic_light_sim')
    tl_model_path = os.path.join(tl_pkg_share, 'models')
    tl_plugin_path = os.path.join(tl_pkg_prefix, 'lib')

    # --- Args ---
    robot_name_arg = DeclareLaunchArgument(
        "robot_name",
        default_value="robocar_bot",
        description="robocar_bot ou rosbotacker"
    )
    robot_name = LaunchConfiguration("robot_name")

    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=PythonExpression([
            "'robocar_bot.urdf' if '", robot_name, "' == 'robocar_bot' else 'rosbotacker.urdf.xacro'"
        ]),
        description="URDF file in robocar_bot_description/urdf"
    )
    robot_model = LaunchConfiguration("model")
    model_path = PathJoinSubstitution([
        FindPackageShare("robocar_bot_description"),
        "urdf",
        robot_model
    ])

    world_arg = DeclareLaunchArgument(
        "world",
        default_value="empty.sdf",
        description="World file in robocar_bot_description/worlds"
    )
    world = LaunchConfiguration("world")
    world_path = PathJoinSubstitution([
        FindPackageShare("robocar_bot_description"),
        "worlds",
        world
    ])

    # --- Resource path ---
    share_parent = str(Path(robocar_bot_description).parent)  # .../share

    # Atualizado para incluir a pasta de modelos do semáforo
    set_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=":".join([share_parent, tl_model_path])
    )
    
    # Adicionado para o Gazebo achar a biblioteca C++ do semáforo
    set_plugin_path = SetEnvironmentVariable(
        name="GZ_SIM_SYSTEM_PLUGIN_PATH",
        value=tl_plugin_path
    )

    # --- Robot description ---
    robot_description = ParameterValue(
        Command(["xacro ", model_path]),
        value_type=str
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description, "use_sim_time": True}],
        output="screen"
    )

    # --- Gazebo ---
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={
            "gz_args": PythonExpression(["'-r -v 4 ", world_path, "'"])
        }.items()
    )

    # --- Conditional spawn arguments based on world (Robô) ---
    spawn_x = PythonExpression(["'0' if 'empty' in '", world, "' else '-4.6770'"])
    spawn_y = PythonExpression(["'0' if 'empty' in '", world, "' else '-4.2073'"])
    spawn_z = PythonExpression(["'0' if 'empty' in '", world, "' else '0.05'"])
    spawn_Y = PythonExpression(["'0' if 'empty' in '", world, "' else '0.0028'"])

    # --- Spawn entity (Robô) ---
    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-topic", "robot_description",
            "-name", robot_name,
            "-x", spawn_x,
            "-y", spawn_y,
            "-z", spawn_z,
            "-Y", spawn_Y
        ],
    )
    
    # --- Spawn entity (Semáforo) ---
    # Coloquei coordenadas genéricas de exemplo (x=5, y=0). Ajuste conforme a sua cidade.
    spawn_traffic_light = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'semaforo_cruzamento_1',
            '-file', os.path.join(tl_model_path, 'traffic_light', 'model.sdf'),
            '-x', '-3.0770', '-y', '-4.5046', '-z', '0.0', 
            '-Y', '3.1358' # Rotação Yaw
        ],
        output='screen',
    )

    bridge_params = os.path.join(
        get_package_share_directory("robocar_bot_description"),
        "config",
        "gz_bridge.yaml"
    )

    gz_ros2_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "--ros-args",
            "-p",
            f"config_file:={bridge_params}",
        ],
        parameters=[{"use_sim_time": True}],
        output="screen"
    )

    ros_gz_image_bridge = Node(
        package="ros_gz_image",
        executable="image_bridge",
        arguments=["/camera/image"],
        parameters=[{"use_sim_time": True}],
        output="screen"
    )

    delayed_spawn = TimerAction(period=5.0, actions=[gz_spawn_entity])

    return LaunchDescription([
        robot_name_arg,
        model_arg,
        world_arg,
        set_resource_path,
        set_plugin_path, # Novo!
        robot_state_publisher_node,
        gazebo,
        spawn_traffic_light, 
        delayed_spawn,
        gz_ros2_bridge,
        ros_gz_image_bridge,
    ])