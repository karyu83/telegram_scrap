import asyncio
import logging

from src.batch_collector import collect_batch

logger = logging.getLogger(__name__)


async def run_batch(client, channels, metadata_path, data_dir="data"):
    results = {}
    for ch in channels:
        if not ch.get("enabled", False):
            continue

        alias = ch["alias"]
        identifier = ch.get("username") or ch.get("id")

        try:
            entity = await client.get_entity(identifier)
            count = await collect_batch(client, entity, alias, metadata_path=metadata_path, data_dir=data_dir)
            results[alias] = count
            logger.info("Batch collected %d messages from %s", count, alias)
        except Exception as e:
            logger.error("Batch collection failed for %s: %s", alias, e)
            results[alias] = 0

    return results


async def run_periodic_batch(client, channels, metadata_path, data_dir="data", interval_sec=300):
    while True:
        await run_batch(client, channels, metadata_path=metadata_path, data_dir=data_dir)
        logger.info("Next batch in %d seconds", interval_sec)
        await asyncio.sleep(interval_sec)
