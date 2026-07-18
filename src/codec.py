import json

import frame
"""
Class tasked with serializing the frames
"""
class Codec:
    PROTOCOL_MAGIC = b"SONDA"
    PROTOCOL_VERSION = 1

    @classmethod
    def is_sonda_hash_frame(cls, serialized_frame: bytes) -> bool:
        """Return whether *serialized_frame* has the Sonda hash-frame header."""
        header = (
            bytes([frame.Frame.CODE_HASH])
            + cls.PROTOCOL_MAGIC
            + bytes([cls.PROTOCOL_VERSION])
        )
        return isinstance(serialized_frame, bytes) and serialized_frame.startswith(
            header
        )

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

            serialized_frame = (
                bytes([data.type])
                + Codec.PROTOCOL_MAGIC
                + bytes([Codec.PROTOCOL_VERSION])
                + metadata_raw
            )

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
            header_size = len(Codec.PROTOCOL_MAGIC) + 1

            if len(payload_raw) < header_size:
                raise ValueError("Invalid Sonda HashFrame header")

            magic = payload_raw[: len(Codec.PROTOCOL_MAGIC)]
            version = payload_raw[len(Codec.PROTOCOL_MAGIC)]

            if magic != Codec.PROTOCOL_MAGIC:
                raise ValueError("Unknown HashFrame protocol")

            if version != Codec.PROTOCOL_VERSION:
                raise ValueError("Unsupported Sonda protocol version")

            try:
                metadata = json.loads(payload_raw[header_size:].decode("utf-8"))
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