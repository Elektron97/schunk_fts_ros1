# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

This is a **ROS 1 (catkin/Noetic)** driver for SCHUNK force-torque sensors, living at
`catkin_ws/src/schunk_fts_ros1`. It is a single catkin package (`package.xml` name
`schunk_fts_ros1`, built with `catkin_python_setup()` + `add_service_files()`/`generate_messages()`),
not a colcon/ROS2 workspace. It provides:

- `src/schunk_fts_library/` — pure-Python, ROS-independent TCP/UDP protocol library (no `rospy`
  import). Installed via `catkin_python_setup()` (`setup.py` at repo root, `package_dir={'': 'src'}`).
- `scripts/schunk_fts_driver_node.py` — the actual ROS node (`SchunkROS1Driver`), a plain `rospy`
  node (no lifecycle state machine) that wraps the library with topics/services.
- `srv/` (repo root) — `SelectNoiseFilter.srv`, `SelectToolSetting.srv`, built by `CMakeLists.txt`'s
  `add_service_files`/`generate_messages`, producing `schunk_fts_ros1.srv.*` types.

**Note on repo history**: earlier versions of this repo (see `git log`, e.g. "ros1 porting") were a
four-package ROS2/colcon stack (`schunk_fts_library`, `schunk_fts_driver`, `schunk_fts_interfaces`,
plus a Rust `schunk_fts_dummy` simulator) using `rclpy` lifecycle nodes. That code has been ported
down to this single ROS1 package and **greatly simplified in the process** — there is still no
lifecycle node (see `MIGRATION_PLAN.md` and the `ros1-vs-ros2-mapping` skill for the full idiom
mapping and what remains deliberately unported, e.g. `SendCommand`/`SetParameter` services, a
`WrenchStampedBatch`-equivalent message type, `ERROR_CODE_MAP`). The `output_rate`/`500_16`
batch-streaming mode **has since been ported back in as an opt-in feature** (see "8kHz batch mode"
below) — don't assume the driver is single-sample-only without checking. Some repo-root config
files were stale leftovers from that older ROS2 layout; the Rust pre-commit hooks and the
devcontainer's Humble/colcon steps have been cleaned up, but re-check before trusting any docs that
predate that cleanup.

## Build

This must be built inside a catkin workspace (this repo is `<ws>/src/schunk_fts_ros1`):

```bash
source /opt/ros/noetic/setup.bash
cd ~/catkin_ws   # workspace root, one level above src/
rosdep install --from-paths src --ignore-src -y
catkin_make        # or `catkin build` if using catkin_tools
source devel/setup.bash
```

## Running against real hardware or the simulator

```bash
rosrun schunk_fts_ros1 schunk_fts_driver_node.py _ip:=192.168.0.100 _port:=82 _frame_id:=fts_link
rostopic echo /schunk/driver/data
```

`_ip`, `_port`, `_frame_id`, `_output_rate` are private (`~`) params read in
`SchunkROS1Driver.__init__` (`scripts/schunk_fts_driver_node.py`). A launch file also exists at
`launch/driver.launch`, exposing the same four as `<arg>`s.

## Tests

Tests live under `src/schunk_fts_library/tests/` and need either a running sensor (real or
simulated) reachable over TCP; the `sensor` fixture in
`src/schunk_fts_library/fixtures.py` picks one, in this order:
1. a prebuilt CI dummy binary at `/tmp/schunk_fts_dummy/debug/schunk_fts_dummy` (started
   automatically if present, requires `FTS_HOST`/`FTS_PORT` env vars also set),
2. a real sensor at `192.168.0.100:82`,
3. an already-running dummy on `127.0.0.1:8082` (polled for up to ~10s).

If none is reachable, sensor-dependent tests are skipped. Don't run a real sensor and a dummy at
the same time. There is no `schunk_fts_dummy` Rust simulator committed in this repo — the dummy
must be provided externally (e.g. via the CI binary path above, or run from wherever that project
lives outside this repo).

```bash
pip install --user pytest coverage
cd src/schunk_fts_library/tests
pytest .                          # or: pytest test_driver.py::test_name for a single test
coverage run -m pytest . && coverage report   # with coverage
```

There is no root `pytest.ini`, so run pytest from inside `src/schunk_fts_library/tests/`, not the
repo root.

## Linting / formatting

Managed through pre-commit (`black`, `flake8`, `mypy`):

```bash
pre-commit install
pre-commit run --all-files
```

The Rust `cargo-*` pre-commit hooks and the devcontainer's Humble/colcon/`schunk_fts_driver`
references (leftovers from the pre-port ROS2 layout) have been removed — `.pre-commit-config.yaml`
and `devcontainer_post_create.sh` now only reference things that actually exist in this repo. If
you find another stale reference like that, flag it rather than fixing it silently — cleaning it up
is a deliberate decision, not a side effect of an unrelated change.

## Architecture

### Wire protocol (`src/schunk_fts_library/utility.py`)

- `Connection` (TCP, command/parameter port, default `82`) and `Stream` (non-blocking UDP, data
  feed, default port `54843`) are the two socket wrappers. `Connection` is reference-counted via a
  `persistent` `Event` so `open()`/`close()` and nested `with` blocks interact safely; `close()`
  fully tears down and rebuilds the underlying socket (`_reset_socket`) so a later `open()` starts
  clean — important for the reconnect path below.
