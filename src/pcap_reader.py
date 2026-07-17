from scapy.all import ICMP, Raw, rdpcap


class PcapReader:
    def __init__(self, icmp_id: int = 333):
        self.icmp_id = icmp_id

    def read(self, file_path: str) -> list:
        packets = rdpcap(str(file_path))
        valid_packets = []

        for packet in packets:
            if not packet.haslayer(ICMP):
                continue

            if packet[ICMP].id != self.icmp_id:
                continue

            if not packet.haslayer(Raw):
                continue

            valid_packets.append(
                (
                    packet[ICMP].seq,
                    bytes(packet[Raw].load),
                )
            )

        return valid_packets
