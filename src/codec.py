import json

import frame

class Codec:
    @staticmethod
    def serialize(data: frame.Frame) -> bytes:
        if isinstance(data, frame.DataFrame):
            return bytes([data.type]) + data.payload

        if isinstance(data, frame.HashFrame):
            metadata = {
                "filename": data.filename,
                "file_size": data.file_size,
                "n_chunks": data.n_chunks,
                "chunk_size": data.chunk_size,
                "sha256": data.digest,
                "session_id": data.session_id,
            }

            metadata_raw = json.dumps(
                metadata,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")

            serialized_frame = bytes([data.type]) + metadata_raw

            if len(serialized_frame) > 1472:
                raise ValueError("HashFrame exceeds ICMP payload size")

            return serialized_frame

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
            try:
                metadata = json.loads(payload_raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise ValueError("Invalid HashFrame metadata") from error

            expected_fields = {
                "filename",
                "file_size",
                "n_chunks",
                "chunk_size",
                "sha256",
                "session_id",
            }

            if not isinstance(metadata, dict) or set(metadata) != expected_fields:
                raise ValueError("Invalid HashFrame metadata fields")

            obj = frame.HashFrame.__new__(frame.HashFrame)
            frame.Frame.__init__(obj, frame.Frame.CODE_HASH)
            obj.filename = metadata["filename"]
            obj.file_size = metadata["file_size"]
            obj.n_chunks = metadata["n_chunks"]
            obj.chunk_size = metadata["chunk_size"]
            obj.digest = metadata["sha256"]
            obj.session_id = metadata["session_id"]
            obj.validate_metadata()
            return obj

        raise ValueError("Unknown frame type")


    # Codec rimosso bytetostr e strtobytes a causa dell'aggiunta di overhead 1400 byte di chunk diventavano circa 4200 byte di payload
    # ora manteniamo tutto in bytes senza fare conversioni. Convertito serialize e desereliaze a trattare solo bytes
