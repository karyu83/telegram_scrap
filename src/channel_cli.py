import argparse
import json

from src.channel_registry import add_channel


def build_parser():
    parser = argparse.ArgumentParser(description="Manage channels.json entries.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a channel entry")
    add_parser.add_argument("--channels-file", default="channels.json")
    add_parser.add_argument("--alias", required=True)
    add_parser.add_argument("--username")
    add_parser.add_argument("--id", type=int, dest="channel_id")
    add_parser.add_argument("--disabled", action="store_true")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "add":
        entry = add_channel(
            channels_path=args.channels_file,
            alias=args.alias,
            username=args.username,
            channel_id=args.channel_id,
            enabled=not args.disabled,
        )
        print(json.dumps(entry, ensure_ascii=False))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
