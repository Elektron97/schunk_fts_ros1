std_msgs/Header header
# Counter of the source UDP packet; wraps after 65535.
uint16 packet_counter
# Sensor protocol identifier for the source UDP packet.
uint8 packet_id
# Number of sequential force-torque samples contained in this packet.
uint8 samples_per_packet
geometry_msgs/WrenchStamped[] samples
