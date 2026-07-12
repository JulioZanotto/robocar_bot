# robocar_bot
Repositório para testes de algoritmos de navegação na mini cidade do evento da RoboCar Race

O bot criado é uma cópia do TurtleBot3 com uma câmera stereo. O workspace conta com um bringup para lançar tudo onde o default é um mapa limpo somente com o semáforo.

Testado no ROS2 Jazzy.

Launch do mapa Robocar Race (Réplica ainda em desenvolvimento):

ros2 launch robocar_bot_bringup robocar_bot_bringup.launch.py world:=robocar_map.sdf

Launch do controle rqt_virtual_joystick:
ros2 run rqt_virtual_joystick rqt_virtual_joystick
Aqui precisa alterar o tópico de publicação do cmd_vel para /robocar_bot_controller/cmd_vel

Mais informações em:
https://github.com/amgaber95/rqt_virtual_joystick
