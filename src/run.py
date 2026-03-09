import argparse
import asyncio
import logging

from dotenv import load_dotenv

from src.batch import run_periodic_batch
from src.channel_manager import filter_enabled_channels, parse_channels, resolve_channels
from src.channel_registry import load_channels_config
from src.client import create_client, start_client
from src.config import load_config
from src.logger import setup_logger
from src.main import run_client, setup_handlers
from src.pathing import resolve_in_workspace, resolve_workspace_dir


def configure_runtime_logging(log_level="INFO", log_dir="logs"):
    bootstrap_logger = setup_logger("ticc", log_dir=log_dir)
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, str(log_level).upper(), logging.INFO))

    if not root_logger.handlers:
        for handler in bootstrap_logger.handlers:
            root_logger.addHandler(handler)


def load_enabled_channels(channels_path):
    config = load_channels_config(channels_path)
    channels = parse_channels(config)
    return filter_enabled_channels(channels)


async def run_realtime_mode(channels_path="channels.json", workspace_dir=None):
    load_dotenv()
    config = load_config()
    workspace_dir = resolve_workspace_dir(workspace_dir)

    log_dir = resolve_in_workspace(config.get("log_dir", "logs"), workspace_dir)
    configure_runtime_logging(config.get("log_level", "INFO"), log_dir=log_dir)

    resolved_channels_path = resolve_in_workspace(channels_path, workspace_dir)
    channels = load_enabled_channels(resolved_channels_path)

    session_dir = resolve_in_workspace(config.get("session_dir", "session"), workspace_dir)
    client = create_client(config, session_dir=session_dir)
    resolved = await resolve_channels(client, channels)
    channel_map = {ch["entity"].id: ch["alias"] for ch in resolved}

    setup_handlers(client, channel_map)
    await run_client(client, phone=config["phone"])


async def run_batch_mode(channels_path="channels.json", metadata_path="data/_metadata.json", workspace_dir=None):
    load_dotenv()
    config = load_config()
    workspace_dir = resolve_workspace_dir(workspace_dir)

    log_dir = resolve_in_workspace(config.get("log_dir", "logs"), workspace_dir)
    configure_runtime_logging(config.get("log_level", "INFO"), log_dir=log_dir)

    resolved_channels_path = resolve_in_workspace(channels_path, workspace_dir)
    resolved_metadata_path = resolve_in_workspace(metadata_path, workspace_dir)
    data_dir = resolve_in_workspace(config.get("data_dir", "data"), workspace_dir)

    channels = load_enabled_channels(resolved_channels_path)

    session_dir = resolve_in_workspace(config.get("session_dir", "session"), workspace_dir)
    client = create_client(config, session_dir=session_dir)
    await start_client(client, phone=config["phone"])
    await run_periodic_batch(
        client,
        channels,
        metadata_path=resolved_metadata_path,
        data_dir=data_dir,
        interval_sec=config.get("batch_interval_sec", 300),
    )


def build_parser():
    parser = argparse.ArgumentParser(description="Run Telegram collector runtime.")
    parser.add_argument("--mode", choices=["realtime", "batch"], default="realtime")
    parser.add_argument("--channels-file", default="channels.json")
    parser.add_argument("--metadata-path", default="data/_metadata.json")
    parser.add_argument("--workspace", default=None)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.mode == "batch":
        asyncio.run(
            run_batch_mode(
                channels_path=args.channels_file,
                metadata_path=args.metadata_path,
                workspace_dir=args.workspace,
            )
        )
    else:
        asyncio.run(run_realtime_mode(channels_path=args.channels_file, workspace_dir=args.workspace))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())