import frame
import chunker
import packet_builder as pb
from codec import Codec as cx
from pathlib import Path
from helper import create_parser
import scapy.all as scapy

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    
    parser = create_parser()
    args = parser.parse_args()

    file = args.read or args.send
    file_path = BASE_DIR / file

    if not file_path.exists():
        print(f"File {file_path} does not exist")
        exit(1)

    with open(file_path, "rb") as f:
        file = f.read()

    # Da spostare la lettura del file all'interno del chunker ? 
    chunker = chunker.Chunker(file, 1472)
    chunks = chunker.chunk()

    for seq,chunk in enumerate(chunks):
        packet = pb.PacketBuilder("127.0.0.1",333)
        pkt = packet.build_packet(cx.serialize(frame.DataFrame(chunk)), seq)

        pkt.show()


        
