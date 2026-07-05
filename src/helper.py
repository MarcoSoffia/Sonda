import argparse

def create_parser() -> argparse.ArgumentParser:
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