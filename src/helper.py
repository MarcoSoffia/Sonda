import argparse
"""
Clip helper
"""
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
        metavar="PCAP",
        help="Read packets from the specified PCAP file.",
    )

    parser.add_argument(
        "-a",
        "--address",
        metavar="ADDRESS",
        help="Destination address (required with --send)",
    )

    parser.add_argument(
        "-st",
        "--strategy",
        choices=("redundant", "interleaved"),
        default="redundant",
        help="Select a strategy for sending the file",
    )

    parser.add_argument(
        "-n",
        "--repeat",
        type=int,
        default=3,
        metavar="N",
        help="Number of repetitions or transmission cycles",
    )

    return parser
