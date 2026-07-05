import pytest
from codec import Codec
from frame import DataFrame, HashFrame


def test_serialize_hash_frame():
    file_bytes = b"abc"
    frame = HashFrame(file_bytes)
    result = Codec.serialize(frame)

    assert result.startswith("0")
    assert result[1:] == frame.digest


def test_serialize_data_frame():
    payload = b"hello"
    frame = DataFrame(payload)
    result = Codec.serialize(frame)

    assert result.startswith("1")
    assert result[1:] == "".join(f"{x:03d}" for x in payload)


def test_deserialize_hash_frame():
    file_bytes = b"abc"
    frame = HashFrame(file_bytes)
    serialized = Codec.serialize(frame)
    result = Codec.deserialize(serialized)

    assert isinstance(result, HashFrame)
    assert result.digest == frame.digest


def test_deserialize_data_frame():
    payload = b"hello"
    frame = DataFrame(payload)
    serialized = Codec.serialize(frame)
    result = Codec.deserialize(serialized)

    assert isinstance(result, DataFrame)
    assert result.payload == payload
