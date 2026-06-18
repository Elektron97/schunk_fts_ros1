#!/usr/bin/env python3
import rospy
import threading
from geometry_msgs.msg import WrenchStamped
from std_srvs.srv import Trigger, TriggerResponse

# IMPORT THE CORRECT CLASS
from schunk_fts_library.driver import Driver 

from schunk_fts_ros1.srv import SelectNoiseFilter, SelectNoiseFilterResponse
from schunk_fts_ros1.srv import SelectToolSetting, SelectToolSettingResponse

class SchunkROS1Driver:
    def __init__(self):
        rospy.init_node('schunk_fts_driver_ros1')
        
        # Parameters
        self.ip = rospy.get_param('~ip', '192.168.0.100')
        self.port = rospy.get_param('~port', 82)
        self.frame_id = rospy.get_param('~frame_id', 'fts_link')
        
        # Initialize hardware connection using the correct class
        self.sensor = Driver(host=self.ip, port=self.port)
        
        # Use streaming_on() instead of connect()
        if self.sensor.streaming_on():
            rospy.loginfo(f"Connected to SCHUNK FTS at {self.ip}. Streaming started.")
        else:
            rospy.logerr(f"Failed to connect to {self.ip}")
            return

        # Publishers
        self.pub = rospy.Publisher('/schunk/driver/data', WrenchStamped, queue_size=10)
        
        # Services
        rospy.Service('/schunk/driver/tare', Trigger, self.handle_tare)
        rospy.Service('/schunk/driver/select_noise_filter', SelectNoiseFilter, self.handle_filter)
        rospy.Service('/schunk/driver/select_tool_setting', SelectToolSetting, self.handle_tool)

        # Start streaming thread
        self.streaming_thread = threading.Thread(target=self.stream_data)
        self.streaming_thread.daemon = True
        self.streaming_thread.start()

    def stream_data(self):
        rate = rospy.Rate(1000)
        while not rospy.is_shutdown():
            try:
                # Use sample() instead of receive_data()
                data = self.sensor.sample()
                if data:
                    msg = WrenchStamped()
                    msg.header.stamp = rospy.Time.now()
                    msg.header.frame_id = self.frame_id
                    
                    # FTData keys must match utility.py exactly
                    msg.wrench.force.x = data.get("fx", 0.0)
                    msg.wrench.force.y = data.get("fy", 0.0)
                    msg.wrench.force.z = data.get("fz", 0.0)
                    msg.wrench.torque.x = data.get("tx", 0.0)
                    msg.wrench.torque.y = data.get("ty", 0.0)
                    msg.wrench.torque.z = data.get("tz", 0.0)
                    
                    self.pub.publish(msg)
            except Exception as e:
                rospy.logwarn_throttle(1.0, f"Data stream error: {e}")
            rate.sleep()

        # Clean shutdown
        self.sensor.streaming_off()

    def handle_tare(self, req):
        try:
            self.sensor.tare()
            return TriggerResponse(success=True, message="Sensor tared.")
        except Exception as e:
            return TriggerResponse(success=False, message=str(e))

    def handle_filter(self, req):
        if req.filter_number > 4:
            return SelectNoiseFilterResponse(success=False, message="Invalid. Use 0-4.")
        try:
            self.sensor.select_noise_filter(req.filter_number)
            return SelectNoiseFilterResponse(success=True, message=f"Filter set to {req.filter_number}")
        except Exception as e:
            return SelectNoiseFilterResponse(success=False, message=str(e))

    def handle_tool(self, req):
        if req.tool_index > 3:
            return SelectToolSettingResponse(success=False, message="Invalid. Use 0-3.")
        try:
            self.sensor.select_tool_setting(req.tool_index)
            return SelectToolSettingResponse(success=True, message=f"Tool set to {req.tool_index}")
        except Exception as e:
            return SelectToolSettingResponse(success=False, message=str(e))

if __name__ == '__main__':
    try:
        driver = SchunkROS1Driver()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass