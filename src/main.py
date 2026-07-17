from pathlib import Path

from helper import create_parser
from sender import SenderEngine
from strategy import InterleavedStrategy, RedundantStrategy
from reader import Reader

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if args.send:
        file_path = Path(args.send).expanduser()

        if not file_path.exists():
            parser.error(f"File {file_path} does not exist")

        strategy_class, strategy_options = {
            "redundant": (
                RedundantStrategy,
                {"repeat": args.repeat},
            ),
            "interleaved": (
                InterleavedStrategy,
                {"cycles": args.repeat},
            ),
        }[args.strategy]

        sender = SenderEngine(
            strategy_class=strategy_class,
            strategy_options=strategy_options,
            chunk_size=1471,
            icmp_id=333,
        )

        try:
            sent_packets = sender.send(file_path)
        except (OSError, TypeError, ValueError) as error:
            parser.error(str(error))

        print(
            f"Transmission completed: "
            f"{sent_packets} packets sent to {sender.destination}"
        )
    
    elif args.read:
            file_path = Path(args.read)
            saved = "main.py"

            reader = Reader()
            count, hash, file = reader.read(file_path)

            file_data = b"".join(file)

            hash_recieved = reader.calculate_hash(file_data)
            hash_from_file = hash.decode()

            if hash_recieved == hash_from_file:
                saved = Path("received_file").write_bytes(file_data)
                print(f"File received and saved as {saved}")
