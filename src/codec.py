import frame

class Codec:
    @staticmethod
    def serialize(data: frame.Frame) -> bytes:
        if isinstance(data, frame.DataFrame):
            return bytes([data.type]) + data.payload

        if isinstance(data, frame.HashFrame):
            return bytes([data.type]) + data.digest.encode("ascii")

        raise TypeError("Unsupported frame")

    @staticmethod
    def deserialize(serialized_frame: bytes) -> frame.Frame:
        if not isinstance(serialized_frame, bytes):
            raise TypeError("Serialized frame must be bytes")

        if serialized_frame == b"":
            raise ValueError("Serialized frame must not be empty")

        frame_type = serialized_frame[0]
        payload_raw = serialized_frame[1:]

        if frame_type == frame.Frame.CODE_DATA:
            return frame.DataFrame(payload_raw)

        if frame_type == frame.Frame.CODE_HASH:
            obj = frame.HashFrame.__new__(frame.HashFrame)
            frame.Frame.__init__(obj, frame.Frame.CODE_HASH)
            obj.digest = payload_raw.decode("ascii")
            return obj

        raise ValueError("Unknown frame type")


    # Codec rimosso bytetostr e strtobytes a causa dell'aggiunta di overhead 1400 byte di chunk diventavano circa 4200 byte di payload
    # ora manteniamo tutto in bytes senza fare conversioni. Convertito serialize e desereliaze a trattare solo bytes