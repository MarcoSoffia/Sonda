from scapy.all import ICMP, Raw, rdpcap
from hashlib import sha256

class Reader:
    def __init__(self, icmp_id: int = 333):
        self.icmp_id = icmp_id

    def read(self, file_path: str) -> tuple[int, str, list]:
        packets = rdpcap(str(file_path))
        received = {}
        file_chunks = []
        received_hash = None

        for packet in packets:
            payload = self.read_payload(packet)

            if payload is None:
                continue

            sequence = packet[ICMP].seq

            if sequence in received:
                continue

            received[sequence] = payload

            if payload[0] == 0x00:
                received_hash = payload[1:]
            else:
                file_chunks.append(payload[1:])

        return len(received), received_hash, file_chunks

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