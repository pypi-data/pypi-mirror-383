import argparse
from outlook_meetings.outlookmeet import maincall


def create_parser():

    parser = argparse.ArgumentParser(
        "Easy Outlook appointments from terminal or command line"
    )
    parser.add_argument(
        "message",
        nargs="*",
        type=str,
        help="Meeting text if date it will be parserd",
    )
    parser.add_argument(
        "-i",
        "--invite",
        type=str,
        help="Specify email to invite, default None",
        default=None,
    )
    parser.add_argument(
        "-on", "--on", nargs="*", type=str, help="On what date", default=None
    )
    parser.add_argument(
        "-w", "--where", type=str, help="Where. specify location", default="NoWhere"
    )
    parser.add_argument(
        "-d", "--duration", type=str, help="Specify duration in mins", default=None
    )

    parser.add_argument(
        "-b",
        "--body",
        type=str,
        nargs="*",
        help="Body to include in the invite '-'  to use stdin. ",
        default=None,
    )

    parser.add_argument(
        "-ds",
        "--dont-send",
        action="store_true",
        help="If given don't send message just show user to confirm",
    )

    parser.add_argument(
        "-ad",
        "--all-day",
        action="store_true",
        help="If given this is a all day event",
    )

    return parser


def cli():
    "Create outlook meetings using cli"
    parser = create_parser()
    args = parser.parse_args()
    maincall(args)
