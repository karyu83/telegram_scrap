import argparse
import json
from pathlib import Path

from src.pathing import resolve_in_workspace, resolve_workspace_dir


def _list_log_files(log_dir):
    directory = Path(log_dir)
    if not directory.exists():
        return []
    return sorted([p.name for p in directory.glob("collector_*.log")])


def _read_last_lines(filepath, lines):
    content = Path(filepath).read_text(encoding="utf-8")
    split_lines = content.splitlines()
    return "\n".join(split_lines[-lines:])


def build_parser():
    parser = argparse.ArgumentParser(description="Inspect collector log files.")
    parser.add_argument("--workspace", default=None)
    parser.add_argument("--log-dir", default="logs")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List collector log files")

    tail_parser = subparsers.add_parser("tail", help="Print tail of collector log")
    tail_parser.add_argument("--file", default=None, help="Specific log file name")
    tail_parser.add_argument("--lines", type=int, default=50)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    workspace = resolve_workspace_dir(args.workspace)
    log_dir = resolve_in_workspace(args.log_dir, workspace)

    if args.command == "list":
        print(json.dumps({"log_dir": log_dir, "files": _list_log_files(log_dir)}, ensure_ascii=False))
        return 0

    if args.command == "tail":
        files = _list_log_files(log_dir)
        if not files:
            raise ValueError(f"No log files found in: {log_dir}")

        target_name = args.file or files[-1]
        target = Path(log_dir) / target_name
        if not target.exists():
            raise ValueError(f"Log file not found: {target_name}")

        print(_read_last_lines(target, lines=max(1, args.lines)))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
