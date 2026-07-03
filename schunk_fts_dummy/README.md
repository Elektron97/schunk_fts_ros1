# SCHUNK Force-Torque Sensor Dummy

Rust-based sensor simulator for testing without hardware.

## Quick Start

### Install Rust
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### Run
```bash
cd schunk_fts_dummy
cargo run
```

Expected output:
```
SCHUNK Force-Torque Sensor Dummy
Listening on:
  TCP: 127.0.0.1:8082 (commands)
  UDP: 127.0.0.1:52964 -> client:54843 (data stream)
```

## Differences from Real Sensor

| Feature | Real Sensor | Dummy |
|---------|-------------|-------|
| Port | 82 (requires root) | 8082 |
| IP | 192.168.0.100 | 127.0.0.1 |
| Data | Real measurements | Random ± noise |
| Commands | Affects sensor | Simulated response only |
| UDP output rate | 1000, 500, 250, 100, 8000 Hz | 1000, 500, 250, 100, 8000 Hz |

The dummy implements `output_rate_udp_ethernet` at parameter `0x1020/0`. Enum values `0`, `1`, `2`, `3`, and `10` select 1000, 500, 250, 100, and 8000 Hz respectively. The 8000 Hz mode sends UDP packets at 500 Hz with 16 sequential datapoints per packet.
