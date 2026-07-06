import packet_builder
from abc import ABC, abstractmethod

class TransmissionStrategy(ABC):
    def __init__(self, packets: list):
        self.packets = packets

    @property
    def packets(self):
        return self.__packets

    @packets.setter
    def packets(self, value: list):
        if not isinstance(value, list):
            raise TypeError("packets must be a list")

        if value == []:
            raise ValueError("packets cannot be empty")

        self.__packets = value

    @abstractmethod
    def plan(self) -> list:
        pass

class RedundantStrategy(TransmissionStrategy):
    def __init__(self, packets: list, repeat: int):
        super().__init__(packets)
        self.repeat = repeat

    @property
    def repeat(self):
        return self.__repeat

    @repeat.setter
    def repeat(self, value: int):
        if not isinstance(value, int):
            raise TypeError("repeat must be an integer")

        if value <= 0:
            raise ValueError("repeat must be greater than zero")

        self.__repeat = value

    def plan(self) -> list:
        return [packet for packet in self.packets for _ in range(self.repeat)]