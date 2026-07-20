---
name: ros1-vs-ros2-mapping
description: Idiom translation table between the ROS2/colcon original (main branch) and this ROS1/catkin fork (ros1 branch) of the SCHUNK FTS driver, plus this fork's deliberate simplifications. Load this before porting any ROS2 driver/node/build-system change to ROS1 — the goal is a faithful idiom translation, not a re-import of stripped machinery.
---

# ROS1 (this fork) vs. ROS2 (`main`) idiom mapping

This fork ported a 4-package ROS2/colcon stack down to a single ROS1/catkin package and
**deliberately dropped several ROS2-only subsystems in the process** (see "Deliberate
simplifications" below). When translating a ROS2 change, first classify it as plumbing
(translate it) vs. dropped machinery (don't blindly resurrect it — flag it for the human instead).

## Build system

| ROS2 (`main`) | ROS1 (this fork) |
|---|---|
| 4 colcon packages: `schunk_fts_library`, `schunk_fts_driver`, `schunk_fts_interfaces`, `schunk_fts_dummy` (Rust, not built by colcon) | 1 catkin package: `schunk_fts_ros1` |
| `ament_python` (`schunk_fts_library`, `schunk_fts_driver`) + `ament_cmake` (`schunk_fts_interfaces`) | `catkin_python_setup()` + `add_service_files()`/`generate_messages()` in one `CMakeLists.txt`/`package.xml` |
| `colcon build --symlink-install` | `catkin_make` (or `catkin build`) from the workspace root |
| Root-level one-line shim files re-exporting the nested package (`schunk_fts_library/driver.py` → `from schunk_fts_library.schunk_fts_library.driver import *`), needed so `ament_python`'s `data_files` could install a script | **No shims in this fork** — `src/schunk_fts_library/{driver,utility,fixtures}.py` are the real files directly, `package_dir={'': 'src'}` in `setup.py` handles it |
| `.srv` files live in the separate `schunk_fts_interfaces` package, `ament_cmake` build | `.srv` files live at repo root (`srv/`), built by this package's own `CMakeLists.txt` |
| `rosdep install --from-paths . --ignore-src -y` run from repo root | `rosdep install --from-paths src --ignore-src -y` run from workspace root (repo is `<ws>/src/schunk_fts_ros1`) |

## Node lifecycle and structure

| ROS2 (`main`) | ROS1 (this fork) |
|---|---|
| `Driver(Node)` from `rclpy.lifecycle`, explicit `on_configure`/`on_activate`/`on_deactivate`/`on_cleanup`/`on_shutdown` state machine | `SchunkROS1Driver`, a plain object (not even a `rospy` node subclass) — connects and calls `sensor.streaming_on()` synchronously in `__init__`, no state machine at all |
| Publishers/services/timers created in `on_activate`, torn down in `on_deactivate` | Publisher and all services created once in `__init__`; a daemon `threading.Thread` (`stream_data`) does the publish loop instead of an `rclpy` timer — no fixed `rospy.Rate`, it loops tightly and relies on `sample()`'s internal blocking wait for pacing (see "Parameters" row on `output_rate` for why a fixed rate doesn't work once batch mode is enabled) |
| `ros2 lifecycle set /schunk/fts configure` / `activate` | Nothing to drive — the node is "active" as soon as it starts (`rosrun schunk_fts_ros1 schunk_fts_driver_node.py`) |
| `rclpy.spin(node)` | `rospy.spin()` |

## Parameters

| ROS2 (`main`) | ROS1 (this fork) |
|---|---|
| `self.declare_parameter("output_rate", "1000")` + `self.get_parameter("output_rate").value` | `rospy.get_param('~ip', '192.168.0.100')` etc. — private (`~`) params read directly in `__init__`, no declare step |
| Set via `ros2 launch ... output_rate:=500-16` or `ros2 param set` | Set via `rosrun ... _ip:=... _port:=... _frame_id:=... _output_rate:=...` or `launch/driver.launch`'s `<arg>`s (`ip`/`port`/`frame_id`/`output_rate`) |
| Params: `ip`/`host`, `port`, `frame_id`, `output_rate` | Params: `ip`, `port`, `frame_id`, `output_rate` — **ported as of `MIGRATION_PLAN.md`'s 8kHz batch-mode work**, same supported values (`"1000"`/`"500"`/`"250"`/`"100"`/`"500-16"`), default `"1000"` |

## Services

| ROS2 (`main`) | ROS1 (this fork) |
|---|---|
| `.srv` types defined in `schunk_fts_interfaces`: `SelectToolSetting`, `SelectNoiseFilter`, `SendCommand`, `SetParameter` | Only `SelectToolSetting` and `SelectNoiseFilter` exist as custom `.srv` in `srv/`; `SendCommand`/`SetParameter` were **not ported** — the library methods (`run_command`, `set_parameter`) exist but have no ROS1 service wrapper |
| Service responses map the ICD `error_code` through `ERROR_CODE_MAP` onto a human-readable `error_message`/`message` field | This fork's `SelectNoiseFilter`/`SelectToolSetting` responses are plain `bool success, string message` — no `ERROR_CODE_MAP`, no error-code translation layer |
| `tare` and `reset_tare` both exposed as services | Only `tare` is exposed (`std_srvs/Trigger`); `reset_tare`/`tare_reset` is not wired to a service despite existing on `Driver` |

## Topics / message types

| ROS2 (`main`) | ROS1 (this fork) |
|---|---|
| Normal rates: `geometry_msgs/WrenchStamped` on `/schunk/fts/data`. `output_rate="500-16"`: `schunk_fts_interfaces/WrenchStampedBatch` instead (16 samples/msg, `packet_counter`/`packet_id`/`samples_per_packet` + `samples[]`) | Always `geometry_msgs/WrenchStamped` on `/schunk/driver/data`, **at every `output_rate` including `"500-16"`** — this fork deliberately chose not to add a `WrenchStampedBatch`-equivalent message (Option A in `MIGRATION_PLAN.md` §2); at `"500-16"` the node publishes 16 individual `WrenchStamped` messages per UDP packet instead of one aggregate message, with per-sample timestamps reconstructed from a per-packet base timestamp + `sample_index * sample_period_ns` |

## Testing / simulator

| ROS2 (`main`) | ROS1 (this fork) |
|---|---|
| `schunk_fts_dummy/` Rust/Tokio simulator committed in-repo, built via `cargo`, wired into CI (`.github/script/install_dummy.sh`) | No dummy simulator committed in this repo at all — tests rely on a prebuilt CI binary path (`/tmp/schunk_fts_dummy/debug/schunk_fts_dummy`), a real sensor, or an externally-run dummy |
| Driver tests exercise lifecycle transitions, QoS, `rclpy` timers | No driver-level test suite in this fork — only `src/schunk_fts_library/tests/` (protocol-layer tests) exist; the node script has no tests |

## Deliberate simplifications (don't silently re-add these)

These were intentionally stripped when porting to ROS1, per the repo's `CLAUDE.md`. If a ROS2
change depends on one of these, **surface it to the user as a scope decision rather than porting
it transparently**:

1. **No lifecycle state machine.** The ROS1 node has no configure/activate/deactivate states.
   Don't reintroduce a state machine to "faithfully" port a lifecycle-callback change — translate
   its *effect* (e.g. what happens on activate) into the flat `__init__`/thread structure instead.
2. **`output_rate`/batch mode: ported, no longer stripped.** As of the `MIGRATION_PLAN.md` 8kHz
   work, this fork *does* support `output_rate` (`Driver.__init__`, `~output_rate` ROS param,
   `launch/driver.launch`) and 16-sample batch decode (`FTDataBuffer.decode_packet`). Don't assume
   single-sample-only. What's still *not* ported from `main`'s batch handling: a
   `WrenchStampedBatch`-equivalent message (this fork publishes one `WrenchStamped` per drained
   sample instead — see the Topics row above), `Driver.sample_batch()`/the tuple-based `FTSample`
   consumer API (only the `FTData`-dict path via `sample()` exists here), and `main`'s
   whole-batch-aware counter-gap reconciliation in its timestamp math (this fork's node
   reconstructs timestamps per-packet-as-drained, a deliberate simplification — see the comment in
   `stream_data`). Adding any of those is still a separate, explicit decision.
3. **No `schunk_fts_interfaces`-equivalent package.** `SendCommand`/`SetParameter` services don't
   exist here. Adding them means extending *this* package's own `srv`/`msg` (there's no separate
   interfaces package to mirror), and should be a deliberate decision, not incidental to another
   port.
4. **No `ERROR_CODE_MAP` translation layer** in service responses — current responses are boolean
   success + free-text message. Introducing ICD error-code mapping is an improvement to propose,
   not something to assume already-intended.
