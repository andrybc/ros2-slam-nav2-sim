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

## Mapping Demo

SLAM Toolbox building an occupancy grid from simulated 360° LiDAR while the
robot is teleoperated through the maze world.


Stack: ROS 2 Jazzy · Gazebo Harmonic · SLAM Toolbox (sync) · RViz2

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
- `base_footprint`
- `base_link`
- `laser_link`

---
TF tree:

```text
map             <- SLAM Toolbox publishes map -> odom
 └─ odom        <- Gazebo DiffDrive publishes odom -> base_footprint
     └─ base_footprint
         └─ base_link        <- robot_state_publisher, fixed
             └─ laser_link   <- robot_state_publisher, fixed
```

`base_footprint` is the ground-projected frame the diff-drive plugin reports
its odometry against (`child_frame_id` in the URDF plugin block), and
`base_link` sits one wheel radius above it. This TF structure is treated as a
strict contract.
All simulation and future hardware components are required to conform to it so that
SLAM Toolbox and Nav2 do not need to be modified when transitioning to real hardware.


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

Status: Completed

---

Phase 2: Simulation (Gazebo)
Goal:
  Simulate realistic robot motion and sensing.

Tasks:
  - Create Gazebo world files
  - Spawn robot into Gazebo
  - Add differential drive plugin
    - Publishes /odom
    - Broadcasts odom -> base_footprint
  - Add LiDAR plugin publishing /scan

Status: Completed

---

Phase 3: SLAM Toolbox
Goal:
  Generate a map from simulated LiDAR data.

Tasks:
  - Launch simulation with SLAM Toolbox
  - Teleoperate robot through environment
  - Verify map -> odom transform
  - Save generated maps to my_robot_maps

Status: In Progress

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

## Build

From a fresh clone on Ubuntu 24.04 with ROS 2 Jazzy installed:

```bash
./scripts/install_deps.sh     # apt + rosdep
./scripts/build.sh            # colcon build --symlink-install
```

Or by hand:

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

---

## Run

Each line needs its own terminal, with the workspace sourced.

```bash
./scripts/run_demo.sh slam      # Gazebo + robot + bridge + SLAM Toolbox
./scripts/run_demo.sh rviz      # RViz, Fixed Frame = map
./scripts/run_demo.sh teleop    # WASD keyboard driving
```

Simulation only, without SLAM — used for odometry diagnostics:

```bash
./scripts/run_demo.sh sim
```

Saving a map, with a non-empty-output check:

```bash
./scripts/save_map.sh small_room
```

Nav2 bringup is not implemented yet; see Phase 4.

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



