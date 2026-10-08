#!/usr/bin/env bash
# Build the workspace from a clean shell.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS="${REPO_ROOT}/ros2_ws"

# ROS setup scripts reference unset variables; -u would abort on them.
set +u
# shellcheck disable=SC1091
source /opt/ros/jazzy/setup.bash
set -u

cd "${WS}"
colcon build --symlink-install "$@"

echo
echo "Build complete. In every new terminal, run:"
echo "  source /opt/ros/jazzy/setup.bash"
echo "  source ${WS}/install/setup.bash"
