from typing import Dict, List
import redis.asyncio as redis
import asyncio

from zenx.settings import settings
from zenx.logger import configure_logger
from zenx.spiders.base import Spider


logger = configure_logger("mitm", settings)
solver_redis = redis.Redis(host=settings.SOLVER_REDIS_HOST, port=6379, password=settings.SOLVER_REDIS_PASS, decode_responses=True, socket_timeout=30)
local_redis = redis.Redis(host="localhost", port=6379, decode_responses=True, socket_timeout=30)


async def consume_target(target: str):
    logger.info("consuming", target=target)
    while True:
        try:
            local_current_size = await local_redis.llen(target)
            if local_current_size >= settings.SESSION_SPARE_BLUEPRINTS: # number of spare blueprints
                logger.debug("spare_blueprints", target=target, local_current_size=local_current_size)
                await asyncio.sleep(1)
                continue
            
            blueprints = await solver_redis.rpop(target, count=settings.SESSION_SPARE_BLUEPRINTS - local_current_size)
            if not blueprints:
                logger.debug("empty", target=target)
                continue
            await local_redis.lpush(target, *blueprints)
            logger.info("got", target=target, blueprints=len(blueprints))
        except Exception:
            logger.exception("consuming_failed", target=target)
            continue


def collect_targets() -> List[Dict]:
    targets = []
    spiders = Spider.spider_list()
    for spider in spiders:
        spider_cls = Spider.get_spider(spider)
        blueprint_key = spider_cls.custom_settings.get("SESSION_BLUEPRINT_REDIS_KEY")
        if not blueprint_key and len(spiders) == 1:
            blueprint_key = settings.SESSION_BLUEPRINT_REDIS_KEY
        if not blueprint_key:
            continue
        targets.append(blueprint_key)
    logger.info("collected_targets", targets=targets)
    return targets


async def run():
    targets = collect_targets()
    async with asyncio.TaskGroup() as tg:
        for target in targets:
            tg.create_task(consume_target(target))
