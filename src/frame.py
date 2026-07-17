from hashlib import sha256
from abc import ABC


class Frame(ABC):
    CODE_HASH = 0x00
    CODE_DATA = 0x01

    def __init__(self, frame_type: int):
        self.type = frame_type    

    @property
    def type(self) -> int:
        return self.__type

    @type.setter
    def type(self, value: int):
        if isinstance(value, int) and value in (self.CODE_HASH, self.CODE_DATA):
            self.__type = value
        else:
            raise TypeError("Invalid frame type")

class DataFrame(Frame):
    def __init__(self, payload: bytes):
        super().__init__(Frame.CODE_DATA)
        self.payload = payload

    @property
    def payload(self) -> bytes:
        return self.__payload

    @payload.setter
    def payload(self, value: bytes):
        if isinstance(value, bytes) and value != b"":
            self.__payload = value
        else:
            raise TypeError("Payload must be non-empty bytes")


class HashFrame(Frame):
    def __init__(
        self,
        file: bytes,
        filename: str,
        n_chunks: int,
        chunk_size: int,
        session_id: int,
    ):
        super().__init__(Frame.CODE_HASH)
        self.file = file
        self.filename = filename
        self.file_size = len(file)
        self.n_chunks = n_chunks
        self.chunk_size = chunk_size
        self.session_id = session_id
        self.digest = self.calculate_hash(file)
        self.validate_metadata()

    @property
    def file(self) -> bytes:
        return self.__file

    @file.setter
    def file(self, file: bytes):
        if isinstance(file, bytes) and file != b"":
            self.__file = file
        else:
            raise TypeError("File must be non-empty bytes")

    @property
    def filename(self) -> str:
        return self.__filename

    @filename.setter
    def filename(self, value: str):
        if not isinstance(value, str):
            raise TypeError("Filename must be a string")

        if value == "" or "/" in value or "\\" in value:
            raise ValueError("Filename must be a valid basename")

        if len(value.encode("utf-8")) > 255:
            raise ValueError("Filename must not exceed 255 bytes")

        self.__filename = value

    @property
    def file_size(self) -> int:
        return self.__file_size

    @file_size.setter
    def file_size(self, value: int):
        if not isinstance(value, int):
            raise TypeError("File size must be an integer")

        if value <= 0:
            raise ValueError("File size must be greater than zero")

        self.__file_size = value

    @property
    def n_chunks(self) -> int:
        return self.__n_chunks

    @n_chunks.setter
    def n_chunks(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Number of chunks must be an integer")

        if value <= 0 or value > 65534:
            raise ValueError("Number of chunks must be between 1 and 65534")

        self.__n_chunks = value

    @property
    def chunk_size(self) -> int:
        return self.__chunk_size

    @chunk_size.setter
    def chunk_size(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Chunk size must be an integer")

        if value <= 0 or value > 1471:
            raise ValueError("Chunk size must be between 1 and 1471")

        self.__chunk_size = value

    @property
    def session_id(self) -> int:
        return self.__session_id

    @session_id.setter
    def session_id(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Session id must be an integer")

        if value < 0 or value > 65535:
            raise ValueError("Session id must be between 0 and 65535")

        self.__session_id = value

    @property
    def digest(self) -> str:
        return self.__digest

    @digest.setter
    def digest(self, value: str):
        if (
            isinstance(value, str)
            and len(value) == 64
            and all(character in "0123456789abcdef" for character in value)
        ):
            self.__digest = value
        else:
            raise TypeError("Digest must be a valid SHA-256 hex string")

    def validate_metadata(self):
        expected_chunks = (
            self.file_size + self.chunk_size - 1
        ) // self.chunk_size

        if self.n_chunks != expected_chunks:
            raise ValueError("Number of chunks does not match file size")

    @staticmethod
    def calculate_hash(file: bytes) -> str:
        h256 = sha256()
        h256.update(file)
        return h256.hexdigest()
