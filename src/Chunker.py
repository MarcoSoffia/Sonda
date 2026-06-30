"""
Class tasked with chunking the file given
"""
class Chunker:
    def __init__(self,text, chunk_size=5):
        self.file_bytes = text
        self.chunk_size = chunk_size

    def chunk(self) -> list:
        return[
            self.file_bytes[x:x + self.chunk_size]
            for x in range(0,len(self.file_bytes),self.chunk_size)
        ]

    @property
    def file_bytes(self):
        return self.__file_bytes

    @file_bytes.setter
    def file_bytes(self, value):
        if isinstance(value, bytes) and value != b"":
            self.__file_bytes = value
        else:
            raise TypeError

    @property
    def chunk_size(self):
        return self.__chunk_size
    @chunk_size.setter
    def chunk_size(self, value):
        if isinstance(value, int) and value > 0:
            self.__chunk_size = value
        else:
            raise TypeError