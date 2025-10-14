import asyncio
import json
from pydantic import config
import redis.asyncio as redis

from zenx.exceptions import NoBlueprintAvailable, NoSessionAvailable
from .base import SessionManager
from .types import Session
from zenx.utils import get_time



class MemorySessionManager(SessionManager):
    name = "memory"


    async def init_session_pool(self) -> None:
        while self.session_pool.qsize() < self.settings.SESSION_POOL_SIZE:
            session = self.client.create_session(**self.session_init_args)
            await self.put_session(session)
        self.logger.info("initialized", session_pool_size=self.session_pool.qsize(), session_manager=self.name)


    async def get_session(self) -> Session:
        try:
            session = await asyncio.wait_for(self.session_pool.get(), timeout=10.0)
            return session
        except asyncio.TimeoutError:
            self.logger.info("timeout", session_pool_size=self.session_pool.qsize(), session_manager=self.name)
            raise NoSessionAvailable()


    async def put_session(self, session: Session) -> None:
        self.session_pool.put_nowait(session)


    async def close_session(self, session: Session) -> None:
        await session.close()


    async def replace_session(self, session: Session, reason: str = "") -> Session:
        await self.close_session(session)
        new_session = self.client.create_session(**self.session_init_args)
        self.logger.debug("replaced_session", old=session.id, new=new_session.id, reason=reason, age=(get_time() - session.created_at)/1000, requests=session.requests)
        return new_session



class RedisSessionManager(SessionManager):
    name = "redis"


    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.r = redis.Redis(host=self.settings.DB_HOST, port=self.settings.DB_PORT, password=self.settings.DB_PASS, decode_responses=True, socket_timeout=30)


    async def _get_blueprints_size(self) -> int:
        return await self.r.llen(self.settings.SESSION_BLUEPRINT_REDIS_KEY)


    async def init_session_pool(self) -> None:
        while self.session_pool.qsize() < self.settings.SESSION_POOL_SIZE:
            config_json = await self.r.rpop(self.settings.SESSION_BLUEPRINT_REDIS_KEY)
            if not config_json:
                self.logger.info("no_blueprint_available", session_pool_size=self.session_pool.qsize(), blueprint_redis_key=self.settings.SESSION_BLUEPRINT_REDIS_KEY, session_manager=self.name)
                await asyncio.sleep(2)
                continue
            config_dict = json.loads(config_json)
            # merge init_args with config_dict
            for k, v in self.session_init_args.items():
                if k == "proxy": # proxy is already set in the blueprint, it should not be overridden in any case
                    continue
                if k in config_dict:
                    config_dict[k].update(v)
                    continue
                config_dict[k] = v
            session = self.client.create_session(**config_dict)
            await self.put_session(session)
            self.logger.debug("updating", session_pool_size=self.session_pool.qsize(), blueprint_redis_key=self.settings.SESSION_BLUEPRINT_REDIS_KEY, session_manager=self.name)
        self.logger.info("initialized", session_pool_size=self.session_pool.qsize(), session_manager=self.name)


    async def get_session(self) -> Session:
        try:
            session = await asyncio.wait_for(self.session_pool.get(), timeout=10.0)
            return session
        except asyncio.TimeoutError:
            self.logger.info("timeout", session_pool_size=self.session_pool.qsize(), session_manager=self.name)
            raise NoSessionAvailable()


    async def put_session(self, session: Session) -> None:
        self.session_pool.put_nowait(session)


    async def close_session(self, session: Session) -> None:
        await session.close()


    async def replace_session(self, session: Session, reason: str = "") -> Session:
        config_json = await self.r.rpop(self.settings.SESSION_BLUEPRINT_REDIS_KEY)
        if not config_json:
            self.logger.info("no_blueprint_available", session_pool_size=self.session_pool.qsize(), blueprint_redis_key=self.settings.SESSION_BLUEPRINT_REDIS_KEY, session_manager=self.name)
            raise NoBlueprintAvailable()
        await self.close_session(session)
        config_dict = json.loads(config_json)
        # merge init_args with config_dict
        for k, v in self.session_init_args.items():
            if k == "proxy":
                if k not in config_dict:
                    config_dict[k] = v
                continue
            if k in config_dict:
                config_dict[k].update(v)
                continue
            config_dict[k] = v
        new_session = self.client.create_session(**config_dict)
        self.logger.debug("replaced_session", old=session.id, new=new_session.id, reason=reason, age=(get_time() - session.created_at)/1000, requests=session.requests)
        return new_session
