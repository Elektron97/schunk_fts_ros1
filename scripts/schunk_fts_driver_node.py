#!/usr/bin/env python3
from __future__ import annotations

import threading
from typing import Optional

import rospy
from geometry_msgs.msg import WrenchStamped
from std_srvs.srv import Trigger, TriggerRequest, TriggerResponse

# IMPORT THE CORRECT CLASS
from schunk_fts_library.driver import Driver

from schunk_fts_ros1.srv import (
    SelectNoiseFilter,
    SelectNoiseFilterRequest,
    SelectNoiseFilterResponse,
    SelectToolSetting,
    SelectToolSettingRequest,
    SelectToolSettingResponse,
)

# Topic/service names, kept as module-level constants so the single string
# literal is shared between the rospy.Publisher/rospy.Service registration
# sites below (avoids drift/typos across the 4 registration sites).
DATA_TOPIC = "/schunk/driver/data"
TARE_SERVICE = "/schunk/driver/tare"
SELECT_NOISE_FILTER_SERVICE = "/schunk/driver/select_noise_filter"
SELECT_TOOL_SETTING_SERVICE = "/schunk/driver/select_tool_setting"


class SchunkROS1Driver:
    def __init__(self) -> None:
        rospy.init_node("schunk_fts_driver_ros1")

        # Parameters
        self.ip: str = rospy.get_param("~ip", "192.168.0.100")
        self.port: int = rospy.get_param("~port", 82)
        self.frame_id: str = rospy.get_param("~frame_id", "fts_link")
        self.output_rate: str = rospy.get_param("~output_rate", "1000")

        self.sensor: Optional[Driver] = None
        self.pub: Optional[rospy.Publisher] = None
        self.streaming_thread: Optional[threading.Thread] = None

        if not self._connect():
            return

        # Publishers
        self.pub = rospy.Publisher(DATA_TOPIC, WrenchStamped, queue_size=10)

        # Services
        rospy.Service(TARE_SERVICE, Trigger, self.handle_tare)
        rospy.Service(
            SELECT_NOISE_FILTER_SERVICE, SelectNoiseFilter, self.handle_filter
        )
        rospy.Service(SELECT_TOOL_SETTING_SERVICE, SelectToolSetting, self.handle_tool)

        # Start streaming thread
        self.streaming_thread = threading.Thread(target=self.stream_data)
        self.streaming_thread.daemon = True
        self.streaming_thread.start()

    def _connect(self) -> bool:
        """Initialize the sensor connection and start streaming.

        Returns True on success. On failure it logs the error and returns
        False, matching __init__'s previous early-return-from-constructor
        behavior (the caller must still return early from __init__ in that
        case).
        """
        # Initialize hardware connection using the correct class.
        # Driver() validates output_rate and raises ValueError for an
        # unsupported value - treat that the same as a failed connection
        # (log + return) rather than letting the node crash on a bad param.
        try:
            self.sensor = Driver(
                host=self.ip, port=self.port, output_rate=self.output_rate
            )
        except ValueError as e:
            rospy.logerr(f"Invalid ~output_rate '{self.output_rate}': {e}")
            return False

        # Use streaming_on() instead of connect()
        if self.sensor.streaming_on():
            rospy.loginfo(f"Connected to SCHUNK FTS at {self.ip}. Streaming started.")
            return True
        else:
            rospy.logerr(f"Failed to connect to {self.ip}")
            return False

    def stream_data(self) -> None:
        # No fixed-rate limiter here: sample() (via FTDataBuffer.get()) already
        # blocks for up to ~0.1s internally when nothing is queued, and returns
        # immediately when a sample is pending. A rospy.Rate(1000) tick was only
        # correct for exactly-one-sample-per-packet at 1000Hz; under "500-16"
        # batch mode, 16 samples surface back-to-back per 2ms packet and then
        # nothing until the next one, so we instead loop tightly and only sleep
        # briefly when sample() returns None (e.g. while not streaming, such as
        # during shutdown) to avoid busy-spinning.
        assert self.sensor is not None
        assert self.pub is not None
        last_counter: Optional[int] = None
        base_stamp: Optional[rospy.Time] = None
        while not rospy.is_shutdown():
            try:
                # Use sample() instead of receive_data()
                data = self.sensor.sample()
                if data:
                    sample_index = data.get("sample_index", 0)
                    counter = data.get("counter")

                    # A new packet starts either when the packet counter changes
                    # or when we see sample_index 0 again; capture a fresh base
                    # timestamp only at that point.
                    if (
                        last_counter is None
                        or counter != last_counter
                        or sample_index == 0
                    ):
                        base_stamp = rospy.Time.now()
                        last_counter = counter

                    if sample_index:
                        # Reconstruct this sample's timestamp from the packet's
                        # base timestamp instead of calling rospy.Time.now()
                        # again, since all 16 samples in a "500-16" batch packet
                        # arrive in a single UDP datagram, not evenly spaced in
                        # real time. This mirrors main's
                        # _calculate_sample_timestamp_ns (base + sample_index *
                        # sample_period_ns), but is a simplified, per-packet-as
                        # -drained version: main additionally reconciles counter
                        # gaps across a whole accumulated batch before
                        # publishing, which doesn't apply here since this node
                        # publishes one WrenchStamped per drained sample
                        # immediately rather than accumulating a batch first.
                        sample_period_ns = self.sensor.output_rate_mode.sample_period_ns
                        stamp = base_stamp + rospy.Duration(
                            nsecs=sample_index * sample_period_ns
                        )
                    else:
                        stamp = base_stamp

                    msg = WrenchStamped()
                    msg.header.stamp = stamp
                    msg.header.frame_id = self.frame_id

                    # FTData keys must match utility.py exactly
                    msg.wrench.force.x = data.get("fx", 0.0)
                    msg.wrench.force.y = data.get("fy", 0.0)
                    msg.wrench.force.z = data.get("fz", 0.0)
                    msg.wrench.torque.x = data.get("tx", 0.0)
                    msg.wrench.torque.y = data.get("ty", 0.0)
                    msg.wrench.torque.z = data.get("tz", 0.0)

                    self.pub.publish(msg)
                else:
                    # Nothing queued right now (e.g. not streaming during
                    # shutdown) - avoid a tight busy-loop.
                    rospy.sleep(0.01)
            except Exception as e:
                rospy.logwarn_throttle(1.0, f"Data stream error: {e}")

        # Clean shutdown
        self.sensor.streaming_off()

    def handle_tare(self, req: TriggerRequest) -> TriggerResponse:
        assert self.sensor is not None
        try:
            self.sensor.tare()
            return TriggerResponse(success=True, message="Sensor tared.")
        except Exception as e:
            return TriggerResponse(success=False, message=str(e))

    def handle_filter(self, req: SelectNoiseFilterRequest) -> SelectNoiseFilterResponse:
        assert self.sensor is not None
        if req.filter_number > 4:
            return SelectNoiseFilterResponse(success=False, message="Invalid. Use 0-4.")
        try:
            self.sensor.select_noise_filter(req.filter_number)
            return SelectNoiseFilterResponse(
                success=True, message=f"Filter set to {req.filter_number}"
            )
        except Exception as e:
            return SelectNoiseFilterResponse(success=False, message=str(e))

    def handle_tool(self, req: SelectToolSettingRequest) -> SelectToolSettingResponse:
        assert self.sensor is not None
        if req.tool_index > 3:
            return SelectToolSettingResponse(success=False, message="Invalid. Use 0-3.")
        try:
            self.sensor.select_tool_setting(req.tool_index)
            return SelectToolSettingResponse(
                success=True, message=f"Tool set to {req.tool_index}"
            )
        except Exception as e:
            return SelectToolSettingResponse(success=False, message=str(e))


if __name__ == "__main__":
    try:
        driver = SchunkROS1Driver()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
