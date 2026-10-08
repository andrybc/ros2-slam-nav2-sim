cmake_minimum_required(VERSION 3.8)
project(my_robot_bringup)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

# Executables must go to lib/<pkg>, which is where `ros2 run` looks,
# and must land with the execute bit set. PROGRAMS does that; FILES does not.
install(
  PROGRAMS
    scripts/wasd_teleop.py
    scripts/odom_yaw_test.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
