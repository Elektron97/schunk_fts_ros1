# CVE-Scan Report – schunk_force_torque_sensor

**Scan-Zeitpunkt:** 2026-07-21T08:20:03Z
**Repository:** SCHUNK-SE-Co-KG/schunk_force_torque_sensor
**Abhängigkeiten geprüft:** 71
**Schwachstellen gefunden:** 2

> 2 Schwachstelle(n) gefunden!

## Zusammenfassung nach Ökosystem

| Ökosystem | Abhängigkeiten | Schwachstellen |
|-----------|---------------|----------------|
| PyPI (Python) | 22 | 2 |
| crates.io (Rust) | 40 | 0 |
| ROS 2 | 9 | 0 |
| **Gesamt** | **71** | **2** |

## Geprüfte Abhängigkeiten

### Python (PyPI)

| Paket | Version | Quelle |
|-------|---------|--------|
| requests | 2.34.2 | schunk_fts_library/setup.py |
| psutil | 7.2.2 | schunk_fts_library/setup.py |
| black | 26.5.1 | schunk_fts_driver/setup.py |
| certifi | 2026.6.17 | schunk_fts_driver/setup.py |
| charset-normalizer | 3.4.7 | schunk_fts_driver/setup.py |
| click | 8.4.2 | schunk_fts_driver/setup.py |
| exceptiongroup | 1.3.1 | schunk_fts_driver/setup.py |
| idna | 3.18 | schunk_fts_driver/setup.py |
| iniconfig | 2.3.0 | schunk_fts_driver/setup.py |
| lark | 1.3.1 | schunk_fts_driver/setup.py |
| mypy_extensions | 1.1.0 | schunk_fts_driver/setup.py |
| numpy | 2.2.6 | schunk_fts_driver/setup.py |
| packaging | 26.2 | schunk_fts_driver/setup.py |
| pathspec | 1.1.1 | schunk_fts_driver/setup.py |
| platformdirs | 4.10.0 | schunk_fts_driver/setup.py |
| pluggy | 1.6.0 | schunk_fts_driver/setup.py |
| pytest | 9.0.2 | schunk_fts_driver/setup.py |
| pytest-repeat | 0.9.4 | schunk_fts_driver/setup.py |
| PyYAML | 6.0.3 | schunk_fts_driver/setup.py |
| tomli | 2.4.1 | schunk_fts_driver/setup.py |
| typing_extensions | 4.15.0 | schunk_fts_driver/setup.py |
| urllib3 | 2.7.0 | schunk_fts_driver/setup.py |

### Rust (crates.io)

| Crate | Version | Quelle |
|-------|---------|--------|
| addr2line | 0.24.2 | schunk_fts_dummy/Cargo.lock |
| adler2 | 2.0.0 | schunk_fts_dummy/Cargo.lock |
| autocfg | 1.4.0 | schunk_fts_dummy/Cargo.lock |
| backtrace | 0.3.75 | schunk_fts_dummy/Cargo.lock |
| bitflags | 2.9.1 | schunk_fts_dummy/Cargo.lock |
| bytes | 1.11.1 | schunk_fts_dummy/Cargo.lock |
| cfg-if | 1.0.0 | schunk_fts_dummy/Cargo.lock |
| gimli | 0.31.1 | schunk_fts_dummy/Cargo.lock |
| libc | 0.2.172 | schunk_fts_dummy/Cargo.lock |
| lock_api | 0.4.12 | schunk_fts_dummy/Cargo.lock |
| memchr | 2.7.4 | schunk_fts_dummy/Cargo.lock |
| miniz_oxide | 0.8.8 | schunk_fts_dummy/Cargo.lock |
| mio | 1.0.3 | schunk_fts_dummy/Cargo.lock |
| object | 0.36.7 | schunk_fts_dummy/Cargo.lock |
| parking_lot | 0.12.3 | schunk_fts_dummy/Cargo.lock |
| parking_lot_core | 0.9.10 | schunk_fts_dummy/Cargo.lock |
| pin-project-lite | 0.2.16 | schunk_fts_dummy/Cargo.lock |
| proc-macro2 | 1.0.95 | schunk_fts_dummy/Cargo.lock |
| quote | 1.0.40 | schunk_fts_dummy/Cargo.lock |
| redox_syscall | 0.5.12 | schunk_fts_dummy/Cargo.lock |
| rustc-demangle | 0.1.24 | schunk_fts_dummy/Cargo.lock |
| scopeguard | 1.2.0 | schunk_fts_dummy/Cargo.lock |
| signal-hook-registry | 1.4.5 | schunk_fts_dummy/Cargo.lock |
| smallvec | 1.15.0 | schunk_fts_dummy/Cargo.lock |
| socket2 | 0.5.9 | schunk_fts_dummy/Cargo.lock |
| syn | 2.0.101 | schunk_fts_dummy/Cargo.lock |
| tokio | 1.45.0 | schunk_fts_dummy/Cargo.lock |
| tokio-macros | 2.5.0 | schunk_fts_dummy/Cargo.lock |
| unicode-ident | 1.0.18 | schunk_fts_dummy/Cargo.lock |
| wasi | 0.11.0+wasi-snapshot-preview1 | schunk_fts_dummy/Cargo.lock |
| windows-sys | 0.52.0 | schunk_fts_dummy/Cargo.lock |
| windows-targets | 0.52.6 | schunk_fts_dummy/Cargo.lock |
| windows_aarch64_gnullvm | 0.52.6 | schunk_fts_dummy/Cargo.lock |
| windows_aarch64_msvc | 0.52.6 | schunk_fts_dummy/Cargo.lock |
| windows_i686_gnu | 0.52.6 | schunk_fts_dummy/Cargo.lock |
| windows_i686_gnullvm | 0.52.6 | schunk_fts_dummy/Cargo.lock |
| windows_i686_msvc | 0.52.6 | schunk_fts_dummy/Cargo.lock |
| windows_x86_64_gnu | 0.52.6 | schunk_fts_dummy/Cargo.lock |
| windows_x86_64_gnullvm | 0.52.6 | schunk_fts_dummy/Cargo.lock |
| windows_x86_64_msvc | 0.52.6 | schunk_fts_dummy/Cargo.lock |

