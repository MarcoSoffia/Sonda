from pathlib import Path

from helper import create_parser
from sender import SenderEngine
from strategy import InterleavedStrategy, RedundantStrategy
from reader import Reader

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if args.send:
        if not args.address:
            parser.error("--address is required when using --send")

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
            destination=args.address,
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
        reader = Reader()

        try:
            count, hash_frame, file = reader.read(file_path)
            file_data = b"".join(file)
            received_hash = reader.calculate_hash(file_data)

            if len(file_data) != hash_frame.file_size:
                raise ValueError("Received file size does not match metadata")

            if received_hash != hash_frame.digest:
                raise ValueError("Received file hash does not match metadata")

            output_path = Path(f"received_{hash_frame.filename}")
            output_path.write_bytes(file_data)
        except (OSError, TypeError, ValueError) as error:
            parser.error(str(error))

        print(
            f"Transmission received successfully\n"
            f"Filename: {hash_frame.filename}\n"
            f"File size: {hash_frame.file_size} bytes declared, "
            f"{len(file_data)} bytes received\n"
            f"Chunks: {len(file)}/{hash_frame.n_chunks}\n"
            f"Chunk size: {hash_frame.chunk_size} bytes\n"
            f"SHA-256: {hash_frame.digest}\n"
            f"Session id: {hash_frame.session_id}\n"
            f"Unique packets: {count}\n"
            f"Integrity: OK\n"
            f"Saved as: {output_path.resolve()}"
        )
