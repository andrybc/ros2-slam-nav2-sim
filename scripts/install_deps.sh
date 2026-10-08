#!/usr/bin/env bash
# Install the ROS 2 Jazzy packages this workspace needs.
# Assumes ROS 2 Jazzy itself is already installed on Ubuntu 24.04.
set -euo pipefail

if [ ! -d /opt/ros/jazzy ]; then
  echo "error: /opt/ros/jazzy not found. Install ROS 2 Jazzy first." >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

sudo apt-get update

# Simulation, bridge, description, and visualization.
sudo apt-get install -y \
  ros-jazzy-ros-gz \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-xacro \
  ros-jazzy-rviz2 \
  ros-jazzy-tf2-ros \
  ros-jazzy-tf2-tools

# SLAM and map saving. nav2-map-server provides map_saver_cli.
sudo apt-get install -y \
  ros-jazzy-slam-toolbox \
  ros-jazzy-nav2-map-server \
  ros-jazzy-teleop-twist-keyboard

# Resolve anything declared in the package.xml files that the list above missed.
if command -v rosdep >/dev/null 2>&1; then
  sudo rosdep init 2>/dev/null || true
  rosdep update
  # ROS setup scripts reference unset variables; -u would abort.
  set +u
  # shellcheck disable=SC1091
  source /opt/ros/jazzy/setup.bash
  set -u
  rosdep install --from-paths "${REPO_ROOT}/ros2_ws/src" --ignore-src -r -y
else
  echo "note: rosdep not installed; skipped package.xml dependency resolution." >&2
fi

echo
echo "Dependencies installed. Next: ./scripts/build.sh"
