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
from schunk_fts_library.utility import Stream
import time
from threading import Thread
import struct
import pytest
from socket import socket as Socket
import socket


def test_stream_has_expected_fields(unused_udp_port):
    with Stream(port=unused_udp_port) as stream:
        assert stream.port == unused_udp_port
        assert stream.socket is not None


def test_stream_opens_with_valid_ports(unused_udp_port_factory):
    valid_ports = [unused_udp_port_factory() for _ in range(3)]
    for port in valid_ports:
        with Stream(port=port) as stream:
            assert stream.is_open(), port


def test_stream_rejects_invalid_ports():
    invalid_ports = [0, -1, 80, 1023, 65535 + 1]
    for port in invalid_ports:
        with Stream(port=port) as stream:
            assert not stream.is_open()


def test_stream_closes_socket_on_exit(unused_udp_port):
    stream = Stream(port=unused_udp_port)
    with stream:
        pass
    assert stream.socket.fileno() == -1  # means closed
    assert not stream.is_open()

    # Repeated closing
    for _ in range(3):
        with stream:
            pass


def test_stream_creates_new_socket_when_reset(unused_udp_port):
    stream = Stream(port=unused_udp_port)
    before = stream.socket
    stream._reset_socket()
    after = stream.socket
    assert after != before


def test_stream_can_be_reused(unused_udp_port):
    stream = Stream(port=unused_udp_port)
    for _ in range(5):
        with stream:
            assert stream.is_open()


def test_stream_supports_reading_data(send_messages, unused_udp_port):
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

    # Build binary packet (matches FTDataBuffer.decode)
    msg = bytearray(data["sync"]) + struct.pack(
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

    stream = Stream(port=unused_udp_port)
    assert stream.read() == list()

    # Succeeds when open.
    # Make sure to send data after we bind to the port to not miss it.
    with stream:
        sender = send_messages(unused_udp_port, [msg])
        time.sleep(0.1)
        result = stream.read()
        sender.join(timeout=1.0)
        assert not sender.is_alive()

        # Verify raw bytes match what was sent
        assert isinstance(result, list)
        assert result == [msg]


def test_stream_filters_packets_by_source_host(unused_udp_port):
    accepted_msg = b"accepted"
    ignored_msg = b"ignored"

    def send_from(source_host: str, msg: bytes) -> None:
        try:
            with Socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
                sender.bind((source_host, 0))
                sender.sendto(msg, ("127.0.0.1", unused_udp_port))
        except OSError as e:
            pytest.skip(f"Cannot bind UDP sender to {source_host}: {e}")

    with Stream(port=unused_udp_port, source_host="127.0.0.1") as stream:
        send_from("127.0.0.2", ignored_msg)
        send_from("127.0.0.1", accepted_msg)
        time.sleep(0.1)

        assert stream.read() == [accepted_msg]
        assert stream.accepted_packet_count == 1
        assert stream.ignored_packet_count == 1
        assert stream.source_addresses == {"127.0.0.1", "127.0.0.2"}


def test_stream_returns_immediately_without_data(unused_udp_port):
    with Stream(port=unused_udp_port) as stream:
        start = time.perf_counter()
        assert stream.read() == list()
        stop = time.perf_counter()
        elapsed = (stop - start) * 1000  # ms
        assert elapsed < 1.0


def test_stream_doesnt_deadlock_for_concurrent_is_open_calls(unused_udp_port):
    stream = Stream(port=unused_udp_port)
    nr_iterations = 100

    def check():
        for n in range(nr_iterations):
            assert not stream.is_open()

    threads = []
    for i in range(10):
        thread = Thread(target=check, daemon=True)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
        assert not thread.is_alive()
