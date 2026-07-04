import pytest
from hashlib import sha256
from frame import Frame, DataFrame, HashFrame


class DummyFrame(Frame):
    def serialize(self) -> str:
        return ""


def test_frame_is_abstract():
    with pytest.raises(TypeError):
        Frame(Frame.CODE_DATA)


def test_invalid_frame_type():
    with pytest.raises(TypeError):
        DummyFrame(0x99)

def test_hash_frame_valid():
    file_bytes = b"abc"
    frame = HashFrame(file_bytes)

    assert frame.type == Frame.CODE_HASH
    assert frame.file == file_bytes
    assert frame.serialize() == sha256(file_bytes).hexdigest()