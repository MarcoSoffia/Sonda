import pytest
from chunker import Chunker


def test_chunker_valid_default_size():
    ch = Chunker(b"hello")

    assert ch.file_bytes == b"hello"
    assert ch.chunk_size == 5
    assert ch.chunk() == [b"hello"]

def test_chunker_invalid_file_format():
    with pytest.raises(TypeError, match="File must be non-empty bytes"):
        Chunker("Test", 12)
    
def test_chunker_negative_size():
    with pytest.raises(TypeError, match="Invalid chunk size"):
        Chunker(b"hello world", -1)

def test_chunker_empty_size():
    with pytest.raises(TypeError, match="Invalid chunk size"):
        Chunker(b"hello world", 0)

def test_chunker_floating_size():
    with pytest.raises(TypeError, match="Invalid chunk size"):
        Chunker(b"hello world", 1.5)