from scapy.all import ICMP, Raw, rdpcap
from hashlib import sha256

from codec import Codec
from frame import DataFrame, Frame, HashFrame

class Reader:
    def __init__(self, icmp_id: int = 333):
        self.icmp_id = icmp_id

    def read(self, file_path: str) -> tuple[int, HashFrame, list]:
        packets = rdpcap(str(file_path))
        received = {}

        for packet in packets:
            payload = self.read_payload(packet)

            if payload is None:
                continue

            sequence = packet[ICMP].seq

            if sequence in received:
                if received[sequence] != payload:
                    raise ValueError(
                        f"Conflicting payload for sequence {sequence}"
                    )

                continue

            if payload == b"":
                raise ValueError(f"Empty payload for sequence {sequence}")

            if payload[0] not in (Frame.CODE_HASH, Frame.CODE_DATA):
                raise ValueError(f"Unknown frame type for sequence {sequence}")

            received[sequence] = payload

        if 0 not in received:
            raise ValueError("Initial HashFrame is missing")

        initial_frame = Codec.deserialize(received[0])

        if not isinstance(initial_frame, HashFrame):
            raise ValueError("Sequence 0 must contain a HashFrame")

        if initial_frame.session_id != self.icmp_id:
            raise ValueError("HashFrame session id does not match ICMP id")

        final_sequence = initial_frame.n_chunks + 1

        if final_sequence not in received:
            raise ValueError("Final HashFrame is missing")

        final_frame = Codec.deserialize(received[final_sequence])

        if not isinstance(final_frame, HashFrame):
            raise ValueError("Final sequence must contain a HashFrame")

        if (
            initial_frame.filename != final_frame.filename
            or initial_frame.file_size != final_frame.file_size
            or initial_frame.n_chunks != final_frame.n_chunks
            or initial_frame.chunk_size != final_frame.chunk_size
            or initial_frame.digest != final_frame.digest
            or initial_frame.session_id != final_frame.session_id
        ):
            raise ValueError("Initial and final HashFrame do not match")

        expected_sequences = set(range(final_sequence + 1))
        received_sequences = set(received)

        if received_sequences != expected_sequences:
            missing = sorted(expected_sequences - received_sequences)
            unexpected = sorted(received_sequences - expected_sequences)
            raise ValueError(
                f"Invalid packet sequences: missing={missing}, "
                f"unexpected={unexpected}"
            )

        file_chunks = []

        for sequence in range(1, final_sequence):
            current_frame = Codec.deserialize(received[sequence])

            if not isinstance(current_frame, DataFrame):
                raise ValueError(
                    f"Sequence {sequence} must contain a DataFrame"
                )

            expected_size = initial_frame.chunk_size

            if sequence == initial_frame.n_chunks:
                expected_size = initial_frame.file_size - (
                    initial_frame.chunk_size * (initial_frame.n_chunks - 1)
                )

            if len(current_frame.payload) != expected_size:
                raise ValueError(
                    f"Invalid chunk size for sequence {sequence}"
                )

            file_chunks.append(current_frame.payload)

        return len(received), initial_frame, file_chunks

    def read_payload(self, packet) -> bytes:
        if not packet.haslayer(ICMP):
            return None

        if packet[ICMP].id != self.icmp_id:
            return None

        if not packet.haslayer(Raw):
            return None

        return bytes(packet[Raw].load)
    
    @staticmethod
    def calculate_hash(file_data: bytes) -> str:
        return sha256(file_data).hexdigest()
