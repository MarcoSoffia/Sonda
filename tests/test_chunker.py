import pytest
from chunker import Chunker

def test_chunker_valid_default_size():
    ch = Chunker(b"hello")

    assert ch.file_bytes == b"hello"
    assert ch.chunk_size == 5
    assert ch.chunk() == [b"hello"]