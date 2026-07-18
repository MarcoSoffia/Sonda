from pathlib import Path
import secrets

import scapy.all as scapy

from chunker import Chunker
from codec import Codec
from frame import DataFrame, HashFrame
from packet_builder import PacketBuilder
from strategy import TransmissionStrategy
"""
Class tasked with sending a file
"""

class SenderEngine:
    def __init__(
        self,
        strategy_class: type[TransmissionStrategy],
        destination: str = "127.0.0.1",
        strategy_options: dict | None = None,
        chunk_size: int = 1471,
        icmp_id: int | None = None,
    ):
        self.destination = destination
        self.chunk_size = chunk_size
        if icmp_id is None:
            self.icmp_id = secrets.randbelow(65535) + 1
        elif isinstance(icmp_id, int) and 1 <= icmp_id <= 65535:
            self.icmp_id = icmp_id
        else:
            raise ValueError("icmp_id must be between 1 and 65535")
        self.strategy_class = strategy_class
        self.strategy_options = strategy_options or {}

    def send(self, file_path: str) -> int:
        file_data = Path(file_path).read_bytes()

        chunks = Chunker(file_data, self.chunk_size).chunk()

        hash_frame = HashFrame(
            file_data,
            Path(file_path).name,
            len(chunks),
            self.chunk_size,
            self.icmp_id,
        )

        frames = [hash_frame]
        frames.extend(DataFrame(chunk) for chunk in chunks)
        frames.append(hash_frame)

        builder = PacketBuilder(self.destination, self.icmp_id)

        packets = [
            builder.build_packet(
                Codec.serialize(current_frame),
                sequence_number,
            )
            for sequence_number, current_frame in enumerate(frames)
        ]

        strategy = self.strategy_class(packets,**self.strategy_options,)

        packets_to_send = strategy.plan()

        scapy.send(packets_to_send, verbose=False)

        return len(packets_to_send)
