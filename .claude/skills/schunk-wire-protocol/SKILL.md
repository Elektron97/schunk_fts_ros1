---
name: schunk-wire-protocol
description: Reference for the SCHUNK FTS TCP command/UDP streaming wire protocol as implemented in src/schunk_fts_library/utility.py (this fork) and schunk_fts_library/schunk_fts_library/utility.py on the ROS2 main branch (8kHz batch mode). Load this before touching any encode/decode logic, adding output-rate support, or porting protocol changes between branches — wire-format bugs are silent (wrong floats, not crashes).
---

# SCHUNK FTS wire protocol

Two sockets, two framings:

- **TCP** (`Connection`, default port `82`) — request/response commands and parameter
  get/set. Persistent, reference-counted open/close via a `persistent` `Event`.
- **UDP** (`Stream`, default port `54843`) — one-way sensor → host data feed, non-blocking
  reads via `recvfrom`.

## TCP command/response framing (`Message` subclasses)

Every request and response shares the same envelope, all little-endian:

```
sync (2 bytes, fixed "ffff")  counter (uint16)  payload_len (uint16)  payload (payload_len bytes)
```

`Message.to_bytes()` builds this generically from a subclass's `__fields__` list (each field is a
hex string, byte-reversed for little-endian, concatenated into `payload`). `from_bytes()` on each
subclass is hand-written per message type — there is no generic decoder, so a new field on a
request class needs a matching hand-written offset read in the paired response class.

Message classes (identical on both branches):

| Class | `__fields__` | Purpose |
|---|---|---|
| `GetParameterRequest` / `Response` | `command_id, param_index, param_subindex` / `+ param_value` | read a parameter (`command_id = "f0"`) |
| `SetParameterRequest` / `Response` | `command_id, param_index, param_subindex, param_value` / `- param_value` | write a parameter (`command_id = "f1"`) |
| `CommandRequest` / `Response` | `command_id` / `command_id, error_code` | fire a zero-argument command |
| `CommandWithParameterRequest` | `command_id, parameter` | fire a command with one uint8 parameter byte |

`error_code == "00"` means success on every response type that carries one.

## Command hex IDs (via `Driver.run_command` / `CommandWithParameterRequest`)

| ID | Meaning | Notes |
|---|---|---|
| `12` | `tare` | zero the sensor |
| `13` | `tare_reset` | remove tare offset |
| `30` | `select_tool_setting` | parameter byte = tool index, valid range 0-3 |
| `31` | `select_noise_filter` | parameter byte = filter number, valid range 0-4 (rolling-average factors 1/2/4/8/16) |
| `40` | start UDP stream | sent at the end of `streaming_on()` |
| `41` | stop UDP stream | sent at the start of `streaming_off()` |
| `f0` | get parameter | see `GetParameterRequest` |
| `f1` | set parameter | see `SetParameterRequest` |

Product identity is read via `get_parameter` at index `0001`: subindex `00` = product name
(ASCII, hex-encoded, null-stripped), subindex `03` = product ID.

## UDP data decode — where the branches diverge

Both branches decode via `FTDataBuffer`, but **this fork (`ros1` branch,
`src/schunk_fts_library/utility.py`) only implements the single-sample format.** The ROS2
`main` branch additionally implements a 16-sample batch format for 8kHz streaming. Do not
assume batch support exists here — it was stripped during the ROS1 port along with the
`output_rate` parameter that selects it (see `ros1-vs-ros2-mapping` skill).

### Single-sample format (both branches, `payload_len == 29`)

```
sync(2) counter(u16) payload_len(u16) id(u8) status_bits(u32) fx,fy,fz,tx,ty,tz(f32 x6)
```

- **ros1 branch**: `FTDataBuffer.decode(data)` unconditionally unpacks
  `struct.unpack("<HHB I ffffff", data[2:])` (skip the 2-byte sync, then counter+payload_len+id+
  status+6 floats) and returns one `FTData` dict. No `payload_len` branch — it assumes every
  packet is a single sample.
- **main branch**: the same 29-byte layout is one branch of `FTDataBuffer.decode_packet(data)`,
  which switches on `payload_len` (unpacked separately first via `struct.unpack("<HH", data[2:6])`)
  and returns `[FTData]` — a **list**, even for the single-sample case, because `decode_packet`
  is also used by the batch path. `FTDataBuffer.decode()` is now just `decode_packet(data)[0]`,
  kept only as a compatibility shim.

### Batch format (main branch only, `payload_len == 449`)

449 bytes = 1 packet ID byte + 16 samples × 28 bytes, at the `500-16` output rate (500 packets/s ×
16 samples/packet = 8000 samples/s effective):

```
sync(2) counter(u16) payload_len(u16) packet_id(u8)
  [ status_bits(u32) fx,fy,fz,tx,ty,tz(f32 x6) ] × 16   (28 bytes each, back-to-back)
```

`decode_packet` reads `packet_id = data[6]`, then loops 16 times over `struct.unpack_from("<I
ffffff", data, offset)` starting at `offset = 7`, incrementing by `struct.calcsize("<I ffffff")`
(28 bytes) each time. Each resulting `FTData` additionally sets `sample_index` (0-15) and
`samples_per_packet=16` — fields that don't exist at all on the ros1-branch `FTData` TypedDict.
`counter` and `sync` are the **same** for all 16 samples in a packet (it's one UDP datagram); only
`sample_index` distinguishes them, and per-sample timestamps must be back-computed from it (the
sensor only timestamps the packet, not each sample — see `_calculate_sample_timestamp_ns` in
`schunk_fts_driver/schunk_fts_driver/driver.py` on main for the ROS2 reconstruction, which is
ROS2-plumbing and not something to port as-is, but the math it encodes is protocol-relevant).

There's a second, leaner decode path on main purely for batch consumption:
`FTDataBuffer.decode_sample_batch(data) -> list[FTSample]`, where `FTSample` is a plain tuple
`(counter, packet_id, sample_index, samples_per_packet, status_bits, fx, fy, fz, tx, ty, tz)`
rather than a dict — used by `Driver.sample_batch()` for lower per-sample overhead than
`FTData` dicts. It has its own independent `payload_len` branch (449 / 29 / fallback) — **any
change to the 449-byte layout must be mirrored in both `decode_packet` and
`decode_sample_batch`**, they are not implemented in terms of each other.

### Fallback branch (main only)

If `payload_len` is neither 29 nor 449, both `decode_packet` and `decode_sample_batch` fall back
to unpacking the whole `data[2:]` as `<HHB I ffffff` (i.e. treat it as single-sample framing
without trusting the separately-read `payload_len`). This exists for forward compatibility /
malformed-length tolerance; the ros1-branch `decode()` has no equivalent fallback since it never
reads `payload_len` at all.

## Consuming code paths

- ros1 branch: `FTDataBuffer.put()/.get()` (simple `Queue`), consumed by `Driver.sample()` only.
  No `sample_batch()` method exists on the ros1 `Driver`.
- main branch: `FTDataBuffer` also holds a `_pending_samples` deque — `get()` decodes a packet
  into potentially multiple `FTData`s (via `decode_packet`) and queues the overflow, so **even
  single-sample callers get correct behavior if a batch packet somehow arrives** while in
  single-sample mode. `get_sample_batch()` is the dedicated batch consumer for `sample_batch()`.
