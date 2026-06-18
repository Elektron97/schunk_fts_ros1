cmake_minimum_required(VERSION 3.0.2)
project(schunk_fts_ros1)

find_package(catkin REQUIRED COMPONENTS
  rospy
  geometry_msgs
  std_srvs
  message_generation
)

catkin_python_setup()

# Register the service files you created
add_service_files(
  FILES
  SelectNoiseFilter.srv
  SelectToolSetting.srv
)

# Generate the service messages
generate_messages(
  DEPENDENCIES
  std_msgs
)

catkin_package(
  CATKIN_DEPENDS rospy geometry_msgs std_srvs message_runtime
)

# Install the python script
catkin_install_python(PROGRAMS
  scripts/schunk_fts_driver_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)