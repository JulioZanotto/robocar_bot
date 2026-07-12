cmake_minimum_required(VERSION 3.8)
project(traffic_light_sim)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(gz-sim8 REQUIRED)
find_package(gz-plugin2 REQUIRED)
find_package(gz-msgs10 REQUIRED)

# Compila o plugin do Gazebo
add_library(traffic_light_plugin SHARED src/traffic_light_plugin.cpp)
target_link_libraries(traffic_light_plugin
  gz-sim8::gz-sim8
  gz-plugin2::gz-plugin2
  gz-msgs10::gz-msgs10
)

# Instala a biblioteca do plugin
install(TARGETS traffic_light_plugin
  DESTINATION lib
)

# Instala os modelos e os launch files
install(DIRECTORY models launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()