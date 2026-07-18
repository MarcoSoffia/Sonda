from hashlib import sha256

from codec import Codec
from frame import HashFrame
from pcap_reader import PcapReader
from reassembler import Reassembler

"""
Class that orchestrates the reading of a transmission
"""
class Reader:
    def __init__(self):
        self.pcap_reader = PcapReader()

    def read(self, file_path: str) -> tuple[int, HashFrame, list]:
        packets = self.pcap_reader.read(file_path)

        for session_id, sequence, payload in packets:
            if sequence != 0 or not Codec.is_sonda_hash_frame(payload):
                continue

            try:
                initial_frame = Codec.deserialize(payload)
            except (TypeError, ValueError):
                continue

            if (
                not isinstance(initial_frame, HashFrame)
                or initial_frame.session_id != session_id
            ):
                continue

            session_packets = [
                (packet_sequence, packet_payload)
                for packet_session_id, packet_sequence, packet_payload in packets
                if packet_session_id == session_id
            ]

            try:
                return Reassembler(session_id).reassemble(session_packets)
            except (TypeError, ValueError):
                continue

        raise ValueError("No complete Sonda transfer found in the PCAP")
    
    @staticmethod
    def calculate_hash(file_data: bytes) -> str:
        return sha256(file_data).hexdigest()
