# SCHUNK FTS Interfaces

Custom ROS2 message and service definitions for SCHUNK force-torque sensor driver.

## Dependencies

Add to your `package.xml`:
```xml
<depend>schunk_fts_interfaces</depend>
```
Subscribers to `/schunk/fts/data` need this package when the driver runs with `output_rate=500_16`, because that mode publishes `schunk_fts_interfaces/WrenchStampedBatch` instead of `geometry_msgs/WrenchStamped`.