### ROS 2

| Paket | Ökosystem | Quelle | Upstream |
|-------|-----------|--------|----------|
| rclpy | ROS | schunk_fts_driver/package.xml | [ros2/rclpy](https://github.com/ros2/rclpy) |
| launch | ROS | schunk_fts_driver/package.xml | [ros2/launch](https://github.com/ros2/launch) |
| launch_ros | ROS | schunk_fts_driver/package.xml | [ros2/launch_ros](https://github.com/ros2/launch_ros) |
| geometry_msgs | ROS | schunk_fts_driver/package.xml | [ros2/common_interfaces](https://github.com/ros2/common_interfaces) |
| std_srvs | ROS | schunk_fts_driver/package.xml | [ros2/common_interfaces](https://github.com/ros2/common_interfaces) |
| sensor_msgs | ROS | schunk_fts_driver/package.xml | [ros2/common_interfaces](https://github.com/ros2/common_interfaces) |
| diagnostic_msgs | ROS | schunk_fts_driver/package.xml | [ros2/common_interfaces](https://github.com/ros2/common_interfaces) |
| example_interfaces | ROS | schunk_fts_driver/package.xml | [ros2/example_interfaces](https://github.com/ros2/example_interfaces) |
| std_msgs | ROS | schunk_fts_interfaces/package.xml | [ros2/common_interfaces](https://github.com/ros2/common_interfaces) |

## Gefundene Schwachstellen

### GHSA-6w46-j5rx-g56g

- **Paket:** PyPI:pytest@9.0.2
- **CVSS-Score:** 6.8
- **Schweregrad:** CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L
- **CVE:** CVE-2025-71176
- **Beschreibung:** pytest has vulnerable tmpdir handling
- **Fix-Version:** 9.0.3
- **Referenzen:**
  - https://nvd.nist.gov/vuln/detail/CVE-2025-71176
  - https://github.com/pytest-dev/pytest/issues/13669
  - https://github.com/pytest-dev/pytest/pull/14343
  - https://github.com/pytest-dev/pytest/commit/95d8423bd24992deea5b9df32555fa1741679e2c
  - https://github.com/pytest-dev/pytes

### PYSEC-2026-1845

- **Paket:** PyPI:pytest@9.0.2
- **CVSS-Score:** 6.8
- **Schweregrad:** CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L
- **CVE:** CVE-2025-71176
- **Beschreibung:** pytest has vulnerable tmpdir handling
- **Fix-Version:** 9.0.3
- **Referenzen:**
  - https://nvd.nist.gov/vuln/detail/CVE-2025-71176
  - https://github.com/pytest-dev/pytest/issues/13669
  - https://github.com/pytest-dev/pytest/pull/14343
  - https://github.com/pytest-dev/pytest/commit/95d8423bd24992deea5b9df32555fa1741679e2c
  - https://github.com/pytest-dev/pytes

---
*Automatisch generiert von `security/cve_scanner.py` via [OSV.dev](https://osv.dev) und GitHub Advisory Database.*
