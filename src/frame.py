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
    def __init__(self, file: bytes):
        super().__init__(Frame.CODE_HASH)
        self.file = file
        self.digest = self.calculate_hash(file)

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
    def digest(self) -> str:
        return self.__digest

    @digest.setter
    def digest(self, value: str):
        if isinstance(value, str) and len(value) == 64:
            self.__digest = value
        else:
            raise TypeError("Digest must be a valid SHA-256 hex string")

    @staticmethod
    def calculate_hash(file: bytes) -> str:
        h256 = sha256()
        h256.update(file)
        return h256.hexdigest()