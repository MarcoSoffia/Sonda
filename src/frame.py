
class Frame:
    TYPE_META = 0x00
    TYPE_DATA = 0x01

    def __init__(self, type: int, payload: bytes, ):
        self.type = type
        self.payload = payload

    def serialize(self) -> bytes:
        return self.type.to_bytes(1, 'big') + self.payload