import frame
import codec as cx
import chunker
from pathlib import Path
from helper import create_parser

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
    chunker = chunker.Chunker(file, 12)
    chunks = chunker.chunk()

    hash_frame = frame.HashFrame(file)
    serialized_hash = cx.Codec.serialize(hash_frame)

    print(serialized_hash)
    received = b""

    for chunk in chunks:
        data_frame = frame.DataFrame(chunk)

        serialized = cx.Codec.serialize(data_frame)
        des_frame = cx.Codec.deserialize(serialized)

        received += des_frame.payload

        print(f"{serialized} | {des_frame.payload}")

    file = received.decode("utf-8")
    print(file)
