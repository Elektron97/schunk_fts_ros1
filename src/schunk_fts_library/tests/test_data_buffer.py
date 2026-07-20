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
from schunk_fts_library.utility import FTDataBuffer, FTData
from threading import Thread
import pytest
import struct
import time


def _single_sample_packet(
    counter: int = 42, id_: int = 0, fx: float = 1.0
) -> bytearray:
    """Build a 29-byte-payload single-sample packet (sync + <HHB I ffffff>)."""
    payload = struct.pack(
        "<HHB I ffffff",
        counter,
        29,
        id_,
        0,  # status_bits
        fx,
        fx + 1.0,
        fx + 2.0,
        fx + 3.0,
        fx + 4.0,
        fx + 5.0,
    )
    return bytearray(b"\xFF\xFF") + payload


def _batch_packet(counter: int = 7, packet_id: int = 3) -> bytearray:
    """Build a 449-byte-payload 16-sample batch packet.

    Layout (per schunk-wire-protocol skill):
    sync(2) counter(u16) payload_len(u16)=449 packet_id(u8)
      [ status_bits(u32) fx,fy,fz,tx,ty,tz(f32 x6) ] x 16, 28 bytes each
    """
    header = bytearray(b"\xFF\xFF") + struct.pack("<HH", counter, 449)
    header += struct.pack("<B", packet_id)
    body = bytearray()
    for i in range(16):
        body += struct.pack(
            "<I ffffff",
            0xA0 + i,  # status_bits, distinct per sample
            float(i),
            float(i) + 0.1,
            float(i) + 0.2,
            float(i) + 0.3,
            float(i) + 0.4,
            float(i) + 0.5,
        )
    packet = header + body
    assert len(packet) == 2 + 2 + 2 + 449  # sync + counter + payload_len + payload
    return packet


def test_buffer_offers_putting_and_getting_data():
    buffer = FTDataBuffer()

    # Without data
    data = buffer.get()
    if not data:
        assert data is None
    else:
        assert data["id"] == 0
        assert data["status_bits"] == 0
        assert pytest.approx(data["fx"]) == 0.0
        assert pytest.approx(data["fy"]) == 0.0
        assert pytest.approx(data["fz"]) == 0.0
        assert pytest.approx(data["tx"]) == 0.0
        assert pytest.approx(data["ty"]) == 0.0
        assert pytest.approx(data["tz"]) == 0.0

    # Put + get
    data_bytes = bytearray(
        [
            0xFF,
            0xFF,  # sync (2 bytes, little-endian)
            0x2A,
            0x00,  # counter (42, 2 bytes, little-endian)
            0x1D,
            0x00,  # payload (29, 2 bytes, little-endian)
            0x00,  # id (0, 1 byte)
            0x00,
            0x00,
            0x00,
            0x00,  # status_bits (0, 4 bytes, little-endian)
            0x00,
            0x00,
            0x80,
            0x3F,  # fx (1.0, 4 bytes, IEEE 754 little-endian)
            0x00,
            0x00,
            0x00,
            0x40,  # fy (2.0, 4 bytes, little-endian)
            0x00,
            0x00,
            0x40,
            0x40,  # fz (3.0, 4 bytes, little-endian)
            0x00,
            0x00,
            0x80,
            0x40,  # tx (4.0, 4 bytes, little-endian)
            0x00,
            0x00,
            0xA0,
            0x40,  # ty (5.0, 4 bytes, little-endian)
            0x00,
            0x00,
            0xC0,
            0x40,  # tz (6.0, 4 bytes, little-endian)
        ]
    )
    buffer.put(packet=data_bytes)  # Expects bytearry
    data = FTData(
        sync=bytearray([0xFF, 0xFF]),
        counter=42,
        payload=29,
        id=0,
        status_bits=0,
        fx=1.0,
        fy=2.0,
        fz=3.0,
        tx=4.0,
        ty=5.0,
        tz=6.0,
    )
    assert buffer.get() == data


def test_buffer_knows_expected_length():
    buffer = FTDataBuffer(maxsize=3)

    # Initially, the buffer should be empty
    assert len(buffer) == 0

    # Add one packet
    buffer.put(bytearray(b"\x00" * 32))
    assert len(buffer) == 1

    # Fill it up to maxsize
    buffer.put(bytearray(b"\x00" * 32))
    buffer.put(bytearray(b"\x00" * 32))
    assert len(buffer) == 3

    # Try to overfill — buffer should drop packets, but size stays constant
    buffer.put(bytearray(b"\x00" * 32))
    assert len(buffer) == 3


