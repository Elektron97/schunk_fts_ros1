#!/usr/bin/env bash
set -e

if [ "${ROS_DISTRO:-}" != "humble" ]; then
  echo "Skipping pytest downgrade for ROS_DISTRO=${ROS_DISTRO:-unset}"
  exit 0
fi

python3 -m pip install --force-reinstall pytest==8.4.2
python3 -m pytest --version
