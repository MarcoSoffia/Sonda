from pathlib import Path

import scapy.all as scapy

from chunker import Chunker
from codec import Codec
from frame import DataFrame, HashFrame
from packet_builder import PacketBuilder
from strategy import TransmissionStrategy


class SenderEngine:
    def __init__(
        self,
        strategy_class: type[TransmissionStrategy],
        destination: str = "127.0.0.1",
        strategy_options: dict | None = None,
        chunk_size: int = 1471,
        icmp_id: int = 333,
    ):
        self.destination = destination
        self.chunk_size = chunk_size
        self.icmp_id = icmp_id
        self.strategy_class = strategy_class
        self.strategy_options = strategy_options or {}

    def send(self, file_path: str) -> int:
        file_data = Path(file_path).read_bytes()

        chunks = Chunker(file_data, self.chunk_size).chunk()

        frames = [DataFrame(chunk) for chunk in chunks]
        frames.append(HashFrame(file_data))

        builder = PacketBuilder(self.destination, self.icmp_id)

        packets = [
            builder.build_packet(
                Codec.serialize(current_frame),
                sequence_number,
            )
            for sequence_number, current_frame in enumerate(frames)
        ]

        strategy = self.strategy_class(
            packets,
            **self.strategy_options,
        )

        packets_to_send = strategy.plan()

        scapy.send(packets_to_send, verbose=False)

        return len(packets_to_send)
