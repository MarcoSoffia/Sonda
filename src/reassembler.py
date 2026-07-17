from codec import Codec
from frame import DataFrame, Frame, HashFrame


class Reassembler:
    def __init__(self, session_id: int = 333):
        self.session_id = session_id

    def reassemble(self, packets: list) -> tuple[int, HashFrame, list]:
        received = {}

        for sequence, payload in packets:
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

        if initial_frame.session_id != self.session_id:
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
