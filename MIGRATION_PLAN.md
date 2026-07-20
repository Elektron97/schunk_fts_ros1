# Migration plan: porting ROS2 (`main`) changes onto the ROS1 fork (`ros1`)

Fork point: `b0e4359` (common ancestor of `main` and `ros1`, per `git merge-base main ros1`).
`main` has since diverged by 5 PRs / ~30 commits (notably `#18 codebase-maintenance` and
`#19 8kHz-support`); `ros1` has diverged by the single `d9dda6d "ros1 porting"` + `80cc52f` bugfix
commits that restructured the whole tree into one catkin package (see `CLAUDE.md`).

This plan covers scaffolding review, the diff classification, the 8kHz batch-mode design, stale
config cleanup, moderate ROS1-side improvements, and test strategy. **No implementation yet** —
this is for approval.

---

## 1. Diff: `main` vs. fork point, classified

`git diff --stat b0e4359 main` shows 74 files changed. Grouped by area and classified as
**library-logic** (ROS-independent, belongs in `src/schunk_fts_library/`, relevant to port),
**ROS2-plumbing** (lifecycle/rclpy-specific, needs idiom translation, not verbatim porting), or
**irrelevant-to-ROS1** (doesn't apply to this fork's scope):

| Area | Files | Classification | Notes |
|---|---|---|---|
| Output-rate + batch decode | `schunk_fts_library/schunk_fts_library/{driver,utility}.py` | **library-logic** | `OUTPUT_RATE_TO_MODE`, `_normalize_output_rate`, `_configure_output_rate`, `FTDataBuffer.decode_packet`/`decode_sample_batch` (449-byte batch format), `Driver.sample_batch()`. This is the 8kHz feature — see §2. |
| UDP source-IP filtering | `utility.py` `Stream.__init__(source_host=...)`, `_resolve_source_ip` | **library-logic** | Restricts accepted UDP datagrams to a resolved source IP; independent of ROS2, worth porting on its own merits (hardening) regardless of batch-mode decision. |
| Reconnection/thread-safety hardening | `driver.py` `_streaming_lock`, `RLock` on `Stream`, `dropped_packet_count`, `clear_samples()`, `_pending_samples` deque | **library-logic** | General robustness improvements independent of `output_rate`. Worth porting even if batch mode is deferred. |
| ROS2 lifecycle node changes | `schunk_fts_driver/schunk_fts_driver/driver.py` (251 lines changed): `declare_parameter("output_rate")`, `WrenchStampedBatch` publishing, `_publish_sample_batches`, `_calculate_sample_timestamp_ns`, `_fill_wrench_stamped`, `_publish_samples`, `ERROR_CODE_MAP` service responses | **ROS2-plumbing** | The *timestamp reconstruction math* in `_calculate_sample_timestamp_ns` is protocol-relevant and should inform the ROS1 node's batch handling (§2), but the lifecycle/`rclpy` structure itself is not portable as-is — see `ros1-vs-ros2-mapping` skill. |
| `schunk_fts_interfaces` additions | `WrenchStampedBatch.msg`, `SendCommand.srv`, `SetParameter.srv`, `CMakeLists.txt` | **ROS2-plumbing / design decision** | No interfaces package exists in this fork; these would become new files in this package's own `srv/`/`msg/` if ported. `SendCommand`/`SetParameter` are out of scope for this plan (not requested); `WrenchStampedBatch`-equivalent is a decision point in §2. |
| ROS2 driver tests | `schunk_fts_driver/schunk_fts_driver/tests/*` (lifecycle, QoS, threading, topics, services) | **irrelevant-to-ROS1** | Exercise `rclpy` lifecycle/QoS machinery this fork doesn't have. Not portable; any new ROS1 node tests would need to be written fresh against `rospy`. |
| `schunk_fts_dummy` Rust simulator | `Cargo.{toml,lock}`, `src/{main,output_rate,sensor,tcp,udp}.rs` | **irrelevant-to-ROS1 (for this repo)** | Not committed in `ros1` at all (see `CLAUDE.md`'s "stale config" note — it's still *referenced* by pre-commit but doesn't exist here). The updated dummy now emits 500-16 batch packets and honors the output-rate parameter — needed to test batch mode locally, but as an external dependency, not something this plan adds to this repo. Flagged for test strategy in §5. |
| Package metadata / READMEs | `*/package.xml` version bumps, `*/README.md` updates | **irrelevant-to-ROS1** | ROS2 package versioning and colcon-package docs; this fork has its own single `package.xml`/root `README.md` already reflecting its own state. |
| CI / Dockerfiles / devcontainer (ROS2 side) | Referenced by commit messages (`Refactor CI workflows...`, `Update Dockerfiles...`) | **irrelevant-to-ROS1** | This fork has no `.github/` workflows and no devcontainer Dockerfile variants; `devcontainer_post_create.sh` here is a separate, already-stale artifact (§3), not something to sync from `main`. |
| `security/` CVE scanner + reports | `security/cve_scanner.py`, `security/reports/*` | **irrelevant-to-ROS1** | Standalone CVE tooling per `CLAUDE.md`, unrelated to the driver; not present in `ros1` at all. |

**Net scope of this plan**: port the library-logic row (output-rate/batch decode, source-IP
filtering, reconnection hardening) into `src/schunk_fts_library/`, translate the batch-relevant
*behavior* (not structure) of the ROS2 node into `scripts/schunk_fts_driver_node.py`, and leave
everything marked irrelevant-to-ROS1 untouched.

---

## 2. 8kHz batch mode as opt-in

**Goal**: single-sample streaming (current, default) is unchanged byte-for-byte; batch mode is
strictly additive and only engages when explicitly requested.

### Parameter

Add a new private param `~output_rate` (string) to `scripts/schunk_fts_driver_node.py`, read
alongside `~ip`/`~port`/`~frame_id`. Proposed values, matching `main`'s
`SUPPORTED_OUTPUT_RATES` exactly for naming consistency across branches (this matters for future
re-diffing/re-porting, per the `ros1-vs-ros2-mapping` skill's philosophy):

```
~output_rate: "1000" (default) | "500" | "250" | "100" | "500-16"
```

Default `"1000"` preserves current behavior exactly. Only `"500-16"` engages batch decoding
(500 packets/s × 16 samples/packet = 8000 samples/s effective).

### Library changes (`protocol-library-porter` scope)

1. Port `OutputRateMode`/`OUTPUT_RATE_TO_MODE`/`_normalize_output_rate` into
   `src/schunk_fts_library/driver.py`; add `output_rate` constructor param to `Driver`, and
   `_configure_output_rate()` (writes parameter index `1020`/subindex `00` — this is protocol
   metadata already covered by the wire-protocol skill's `set_parameter` mechanism, just a new
   caller).
2. Extend `FTData` (TypedDict) with optional `sample_index`/`samples_per_packet` fields, matching
   `main`.
3. Replace `FTDataBuffer.decode()` with `main`'s `decode_packet()` (list-returning, branches on
   `payload_len`: 29 = single sample, 449 = 16-sample batch, per the `schunk-wire-protocol` skill)
   plus the `_pending_samples` deque in `.get()`. This is the key design choice that keeps the
   *default* path unaffected: at `output_rate="1000"`, every packet is still 29 bytes, decodes to
   a 1-element list, and `sample()`'s public behavior/signature is unchanged. `sample_batch()` is
   **not** part of this MVP (`Driver.sample()` alone, transparently draining the pending-samples
   queue, is sufficient — see node-side handling below); add it later only if a caller needs the
   lower-overhead tuple form.
4. Port the source-IP filtering and reconnection/locking hardening (`_streaming_lock`, `RLock`,
   `dropped_packet_count`, `clear_samples()`) at the same time — they're independent improvements
   bundled into the same `main` commits, and skipping them would mean re-diffing `utility.py`
   twice.

### Node changes (`ros2-to-ros1-translator` scope)

The current `stream_data` loop assumes exactly one sample per `rospy.Rate(1000)` tick — this
assumption breaks under batch mode two ways, both needing explicit handling, not a silent
carry-over:

1. **Sample cadence**: at `500-16`, packets arrive every 2ms but each contains 16 samples (8000
   samples/s). Since `FTDataBuffer.get()` (via `_pending_samples`) already drains one sample per
   call regardless of batching, the minimal fix is to decouple the loop from a fixed 1000Hz
   `rospy.Rate` and instead drain-and-publish in a tight loop with a short sleep when the buffer is
   empty (rather than a fixed-period `Rate.sleep()`), so 16x the call rate doesn't require guessing
   the right fixed rate up front for every `output_rate` value.
2. **Timestamps**: `rospy.Time.now()` at dequeue time is not accurate per-sample once 16 samples
   are drained in a burst. Port the reconstruction math from `main`'s
   `_calculate_sample_timestamp_ns` (base packet timestamp + `sample_index * sample_period_ns`,
   with `sample_period_ns` derived from the `OutputRateMode` table) into the ROS1 node — this is
   the one piece of "ROS2-plumbing" from §1 whose *logic* (not its `rclpy` packaging) is worth
   porting directly.

### Open decision: new batch message type

`main` publishes `schunk_fts_interfaces/WrenchStampedBatch` (packet-level metadata + 16 embedded
`WrenchStamped`s) at `500-16`. This fork has no interfaces-equivalent package. Two options —
**recommend Option A for the initial opt-in**, with Option B as a documented follow-up:

- **Option A (recommended MVP)**: keep the topic type as plain `geometry_msgs/WrenchStamped` on
  `/schunk/driver/data` always. In batch mode, publish 16 individual `WrenchStamped` messages per
  packet (one per drained sample, each with its reconstructed timestamp). Simpler, no new
  build-system surface, but loses packet-level metadata (`packet_counter`, `packet_id`,
  `samples_per_packet`) that `main` preserves.
- **Option B**: add a `WrenchStampedBatch`-equivalent `.msg` to this package's own `msg/`
  directory (new `add_message_files`/`generate_messages` entries in `CMakeLists.txt`, new
  `message_generation`/`message_runtime` deps already present in `package.xml`), and switch topic
  type conditionally on `output_rate`, mirroring `main`'s `_publish_sample_batches` flag. More
  faithful to `main`, more build-system surface, larger review footprint.

**Please confirm which option you want before implementation** — this is the one part of the plan
that changes the public topic contract.

---

## 3. Stale config cleanup

Per `CLAUDE.md`'s explicit callout, two files reference the pre-port ROS2 layout and will fail as-is:

1. **`.pre-commit-config.yaml`**: remove the four Rust hooks (`cargo-fmt`, `cargo-check`,
   `cargo-clippy`, `cargo-test`), all pointed at `schunk_fts_dummy/Cargo.toml`, which doesn't exist
   in this repo. No Rust code is committed here.
2. **`devcontainer_post_create.sh`**: remove `pip install -e /workspace/src/schunk_fts_driver`
   (package doesn't exist) and `pip install -e /workspace/src/schunk_fts_library` (this fork uses
   `catkin_python_setup()`, not a separately pip-installable package — the existing
   `catkin_make` + `source /workspace/install/setup.bash` steps already make
   `schunk_fts_library` importable via the catkin devel/install space, which is how the test suite
   presumably resolves imports today with no `pytest.ini`/`pythonpath` config). Replace the
   `source /opt/ros/humble/setup.bash` line with `source /opt/ros/noetic/setup.bash`, and swap
   `colcon build --symlink-install` for `catkin_make` against a catkin workspace layout.

Both are small, mechanical, low-risk edits — no behavior change to the driver itself.

---

## 4. Moderate ROS1 improvements

Scoped narrowly to what was requested — not a broader refactor:

1. **Clarity refactors** in `scripts/schunk_fts_driver_node.py`: extract topic/service name
   string literals (`/schunk/driver/data`, `/schunk/driver/tare`, etc.) to module-level constants
   (mirrors how `driver.py`'s command hex IDs are at least grouped, and avoids typos across the
   3 service registrations + 1 publisher); keep `__init__` focused on wiring, with the
   connect-and-verify step (`streaming_on()` + its error branch) as a small separate method for
   readability. No change in behavior.
2. **Launch file**: add `launch/driver.launch` (ROS1 XML launch, since none exists yet) exposing
   `ip`, `port`, `frame_id` (and `output_rate` once §2 lands) as `<arg>`s passed through to
   `<param>`s, matching the `rosrun ... _ip:=...` args already documented in `CLAUDE.md` so both
   invocation styles stay equivalent.
3. **Type hints**: `scripts/schunk_fts_driver_node.py` currently has none, unlike the library
   (which uses `from __future__ import annotations` throughout). Add type hints to the node's
   methods/attributes and confirm `mypy` (already run repo-wide per `.pre-commit-config.yaml`)
   passes on it — check whether `scripts/` needs adding to `.mypy.ini`'s scope, since the current
   exclude list (`setup.py$`) predates this file existing at its current path.

Not in scope unless you want it added: exposing `reset_tare`/`send_command`/`set_parameter` as
services (library methods already exist, per the mapping skill's service-surface table) — flagging
it here since it came up during research, but treating it as a separate ask rather than folding it
into "moderate improvements."

---

## 5. Test strategy

Existing suite lives in `src/schunk_fts_library/tests/` (17 files, ~3200 lines). Split by whether
they touch a live socket/fixture (`sensor`/`send_messages`) or are pure synthetic-bytes unit
tests, checked directly against the current files:

| Needs dummy/sim or real sensor | Pure unit tests (no live connection needed) |
|---|---|
| `test_connection.py`, `test_connection_lifecycle.py` | `test_data_buffer.py` (decode logic — **critical to extend for batch decode**, per `schunk-wire-protocol` skill) |
| `test_driver.py`, `test_reconnection.py` | `test_messages.py` (Message subclass to/from bytes) |
| `test_error_handling.py`, `test_firmware.py` | `test_protocol.py` (framing) |
| `test_performance.py`, `test_thread_safety.py` | `test_streaming.py` (uses `conftest.send_messages` to fire synthetic UDP datagrams at a bound socket — no real sensor/dummy process needed, just a raw socket send) |
| `test_commands.py`, `test_parameters.py` | |

**Plan**:

- New batch-decode unit tests (449-byte payload, 16-sample unpacking, `sample_index`/
  `samples_per_packet` fields) belong in the pure-unit-test column — synthetic bytes, no dummy
  needed, run everywhere including CI without hardware. These are the tests that actually catch
  wire-format bugs (per the wire-protocol skill's "silent bugs" framing) and should be written
  first, before wiring `output_rate` through `Driver`.
- End-to-end batch-mode verification (does the sensor actually emit 500-16 packets when the
  parameter is set, does auto-reconnect survive mid-batch-stream) needs a dummy that itself emits
  500-16 packets — which means a dummy built from `main`'s updated `schunk_fts_dummy` Rust code
  (the `ros1`-visible dummy path, `/tmp/schunk_fts_dummy/debug/schunk_fts_dummy`, is whatever
  binary CI drops there; locally you'd need to build the dummy from a `main`-branch checkout or
  wherever that Rust project currently lives, since it isn't committed in this repo). Use
  `ros1-test-runner` to run these once such a dummy is available; treat their absence as "skip and
  report," not "fail."
- `catkin_make` build verification (does the workspace still build after `srv`/`msg`/
  `CMakeLists.txt` changes) is cheap and should run on every change regardless of sensor
  availability — `ros1-test-runner` covers this as step 1 before pytest.

---

## Summary / what happens after approval

Once you approve (and answer the Option A/B question in §2), implementation order would be:
1. §3 stale-config cleanup (independent, zero-risk, unblocks trustworthy `pre-commit run --all-files`).
2. §2 library-side batch decode + reconnection/source-IP hardening, with unit tests first
   (`protocol-library-porter`).
3. §2 node-side `output_rate` param, cadence/timestamp handling (`ros2-to-ros1-translator`).
4. §4 moderate improvements (can interleave, lowest risk).
5. `ros1-test-runner` build+test pass after each stage.

No code changes have been made yet beyond this plan and the `.claude/skills/`/`.claude/agents/`
scaffolding.
