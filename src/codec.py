import frame


class Codec:
    @staticmethod
    def bytetostr(payload: bytes) -> str:
        if not isinstance(payload, bytes):
            raise TypeError("Payload must be bytes")

        return "".join(f"{x:03d}" for x in payload)

    @staticmethod
    def strtobyte(serialized: str) -> bytes:
        if not isinstance(serialized, str):
            raise TypeError("Serialized payload must be a string")

        if len(serialized) % 3 != 0:
            raise ValueError("Invalid serialized payload length")

        data = []

        for i in range(0, len(serialized), 3):
            value = int(serialized[i:i + 3])
            data.append(value)

        return bytes(data)

    @staticmethod
    def serialize(data: frame.Frame) -> str:
        if isinstance(data, frame.DataFrame):
            payload = Codec.bytetostr(data.payload)
            return f"{frame.Frame.CODE_DATA}{payload}"

        if isinstance(data, frame.HashFrame):
            return f"{frame.Frame.CODE_HASH}{data.digest}"

        raise TypeError("Unsupported frame")

    @staticmethod
    def deserialize(serialized_frame: str) -> frame.Frame:
        frame_type = int(serialized_frame[:1])
        payload_raw = serialized_frame[1:]

        if frame_type == frame.Frame.CODE_DATA:
            payload = Codec.strtobyte(payload_raw)
            return frame.DataFrame(payload)

        if frame_type == frame.Frame.CODE_HASH:
            obj = frame.HashFrame.__new__(frame.HashFrame)
            frame.Frame.__init__(obj, frame.Frame.CODE_HASH)
            obj.digest = payload_raw
            return obj

        raise ValueError("Unknown frame type")