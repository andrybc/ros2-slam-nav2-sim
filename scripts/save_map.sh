#!/usr/bin/env bash
# Save the live SLAM map and refuse to succeed unless both output files
# are non-empty. Run this while slam.launch.py is still up.
#
#   ./scripts/save_map.sh small_room
set -euo pipefail

NAME="${1:-}"
if [ -z "${NAME}" ]; then
  echo "usage: ./scripts/save_map.sh <map_name>" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS="${REPO_ROOT}/ros2_ws"
OUT_DIR="${WS}/src/my_robot_maps/maps"

# shellcheck disable=SC1091
source /opt/ros/jazzy/setup.bash
# shellcheck disable=SC1091
source "${WS}/install/setup.bash"

# A 0-byte .pgm almost always means map_saver ran before /map had data, or
# the node was not in the active lifecycle state. Fail loudly instead.
if ! timeout 10 ros2 topic echo /map --once >/dev/null 2>&1; then
  echo "error: nothing publishing on /map. Is slam.launch.py running and active?" >&2
  echo "  ros2 lifecycle get /slam_toolbox" >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"
cd "${OUT_DIR}"

ros2 run nav2_map_server map_saver_cli -f "${NAME}" --ros-args -p use_sim_time:=true

PGM="${OUT_DIR}/${NAME}.pgm"
YAML="${OUT_DIR}/${NAME}.yaml"

fail=0
for f in "${PGM}" "${YAML}"; do
  if [ ! -s "${f}" ]; then
    echo "error: ${f} is missing or 0 bytes — do NOT commit this." >&2
    fail=1
  else
    echo "ok: ${f} ($(stat -c%s "${f}") bytes)"
  fi
done
[ "${fail}" -eq 0 ] || exit 1

echo
echo "Map saved. Review it before committing:"
echo "  eog ${PGM}   # or any image viewer"
