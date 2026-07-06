"""
Function that builds a packet
"""

import scapy.all as scapy
from frame import HashFrame, DataFrame, Frame

class PacketBuilder:
    @staticmethod
    def build_packet(payload: bytes, seq: int):
        if not isinstance(payload, bytes):
            raise TypeError("Payload must be a bytes")

        pkt = (
                scapy.IP(dst="172.20.129.149")
                / scapy.ICMP(id=333, seq=seq)
                / scapy.Raw(load=payload)
        )
        return pkt
