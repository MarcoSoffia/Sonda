"""
Function that builds the packets
"""

import scapy.all as scapy
from frame import HashFrame, DataFrame, Frame

class PacketBuilder:
    def __init__(self,ip: str, id: int):
        self.ip = ip
        self.id = id

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self,value: int):
        if isinstance(value, int):
            self.__id = value
        else:
            raise TypeError("id must be a integer")

    @property
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self,value: str):
        if isinstance(value, str):
            self.__ip = value
        else:
            raise TypeError("ip must be a string")


    def build_packet(self,payload: bytes, seq: int):
        if not isinstance(payload, bytes):
            raise TypeError("Payload must be a bytes")

        pkt = (
                scapy.IP(dst=self.ip)
                / scapy.ICMP(id=self.id, seq=seq)
                / scapy.Raw(load=payload)
        )
        return pkt
