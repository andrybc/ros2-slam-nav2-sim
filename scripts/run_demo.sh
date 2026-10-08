#!/usr/bin/env bash
# Launch one piece of the stack with the workspace already sourced.
#
#   ./scripts/run_demo.sh sim      Gazebo + robot + bridge, no SLAM
#   ./scripts/run_demo.sh slam     the above plus SLAM Toolbox
#   ./scripts/run_demo.sh rviz     RViz with the project config
#   ./scripts/run_demo.sh teleop   keyboard driving
#
# Each needs its own terminal. This script deliberately does not spawn
# terminals for you, so that the output of each node stays readable.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS="${REPO_ROOT}/ros2_ws"

if [ ! -f "${WS}/install/setup.bash" ]; then
  echo "error: workspace not built. Run ./scripts/build.sh first." >&2
  exit 1
fi

# ROS setup scripts reference unset variables; -u would abort on them.
set +u
# shellcheck disable=SC1091
source /opt/ros/jazzy/setup.bash
# shellcheck disable=SC1091
source "${WS}/install/setup.bash"
set -u

case "${1:-}" in
  sim)    exec ros2 launch my_robot_bringup sim.launch.py ;;
  slam)   exec ros2 launch my_robot_bringup slam.launch.py ;;
  rviz)   exec ros2 launch my_robot_bringup rviz.launch.py ;;
  teleop) exec ros2 run my_robot_bringup wasd_teleop.py ;;
  *)
    sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit 1
    ;;
esac
