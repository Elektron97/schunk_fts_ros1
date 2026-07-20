#!/bin/bash

# Command to be run within the "postCreateCommand" field of devcontainer.json

set -e  # exit on first error

# Install and setup git
apt update
apt install -y git
git config --global --add safe.directory /workspace/src

# Ensure system dependencies are installed
rosdep update
rosdep install --from-paths /workspace/src --ignore-src -y

# Install and setup pre-commit
pip install pre-commit
cd /workspace/src
pre-commit install
cd /workspace

# Build the ROS workspace
source /opt/ros/noetic/setup.bash
cd /workspace
catkin_make
# Overlay the production workspace
source /workspace/devel/setup.bash
echo 'source /workspace/devel/setup.bash' >> /etc/bash.bashrc

echo "post_create_command.sh completed."