- Request/response framing is modeled by `Message` subclasses (`GetParameterRequest/Response`,
  `SetParameterRequest/Response`, `CommandRequest/Response`, `CommandWithParameterRequest`), each
  declaring `__fields__` and hex-encoding/decoding against the sensor's
  `sync + counter + payload_len + payload` framing.
- `FTDataBuffer.decode_packet()` decodes incoming UDP packets into `list[FTData]`, branching on
  `payload_len`: `29` bytes = one single sample (default `output_rate="1000"`), `449` bytes = a
  16-sample batch (`output_rate="500_16"`, 8kHz effective), anything else falls back to the
  unconditional single-sample layout. `FTData` is `TypedDict, total=False`; batch samples carry
  extra `sample_index`/`samples_per_packet` keys, single samples don't. `decode()` is a thin
  `decode_packet(data)[0]` shim kept for compatibility. `FTDataBuffer.get()` drains a
  `_pending_samples` deque first, so a caller doing `sample()` in a loop transparently gets one
  `FTData` per call regardless of whether the underlying packet was single or batch — see the
  `schunk-wire-protocol` skill for full byte-layout detail.

### `Driver` (`src/schunk_fts_library/driver.py`)

- Owns one `Connection` (TCP) and one `Stream` (UDP), plus a background thread
  (`stream_update_thread`) running `_update()` via `asyncio.run` that continuously reads UDP
  packets into `FTDataBuffer` and, when `auto_reconnect=True` (the `streaming_on()` default),
  detects a stalled stream (`timeout_sec`, default 0.1s) and calls `_attempt_reconnect()` in a loop
  until the sensor comes back — independent of the ROS layer.
- `streaming_on()` opens the TCP connection, starts the update thread, waits for the UDP socket to
  bind, reads the product name/ID parameters (index `0001`), configures the output rate
  (`_configure_output_rate()`, parameter `1020`/`00`; fails closed — connection is closed and
  `streaming_on()` returns `False` if the sensor rejects it), then issues the `start_udp_stream`
  command (`"40"`). `streaming_off()` reverses this (`"41"`, thread join, connection close).
- `Driver.__init__` takes `output_rate: int | str = 1000`, validated against `OUTPUT_RATE_TO_MODE`
  (`"1000"`/`"500"`/`"250"`/`"100"`/`"500_16"` — raises `ValueError` otherwise) and exposed as
  `output_rate_mode` (an `OutputRateMode` with `sample_period_ns`/`packet_period_ns`). Also takes
  `streaming_source_host` to restrict which UDP source IP `Stream` accepts packets from
  (`Stream._accepts_source`); `_attempt_reconnect()` re-runs `_configure_output_rate()` so a
  mid-stream sensor reboot doesn't silently drop back to the sensor's default rate.
- Sensor operations are thin wrappers around `run_command`/`get_parameter`/`set_parameter` using hex
  command IDs from the sensor's ICD, e.g. `tare` = `"12"`, `tare_reset` = `"13"`,
  `select_tool_setting` = `"30"` (0-3), `select_noise_filter` = `"31"` (0-4, factors 1/2/4/8/16).
  `select_tool_setting`/`select_noise_filter` validate their range client-side before sending.

### ROS node (`scripts/schunk_fts_driver_node.py`)

- `SchunkROS1Driver` is a plain object constructed in `__main__`, not a `rospy.Node` subclass and
  not a lifecycle node — `_connect()` builds the `Driver` (passing through `~output_rate`) and
  calls `sensor.streaming_on()` synchronously, called from `__init__`, which returns early on
  failure. `stream_data` then runs a daemon thread with no fixed-rate limiter (a `rospy.Rate` tick
  was only correct for exactly-one-sample-per-packet at `"1000"`; it loops tightly, calling
  `sample()` and publishing, sleeping briefly only when `sample()` returns `None`) and publishes
  one `geometry_msgs/WrenchStamped` per drained sample on `/schunk/driver/data` — **no new message
  type was introduced for batch mode** (that was an explicit MVP scope decision, see
  `MIGRATION_PLAN.md` §2 "Option A"; at `"500_16"` this means 16 individual `WrenchStamped`
  messages per UDP packet rather than one aggregate message). Per-sample timestamps in batch mode
  are reconstructed from a per-packet base `rospy.Time.now()` plus `sample_index *
  output_rate_mode.sample_period_ns`, not read fresh per sample — see the code comment in
  `stream_data` for why (all 16 samples arrive in one datagram, not evenly spaced in real time).
- Exposes three services under `/schunk/driver/`: `tare` (`std_srvs/Trigger`), `select_noise_filter`
  (`schunk_fts_ros1/SelectNoiseFilter`), `select_tool_setting` (`schunk_fts_ros1/SelectToolSetting`)
  — both custom services use plain `bool success, string message` responses (no ICD error-code
  mapping). The library also supports `tare_reset`, `set_parameter`, and raw `run_command`, but the
  node does not currently expose services for them.

## Key non-obvious constraints

- **Multiple sensors**: not possible over UDP — the streaming port is fixed on the sensor firmware
  side, so two sensors can't stream to distinct ports simultaneously. This is a hardware limit, not
  a driver gap.
- **Always edit the nested library copy**: protocol code lives only in
  `src/schunk_fts_library/{driver,utility,fixtures}.py` — there are no separate root-level shim
  files in this ROS1 layout (unlike the old ROS2 version this repo was ported from).
