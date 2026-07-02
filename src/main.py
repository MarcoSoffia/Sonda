import chunker
import argparse
from pathlib import Path

def helper() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
            prog="Sonda",
            usage=argparse.SUPPRESS,
            description="File exfiltration over network",
            epilog="""
usage: main.py -s file.txt -a 192.168.1.10
usage: main.py -r file.pcap
            """,
            formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-s", "--send", metavar="FILE", help="Send a file over a network protocol")
    parser.add_argument("-r", "--read", metavar="FILE", help="Read a pcap file")
    parser.add_argument("-st", "--strategy", help="Select a strategy for sending the file")

    return parser 

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    
    parser = helper()
    args = parser.parse_args()

    file_path = BASE_DIR / args.read

    # Read, Bytes
    with open(file_path, "rb") as f:
        file = f.read()

    chunker = chunker.Chunker(file)
    chunks = chunker.chunk()

    [print(chunk) for chunk in chunks]

