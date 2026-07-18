from scapy.all import ICMP, Raw, rdpcap

"""
Class tasked with reading the pcap file captured
"""

class PcapReader:
    def read(self, file_path: str) -> list[tuple[int, int, bytes]]:
        packets = rdpcap(str(file_path))
        icmp_payloads = []

        for packet in packets:
            if not packet.haslayer(ICMP):
                continue

            if not packet.haslayer(Raw):
                continue

            icmp_payloads.append(
                (
                    packet[ICMP].id,
                    packet[ICMP].seq,
                    bytes(packet[Raw].load),
                )
            )

        return icmp_payloads
