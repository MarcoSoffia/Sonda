import pytest
from frame import Frame, DataFrame, HashFrame


class DummyFrame(Frame):
    def serialize(self) -> str:
        return ""


def test_invalid_frame_type():
    with pytest.raises(TypeError, match="Invalid frame type"):
        DummyFrame(0x99)


def test_hash_frame_valid():
    file_bytes = b"abc"
    frame = HashFrame(file_bytes)

    assert frame.type == Frame.CODE_HASH
    assert frame.file == file_bytes


def test_hash_empty_bytes_invalid():
    with pytest.raises(TypeError, match="File must be non-empty bytes"):
        HashFrame(b"")


def test_hash_string_invalid():
    with pytest.raises(TypeError, match="File must be non-empty bytes"):
        HashFrame("AAAA")
