#!/usr/bin/env bash
set -e

target_ws="${BASEDIR:-$HOME}/${PREFIX:-}target_ws"
repo_ws="$target_ws/src/${TARGET_REPO_NAME:-schunk_force_torque_sensor}"
if [ ! -d "$repo_ws" ]; then
  repo_ws="${TARGET_REPO_PATH:-/schunk_force_torque_sensor/src/schunk_force_torque_sensor}"
fi

cd "$repo_ws"

bash .github/script/install_dummy.sh

pip_args=()
if python3 -m pip install --help | grep -q -- "--break-system-packages"; then
  pip_args+=(--break-system-packages)
fi
python3 -m pip install "${pip_args[@]}" pytest

source "/opt/ros/${ROS_DISTRO}/setup.bash"
if [ -f "$target_ws/install/setup.bash" ]; then
  source "$target_ws/install/setup.bash"
elif [ -f /schunk_force_torque_sensor/install/setup.bash ]; then
  source /schunk_force_torque_sensor/install/setup.bash
fi

python3 -m pytest \
  schunk_fts_library/schunk_fts_library/tests