def test_buffer_supports_concurrent_accesses():
    buffer = FTDataBuffer(maxsize=100)
    nr_iterations = 10_000  # keep runtime short for CI

    # Helper: create valid packet
    def make_packet(counter: int, id_: int, fx: float) -> bytearray:
        payload = struct.pack(
            "<HHB I ffffff",
            counter,  # counter
            29,  # length
            id_,  # id
            0,  # status_bits
            fx,
            fx,
            fx,
            fx,
            fx,
            fx,  # fx..tz
        )
        return bytearray(b"\xFF\xFF") + payload

    packet0 = make_packet(1, 0, 1.1)
    packet1 = make_packet(2, 1, 2.2)

    exception = None

    def writer():
        for n in range(nr_iterations):
            packet = packet0 if n % 2 == 0 else packet1
            buffer.put(packet)
            time.sleep(0.0001)  # simulate 10kHz rate

    def reader():
        nonlocal exception
        for _ in range(nr_iterations):
            data = buffer.get()
            if data is None:
                continue  # skip empty cycles
            try:
                assert isinstance(data, dict)
                assert data["sync"] == b"\xFF\xFF"
                assert data["payload"] == 29
                assert data["id"] in (0, 1)
                assert pytest.approx(data["fx"]) in (1.1, 2.2)
            except AssertionError as e:
                exception = e
                break

    writer_thread = Thread(target=writer, daemon=True)
    reader_thread = Thread(target=reader, daemon=True)

    writer_thread.start()
    reader_thread.start()

    writer_thread.join(timeout=5)
    reader_thread.join(timeout=5)

    assert not writer_thread.is_alive()
    assert not reader_thread.is_alive()

    if exception:
        raise exception


def test_decode_packet_single_sample_matches_legacy_decode():
    """29-byte payload_len must still decode identically to the pre-batch decode()."""
    packet = _single_sample_packet(counter=42, id_=0, fx=1.0)

    legacy = FTDataBuffer.decode(packet)
    samples = FTDataBuffer.decode_packet(packet)

    assert len(samples) == 1
    assert samples[0] == legacy
    assert legacy == FTData(
        sync=bytearray([0xFF, 0xFF]),
        counter=42,
        payload=29,
        id=0,
        status_bits=0,
        fx=1.0,
        fy=2.0,
        fz=3.0,
        tx=4.0,
        ty=5.0,
        tz=6.0,
    )
    # No batch-only fields on the single-sample result.
    assert "sample_index" not in samples[0]
    assert "samples_per_packet" not in samples[0]


def test_decode_packet_batch_returns_16_indexed_samples():
    """449-byte payload_len must decode into 16 FTData samples, correctly indexed."""
    packet = _batch_packet(counter=7, packet_id=3)

    samples = FTDataBuffer.decode_packet(packet)

    assert len(samples) == 16
    for i, sample in enumerate(samples):
        assert sample["counter"] == 7  # same for every sample in the packet
        assert sample["sync"] == b"\xFF\xFF"
        assert sample["payload"] == 449
        assert sample["id"] == 3  # packet_id, shared across all 16 samples
        assert sample["sample_index"] == i
        assert sample["samples_per_packet"] == 16
        assert sample["status_bits"] == 0xA0 + i
        assert pytest.approx(sample["fx"]) == float(i)
        assert pytest.approx(sample["fy"]) == float(i) + 0.1
        assert pytest.approx(sample["fz"]) == float(i) + 0.2
        assert pytest.approx(sample["tx"]) == float(i) + 0.3
        assert pytest.approx(sample["ty"]) == float(i) + 0.4
        assert pytest.approx(sample["tz"]) == float(i) + 0.5


def test_buffer_get_drains_batch_packet_one_sample_at_a_time():
    """FTDataBuffer.get() must queue overflow samples from a batch packet."""
    buffer = FTDataBuffer()
    packet = _batch_packet(counter=7, packet_id=3)

    buffer.put(packet)
    # A single put() of one 449-byte packet must yield exactly 16 get()s.
    assert len(buffer) == 1

    drained = [buffer.get() for _ in range(16)]
    assert len(drained) == 16
    for i, sample in enumerate(drained):
        assert sample["sample_index"] == i
        assert sample["samples_per_packet"] == 16

    assert len(buffer) == 0


def test_buffer_get_at_default_rate_yields_one_sample_per_packet():
    """Regression guard: single-sample packets must not get queued as pending."""
    buffer = FTDataBuffer()
    buffer.put(_single_sample_packet(counter=1))
    buffer.put(_single_sample_packet(counter=2))

    first = buffer.get()
    second = buffer.get()

    assert first["counter"] == 1
    assert second["counter"] == 2
    assert len(buffer._pending_samples) == 0


def test_buffer_tracks_dropped_packets_when_full():
    buffer = FTDataBuffer(maxsize=1)
    assert buffer.dropped_packet_count == 0

    buffer.put(_single_sample_packet(counter=1))
    buffer.put(_single_sample_packet(counter=2))  # queue full, should be dropped

    assert buffer.dropped_packet_count == 1


def test_buffer_clear_empties_queue_and_pending_samples():
    buffer = FTDataBuffer()
    buffer.put(_batch_packet(counter=7, packet_id=3))
    buffer.get()  # decode packet, populate _pending_samples with 15 remaining

    assert len(buffer) == 15

    buffer.clear()

    assert len(buffer) == 0
    assert buffer.get() is None or buffer.get()["counter"] == 0
