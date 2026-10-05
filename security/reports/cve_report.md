# CVE-Scan Report – schunk_force_torque_sensor

**Scan-Zeitpunkt:** 2026-10-05T16:46:53Z
**Repository:** SCHUNK-SE-Co-KG/schunk_force_torque_sensor
**Abhängigkeiten geprüft:** 71
**Schwachstellen gefunden:** 8

> 8 Schwachstelle(n) gefunden!

## Zusammenfassung nach Ökosystem

| Ökosystem | Abhängigkeiten | Schwachstellen |
|-----------|---------------|----------------|
| PyPI (Python) | 22 | 8 |
| crates.io (Rust) | 40 | 0 |
| ROS 2 | 9 | 0 |
| **Gesamt** | **71** | **8** |

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

### GHSA-8988-9cw3-xx77

- **Paket:** PyPI:urllib3@2.7.0
- **CVSS-Score:** 7.6 (KRITISCH)
- **Schweregrad:** CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N
- **CVE:** CVE-2026-97687
- **Beschreibung:** urllib3: HTTPS proxy TLS configuration may be ignored or overridden
- **Fix-Version:** 2.8.0
- **Referenzen:**
  - https://github.com/urllib3/urllib3/security/advisories/GHSA-8988-9cw3-xx77
  - https://nvd.nist.gov/vuln/detail/CVE-2026-97687
  - https://github.com/urllib3/urllib3/pull/5093
  - https://github.com/urllib3/urllib3/commit/07408cec79d1856d81bb42c74a904a24fdb9e465
  - https://github.com/urllib3/urllib3/commit/b6447295fff7b38fdffc67e0df9712d60cef3cc3

### GHSA-gh4c-6fx4-qh6g

- **Paket:** PyPI:urllib3@2.7.0
- **CVSS-Score:** 6.9
- **Schweregrad:** CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N
- **CVE:** CVE-2026-97688
- **Beschreibung:** urllib3: Chunked Deflate streaming can enter an infinite loop
- **Fix-Version:** 2.8.0
- **Referenzen:**
  - https://github.com/urllib3/urllib3/security/advisories/GHSA-gh4c-6fx4-qh6g
  - https://nvd.nist.gov/vuln/detail/CVE-2026-97688
  - https://github.com/urllib3/urllib3/commit/ea2ad7b21a80da3632f80016526a18864586077f
  - https://github.com/urllib3/urllib3
  - https://github.com/urllib3/urllib3/releases/tag/2.8.0

### GHSA-vxq7-64xx-v4gw

- **Paket:** PyPI:urllib3@2.7.0
- **CVSS-Score:** 8.9 (KRITISCH)
- **Schweregrad:** CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H
- **CVE:** CVE-2026-97689
- **Beschreibung:** urllib3: HTTPResponse.stream()/read_chunked() buffers an unbounded chunk-size line into memory
- **Fix-Version:** 2.8.0
- **Referenzen:**
  - https://github.com/urllib3/urllib3/security/advisories/GHSA-vxq7-64xx-v4gw
  - https://nvd.nist.gov/vuln/detail/CVE-2026-97689
  - https://github.com/urllib3/urllib3/commit/cd770b059b543be29298ea5c52afb0b1b090f5ed
  - https://github.com/urllib3/urllib3
  - https://github.com/urllib3/urllib3/releases/tag/2.8.0

### PYSEC-2026-4175

- **Paket:** PyPI:urllib3@2.7.0
- **CVSS-Score:** 7.6 (KRITISCH)
- **Schweregrad:** CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N
- **CVE:** CVE-2026-97687
- **Beschreibung:** urllib3: HTTPS proxy TLS configuration may be ignored or overridden
- **Fix-Version:** 2.8.0
- **Referenzen:**
  - https://github.com/urllib3/urllib3/security/advisories/GHSA-8988-9cw3-xx77
  - https://nvd.nist.gov/vuln/detail/CVE-2026-97687
  - https://github.com/urllib3/urllib3/pull/5093
  - https://github.com/urllib3/urllib3/commit/07408cec79d1856d81bb42c74a904a24fdb9e465
  - https://github.com/urllib3/urllib3/commit/b6447295fff7b38fdffc67e0df9712d60cef3cc3

### PYSEC-2026-4176

- **Paket:** PyPI:urllib3@2.7.0
- **CVSS-Score:** 6.9
- **Schweregrad:** CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N
- **CVE:** CVE-2026-97688
- **Beschreibung:** urllib3: Chunked Deflate streaming can enter an infinite loop
- **Fix-Version:** 2.8.0
- **Referenzen:**
  - https://github.com/urllib3/urllib3/security/advisories/GHSA-gh4c-6fx4-qh6g
  - https://nvd.nist.gov/vuln/detail/CVE-2026-97688
  - https://github.com/urllib3/urllib3/commit/ea2ad7b21a80da3632f80016526a18864586077f
  - https://github.com/urllib3/urllib3
  - https://github.com/urllib3/urllib3/releases/tag/2.8.0

### PYSEC-2026-4177

- **Paket:** PyPI:urllib3@2.7.0
- **CVSS-Score:** 8.9 (KRITISCH)
- **Schweregrad:** CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H
- **CVE:** CVE-2026-97689
- **Beschreibung:** urllib3: HTTPResponse.stream()/read_chunked() buffers an unbounded chunk-size line into memory
- **Fix-Version:** 2.8.0
- **Referenzen:**
  - https://github.com/urllib3/urllib3/security/advisories/GHSA-vxq7-64xx-v4gw
  - https://nvd.nist.gov/vuln/detail/CVE-2026-97689
  - https://github.com/urllib3/urllib3/commit/cd770b059b543be29298ea5c52afb0b1b090f5ed
  - https://github.com/urllib3/urllib3
  - https://github.com/urllib3/urllib3/releases/tag/2.8.0

---
*Automatisch generiert von `security/cve_scanner.py` via [OSV.dev](https://osv.dev) und GitHub Advisory Database.*
