from hashlib import sha256
from abc import ABC, abstractmethod

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

    @abstractmethod
    def serialize(self) -> str:
        pass


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
            self.__payload = list(value)
        else:
            raise TypeError("payload must be non-empty bytes")

    def serialize(self) -> str:
        return "".join(str(x) for x in list(self.payload))


class HashFrame(Frame):
    def __init__(self, file: bytes):
        super().__init__(Frame.CODE_HASH)
        self.file = file

    @property
    def file(self) -> bytes:
        return self.__file

    @file.setter
    def file(self, file: bytes):
        if isinstance(file, bytes) and file != b"":
            self.__file = file
        else:
            raise TypeError("file must be non-empty bytes")

    def serialize(self) -> str:
        if not isinstance(self.file, bytes):
            raise TypeError("file must be bytes")
        
        h256 = sha256()
        h256.update(self.file)
        return h256.hexdigest()