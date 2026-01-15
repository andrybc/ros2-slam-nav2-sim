# ROS 2 Jazzy SLAM & Navigation  
**Simulation-First Differential Drive Robot → Real Hardware**

This repository documents my end-to-end process of building a **differential-drive mobile robot** using **ROS 2 Jazzy**, starting fully in **simulation** and then transitioning the same architecture to a **real robot**.

The focus of this project is understanding and implementing:
- URDF/Xacro robot modeling
- TF frame design and debugging
- Gazebo simulation (diff-drive + LiDAR)
- SLAM Toolbox mapping
- Nav2 navigation
- Clean bringup and reproducible workflows

The simulation is designed so that **SLAM and Nav2 do not change** when moving to real hardware — only the sensor and base drivers are swapped.

---

## Project Goals

- Build a minimal differential-drive robot from scratch
- Design a correct TF tree for SLAM and Nav2
- Simulate realistic odometry and LiDAR data
- Generate maps using SLAM Toolbox
- Navigate using Nav2
- Transition the same ROS graph to a physical robot later

---

## Standard Interfaces (Kept Stable Across Sim & Hardware)

### Topics
- `/scan` — `sensor_msgs/LaserScan`
- `/odom` — `nav_msgs/Odometry`
- `/cmd_vel` — `geometry_msgs/Twist`
- `/tf`, `/tf_static`

### Frames
- `map`
- `odom`
- `base_link`
- `laser_link`
- (optional) `base_footprint`

---
Target TF tree:

  map -> odom -> base_link -> laser_link

This TF structure is treated as a strict contract.
All simulation and future hardware components are required to conform to it so that
SLAM Toolbox and Nav2 do not need to be modified when transitioning to real hardware.

---

Repository Structure:

  ros2-slam-nav2-sim/
  ├── docs/
  │   ├── images/        # gifs, diagrams, screenshots
  │   ├── notes/         # setup, debugging, tuning notes
  │   └── roadmap.md
  ├── ros2_ws/src/
  │   ├── my_robot_description/  # URDF/Xacro
  │   ├── my_robot_sim/          # Gazebo worlds
  │   ├── my_robot_bringup/      # launch + config
  │   └── my_robot_maps/         # saved maps
  └── scripts/                   # build/run helpers

---

Plan: Build My Own Differential Drive Robot (Simulation -> Hardware)

Phase 1: Robot Model (URDF/Xacro)
Goal:
  Create a minimal, well-structured robot description with correct frames.

Tasks:
  - Create my_robot.urdf.xacro
  - Define base_link, wheel links, and laser_link
  - Verify model loads correctly in RViz
  - Confirm static TF relationships are correct

Status: not started

---

Phase 2: Simulation (Gazebo)
Goal:
  Simulate realistic robot motion and sensing.

Tasks:
  - Create Gazebo world files
  - Spawn robot into Gazebo
  - Add differential drive plugin
    - Publishes /odom
    - Broadcasts odom -> base_link
  - Add LiDAR plugin publishing /scan

Status: not started

---

Phase 3: SLAM Toolbox
Goal:
  Generate a map from simulated LiDAR data.

Tasks:
  - Launch simulation with SLAM Toolbox
  - Teleoperate robot through environment
  - Verify map -> odom transform
  - Save generated maps to my_robot_maps

Status: not started

---

Phase 4: Navigation (Nav2)
Goal:
  Enable autonomous navigation using the generated map.

Tasks:
  - Configure Nav2 parameters
  - Set initial pose in RViz
  - Send navigation goals
  - Tune planner and controller behavior

Status: not started

---

Phase 5: Transition to Real Robot (Planned)
Goal:
  Apply the same ROS graph to physical hardware.

Tasks:
  - Replace Gazebo plugins with hardware drivers
  - Preserve topic names and TF tree
  - Validate SLAM and Nav2 without code changes

Status: planned

---

Build Instructions:

  cd ros2_ws
  colcon build --symlink-install
  source install/setup.bash

Optional helper scripts:
  ./scripts/install_deps.sh
  ./scripts/build.sh

---

Launch Commands (Planned):

  ros2 launch my_robot_bringup sim.launch.py
  ros2 launch my_robot_bringup slam.launch.py
  ros2 launch my_robot_bringup nav2.launch.py

---

Debugging Checklist:

Topics and nodes:
  ros2 topic list
  ros2 topic echo /scan
  ros2 topic echo /odom
  ros2 node list

TF inspection:
  ros2 run tf2_tools view_frames
  ros2 run tf2_ros tf2_echo odom base_link
  ros2 run tf2_ros tf2_echo base_link laser_link

Expected behavior:
  - odom -> base_link updates while moving
  - base_link -> laser_link is static
  - SLAM publishes map -> odom

---

Documentation and Progress Tracking:

  docs/notes/setup.md      # environment and dependencies
  docs/notes/debugging.md  # issues encountered and fixes
  docs/notes/tuning.md     # SLAM and Nav2 parameter tuning
  docs/images/             # gifs and screenshots

Each completed phase will include:
  - A short written summary
  - Visual evidence (gif or screenshot)
  - Notes on lessons learned

---

License:
  See LICENSE file


