import argparse
import json

from src.channel_registry import add_channel, list_channels, remove_channel, set_channel_enabled
from src.pathing import resolve_in_workspace, resolve_workspace_dir


def _add_common_path_args(parser):
    parser.add_argument("--channels-file", default="channels.json")
    parser.add_argument("--workspace", default=None)


def _resolve_channels_path(args):
    workspace = resolve_workspace_dir(args.workspace)
    return resolve_in_workspace(args.channels_file, workspace)


def build_parser():
    parser = argparse.ArgumentParser(description="Manage channels.json entries.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a channel entry")
    _add_common_path_args(add_parser)
    add_parser.add_argument("--alias", required=True)
    add_parser.add_argument("--username")
    add_parser.add_argument("--id", type=int, dest="channel_id")
    add_parser.add_argument("--disabled", action="store_true")

    list_parser = subparsers.add_parser("list", help="List channels")
    _add_common_path_args(list_parser)

    enable_parser = subparsers.add_parser("enable", help="Enable a channel")
    _add_common_path_args(enable_parser)
    enable_parser.add_argument("--alias", required=True)

    disable_parser = subparsers.add_parser("disable", help="Disable a channel")
    _add_common_path_args(disable_parser)
    disable_parser.add_argument("--alias", required=True)

    remove_parser = subparsers.add_parser("remove", help="Remove a channel")
    _add_common_path_args(remove_parser)
    remove_parser.add_argument("--alias", required=True)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    channels_path = _resolve_channels_path(args)

    if args.command == "add":
        entry = add_channel(
            channels_path=channels_path,
            alias=args.alias,
            username=args.username,
            channel_id=args.channel_id,
            enabled=not args.disabled,
        )
        print(json.dumps(entry, ensure_ascii=False))
        return 0

    if args.command == "list":
        print(json.dumps({"channels": list_channels(channels_path)}, ensure_ascii=False))
        return 0

    if args.command == "enable":
        entry = set_channel_enabled(channels_path, alias=args.alias, enabled=True)
        print(json.dumps(entry, ensure_ascii=False))
        return 0

    if args.command == "disable":
        entry = set_channel_enabled(channels_path, alias=args.alias, enabled=False)
        print(json.dumps(entry, ensure_ascii=False))
        return 0

    if args.command == "remove":
        entry = remove_channel(channels_path, alias=args.alias)
        print(json.dumps(entry, ensure_ascii=False))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
