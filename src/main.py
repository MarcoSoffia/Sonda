import frame
import codec as cx
import chunker
import argparse
from pathlib import Path

def helper() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Sonda",
        usage=argparse.SUPPRESS,
        description="File transfer utility",
        epilog="""
usage: main.py -s file.txt -a 192.168.1.10
usage: main.py -r file.pcap
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-s",
        "--send",
        metavar="FILE",
        help="Send a file over a network protocol",
    )
    group.add_argument(
        "-r",
        "--read",
        metavar="FILE",
        help="Read a file",
    )

    parser.add_argument(
        "-a",
        "--address",
        metavar="ADDRESS",
        help="Destination address",
    )

    parser.add_argument(
        "-st",
        "--strategy",
        help="Select a strategy for sending the file",
    )

    return parser

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    
    parser = helper()
    args = parser.parse_args()

    file = args.read or args.send
    file_path = BASE_DIR / file

    if not file_path.exists():
        print(f"File {file_path} does not exist")
        exit(1)

    # Read, Bytes
    with open(file_path, "rb") as f:
        file = f.read()

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
