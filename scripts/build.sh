#!/usr/bin/env bash
# Build the workspace from a clean shell.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS="${REPO_ROOT}/ros2_ws"

# shellcheck disable=SC1091
source /opt/ros/jazzy/setup.bash

cd "${WS}"
colcon build --symlink-install "$@"

echo
echo "Build complete. In every new terminal, run:"
echo "  source /opt/ros/jazzy/setup.bash"
echo "  source ${WS}/install/setup.bash"
