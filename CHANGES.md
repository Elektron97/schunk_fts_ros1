# What's new in this version

This document explains the changes made while porting the ROS2 `main` branch's 8kHz batch-streaming
support onto this ROS1/catkin fork, and how to use the resulting driver. For the full rationale and
the diff classification behind these changes, see `MIGRATION_PLAN.md`; for the ROS1/ROS2 idiom
mapping, see `.claude/skills/ros1-vs-ros2-mapping/SKILL.md`.

## Summary of changes

1. **Opt-in 8kHz batch streaming** — a new `output_rate` setting lets the sensor stream 16 samples
   per UDP packet (8000 samples/sec effective) instead of one. Off by default; existing behavior is
   unchanged unless you explicitly opt in.
2. **Reconnection and stream hardening** — UDP source-IP filtering, a reentrant lock around the
   stream socket, dropped-packet counting, and output-rate reconfiguration on reconnect.
3. **A launch file** — `launch/driver.launch`, where previously only `rosrun` with manual `_arg:=`
   overrides was documented.
4. **Node-code clarity and type hints** — named topic/service constants, a separated connection
   step, and full type annotations on the node script.
5. **Stale config removed** — the leftover ROS2/Rust references in `.pre-commit-config.yaml` and
   `devcontainer_post_create.sh` are gone; both now only reference things that actually exist in
   this repo.

None of this changes the default behavior: run the node with no extra arguments and you get exactly
the same single-sample-at-1000Hz stream as before.

## Usage

### Running the node

Unchanged for the default case:

```bash
rosrun schunk_fts_ros1 schunk_fts_driver_node.py _ip:=192.168.0.100 _port:=82 _frame_id:=fts_link
rostopic echo /schunk/driver/data
```

New: a launch file, equivalent to the above but with named args:

```bash
roslaunch schunk_fts_ros1 driver.launch ip:=192.168.0.100 port:=82 frame_id:=fts_link
```

Both accept the same four settings; the launch file's `<arg>` defaults match the node's own
parameter defaults (`ip=192.168.0.100`, `port=82`, `frame_id=fts_link`, `output_rate=1000`).

### Enabling 8kHz batch mode

Set `output_rate` to `"500-16"` (the sensor's batch-streaming mode: 500 packets/sec × 16 samples =
8000 samples/sec):

```bash
rosrun schunk_fts_ros1 schunk_fts_driver_node.py _ip:=192.168.0.100 _output_rate:=500-16
# or
roslaunch schunk_fts_ros1 driver.launch output_rate:=500-16
```

Other supported values: `"1000"` (default), `"500"`, `"250"`, `"100"` — these are all still
single-sample-per-packet, just at different rates; only `"500-16"` engages the batch path. An
unsupported value (e.g. `_output_rate:=8000`) is rejected at startup with a logged error rather
than crashing the node.

> **Note on the delimiter**: this value is spelled with a hyphen (`500-16`), not an underscore
> (`500_16`) as in some earlier drafts of this feature. `rosrun _output_rate:=500_16` (and any
> other rosparam/YAML-based way of setting it) silently turned `"500_16"` into the integer `50016`
> before it ever reached validation, because YAML 1.1 and Python's `int()` both treat `_` as a
> digit-group separator — the batch rate could never actually be selected from the documented CLI
> syntax. A hyphen isn't part of any numeric literal grammar those parsers use, so `"500-16"`
> always survives as a plain string. See GH issue #1.

**What batch mode looks like on the topic side**: `/schunk/driver/data` still only ever publishes
`geometry_msgs/WrenchStamped` — there's no new message type. At `"500-16"`, the node publishes 16
individual `WrenchStamped` messages per UDP packet (i.e. `rostopic hz /schunk/driver/data` should
read close to 8000, not 500) instead of one aggregate message with an array field. This was a
deliberate scope decision (see `MIGRATION_PLAN.md` §2, "Option A") to avoid introducing a new custom
message type and the extra `CMakeLists.txt`/`msg/` surface that would require; it's revisitable if
a future application needs the packet-level metadata (`packet_counter`, `packet_id`) that a batch
message would preserve.

**Timestamp accuracy in batch mode**: all 16 samples in one packet arrive in a single UDP datagram,
not evenly spaced in real time. Rather than stamping each with `rospy.Time.now()` at publish time
(which would bunch all 16 timestamps together), the node reconstructs each sample's timestamp from
one base timestamp per packet plus `sample_index * sample_period_ns` (125µs steps at 8kHz). This is
a simplified version of the equivalent ROS2 logic — see the comment in `stream_data()` in
`scripts/schunk_fts_driver_node.py` for the specifics of what's simplified and why.

### Services (unchanged)

```bash
rosservice call /schunk/driver/tare
rosservice call /schunk/driver/select_tool_setting "tool_index: 0"      # 0-3
rosservice call /schunk/driver/select_noise_filter "filter_number: 2"   # 0-4
```

### Reconnection behavior

The driver already auto-reconnected on a stalled UDP stream (e.g. sensor power loss); that's
unchanged. What's new: on reconnect, the driver now also re-sends the `output_rate` configuration
to the sensor, so a mid-stream sensor reboot doesn't silently fall back to the sensor's own default
rate while your node still thinks it's in batch mode.

### Testing

No change to the test-running instructions in `CLAUDE.md`:

```bash
cd src/schunk_fts_library/tests
pytest .
```

The new batch-decode tests (`test_data_buffer.py`, `test_protocol.py`, `test_driver.py`) use
synthetic packet bytes and don't need a live sensor or dummy simulator; the rest of the suite still
needs one, per the existing `sensor` fixture behavior.

## What's still not ported

For completeness — these exist on the ROS2 `main` branch but were deliberately left out of this
round, per `MIGRATION_PLAN.md`:

- A dedicated batch/`WrenchStampedBatch`-style message type (see "batch mode" above).
- `Driver.sample_batch()` / the tuple-based `FTSample` consumer API — only the dict-based
  `sample()` path exists in this fork.
- `SendCommand`/`SetParameter` ROS services (the underlying library methods exist, just no service
  wrapper) and an `ERROR_CODE_MAP` translation layer on service responses.
- A lifecycle state machine (`configure`/`activate`/... ) — this node has never had one, ROS1 or
  ROS2 lifecycle both being out of scope for this fork.
