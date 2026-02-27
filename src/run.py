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


def configure_runtime_logging(log_level="INFO"):
    bootstrap_logger = setup_logger("ticc")
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, str(log_level).upper(), logging.INFO))

    if not root_logger.handlers:
        for handler in bootstrap_logger.handlers:
            root_logger.addHandler(handler)


def load_enabled_channels(channels_path):
    config = load_channels_config(channels_path)
    channels = parse_channels(config)
    return filter_enabled_channels(channels)


async def run_realtime_mode(channels_path="channels.json"):
    load_dotenv()
    config = load_config()
    configure_runtime_logging(config.get("log_level", "INFO"))

    channels = load_enabled_channels(channels_path)
    client = create_client(config)
    resolved = await resolve_channels(client, channels)
    channel_map = {ch["entity"].id: ch["alias"] for ch in resolved}

    setup_handlers(client, channel_map)
    await run_client(client, phone=config["phone"])


async def run_batch_mode(channels_path="channels.json", metadata_path="data/_metadata.json"):
    load_dotenv()
    config = load_config()
    configure_runtime_logging(config.get("log_level", "INFO"))

    channels = load_enabled_channels(channels_path)
    client = create_client(config)
    await start_client(client, phone=config["phone"])
    await run_periodic_batch(
        client,
        channels,
        metadata_path=metadata_path,
        data_dir=config.get("data_dir", "data"),
        interval_sec=config.get("batch_interval_sec", 300),
    )


def build_parser():
    parser = argparse.ArgumentParser(description="Run Telegram collector runtime.")
    parser.add_argument("--mode", choices=["realtime", "batch"], default="realtime")
    parser.add_argument("--channels-file", default="channels.json")
    parser.add_argument("--metadata-path", default="data/_metadata.json")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.mode == "batch":
        asyncio.run(
            run_batch_mode(
                channels_path=args.channels_file,
                metadata_path=args.metadata_path,
            )
        )
    else:
        asyncio.run(run_realtime_mode(channels_path=args.channels_file))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
