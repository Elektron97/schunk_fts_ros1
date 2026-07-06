# Copyright 2025 SCHUNK SE & Co. KG
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.
# --------------------------------------------------------------------------------
from schunk_fts_library.driver import Driver
from schunk_fts_library.utility import Connection
import time
import pytest
import struct


@pytest.mark.parametrize(
    ("output_rate_hz", "expected_enum"),
    [
        (1000, "00"),
        (500, "01"),
        (250, "02"),
        (100, "03"),
        (8000, "0a"),
    ],
)
def test_driver_accepts_supported_output_rates(output_rate_hz, expected_enum):
    driver = Driver(output_rate_hz=output_rate_hz)

    assert driver.output_rate_hz == output_rate_hz
    assert driver.output_rate_parameter_value == expected_enum


@pytest.mark.parametrize("output_rate_hz", [0, 10, 499, 999, 2000, 16000])
def test_driver_rejects_unsupported_output_rates(output_rate_hz):
    with pytest.raises(ValueError, match="Unsupported output_rate_hz"):
        Driver(output_rate_hz=output_rate_hz)


def test_driver_configures_output_rate_parameter(monkeypatch):
    driver = Driver(output_rate_hz=8000)
    calls = []

    class Response:
        error_code = "00"

    def set_parameter(value: str, index: str, subindex: str = "00"):
        calls.append((value, index, subindex))
        return Response()

    monkeypatch.setattr(driver, "set_parameter", set_parameter)

    assert driver._configure_output_rate()
    assert calls == [("0a", "1020", "00")]


def test_driver_filters_udp_source_by_default_host():
    driver = Driver(host="10.49.60.117")

    assert driver.streaming_source_host == "10.49.60.117"
    assert driver.stream.source_ip == "10.49.60.117"


def test_driver_supports_explicit_udp_source_host():
    driver = Driver(host="10.49.60.117", streaming_source_host="127.0.0.1")

    assert driver.streaming_source_host == "127.0.0.1"
    assert driver.stream.source_ip == "127.0.0.1"


def test_driver_initializes_as_expected():

    # Default initialization
    driver = Driver()
    assert isinstance(driver.connection, Connection)
    assert driver.connection.host == "192.168.0.100"
    assert driver.connection.port == 82
    assert not driver.connection.is_open

    # With arguments
    host = "some-arbitrary string $\n#^^"
    port = -12345

    driver = Driver(host=host, port=port)
    assert driver.connection.host == host
    assert driver.connection.port == port


def test_driver_offers_streaming(sensor):
    HOST, PORT = sensor
    driver = Driver(host=HOST, port=PORT)
    assert not driver.is_streaming

    try:
        for run in range(3):
            assert not driver.stream.is_open()
            assert driver.streaming_on(), f"run: {run}"
            assert driver.is_streaming
            assert driver.stream.is_open()

            driver.streaming_off()
            assert not driver.is_streaming
            assert not driver.stream.is_open()
    finally:
        driver.streaming_off()
        time.sleep(0.1)


def test_driver_uses_same_stream_for_multiple_on_calls(sensor):
    HOST, PORT = sensor
    driver = Driver(host=HOST, port=PORT)
    try:
        driver.streaming_on()
        before = driver.stream_update_thread
        for _ in range(3):
            assert driver.streaming_on()
            after = driver.stream_update_thread
        assert after == before
    finally:
        driver.streaming_off()
        time.sleep(0.1)


def test_driver_survives_multiple_streaming_off_calls():
    driver = Driver()
    for _ in range(3):
        driver.streaming_off()
    assert not driver.is_streaming


def test_driver_runs_update_thread_when_streaming(sensor):
    HOST, PORT = sensor
    driver = Driver(host=HOST, port=PORT)
    assert not driver.stream_update_thread.is_alive()

    try:
        for _ in range(3):
            driver.streaming_on()
            assert driver.stream_update_thread.is_alive()
            driver.streaming_off()
            assert not driver.stream_update_thread.is_alive()
            time.sleep(0.01)
    finally:
        driver.streaming_off()
        time.sleep(0.1)


def test_driver_timeouts_when_streaming_fails():
    driver = Driver(streaming_port=-1)
    assert not driver.streaming_on()

    invalid_timeouts = [-1, -500.0, 0, 0.0, "15.0", ""]
    for timeout in invalid_timeouts:
        assert not driver.streaming_on(timeout_sec=timeout)


def test_driver_supports_sampling_force_torque_data(sensor, send_messages):
    HOST, PORT = sensor
    test_port = 8001
    driver = Driver(
        host=HOST,
        port=PORT,
        streaming_port=test_port,
        streaming_source_host="127.0.0.1",
    )

    # Not streaming
    assert driver.sample() is None

    # Stream a specific data point and check
    # that we sample that.
    assert driver.streaming_on()
    data = {
        "sync": b"\xFF\xFF",
        "counter": 42,
        "length": 29,
        "id": 1,
        "status_bits": 0x00000000,
        "fx": 1.0,
        "fy": 2.1,
        "fz": 3.3,
        "tx": 0.04,
        "ty": -17.358,
        "tz": 23.001,
    }

    # Build binary packet manually
    packet = bytearray(data["sync"]) + struct.pack(
        "<HHB I ffffff",
        data["counter"],
        data["length"],
        data["id"],
        data["status_bits"],
        data["fx"],
        data["fy"],
        data["fz"],
        data["tx"],
        data["ty"],
        data["tz"],
    )

    send_messages(test_port, [packet])
    time.sleep(0.1)  # allow driver to read from socket

    try:
        result = driver.sample()
        assert result is not None
        assert result["id"] == data["id"]
        assert result["status_bits"] == data["status_bits"]
        assert pytest.approx(result["fx"]) == data["fx"]
        assert pytest.approx(result["fy"]) == data["fy"]
        assert pytest.approx(result["fz"]) == data["fz"]
        assert pytest.approx(result["tx"]) == data["tx"]
        assert pytest.approx(result["ty"]) == data["ty"]
        assert pytest.approx(result["tz"]) == data["tz"]
    finally:
        driver.streaming_off()
        time.sleep(0.1)


def test_driver_supports_sampling_at_different_rates(sensor):
    HOST, PORT = sensor
    if (HOST, PORT) != ("127.0.0.1", 8082):
        pytest.skip("Output-rate switching test runs against the dummy sensor only.")

    for rate in [1000, 500, 250, 100, 8000]:
        driver = Driver(host=HOST, port=PORT, output_rate_hz=rate)
        try:
            assert driver.streaming_on(timeout_sec=1.0)
            deadline = time.time() + 1.0
            sample = None
            while time.time() < deadline:
                sample = driver.sample()
                if sample is None:
                    continue
                if rate != 8000 or sample.get("samples_per_packet") == 16:
                    break

            assert sample is not None, f"No sample received at {rate} Hz"
            if rate == 8000:
                assert sample["samples_per_packet"] == 16
            else:
                assert sample.get("samples_per_packet", 1) == 1
        finally:
            driver.streaming_off()
            time.sleep(0.1)
