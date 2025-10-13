import inspect
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Generator
from contextlib import contextmanager

from init_provider import BaseProvider, init
from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import (
    sessionmaker,
    Session,
)
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
    AsyncEngine,
)


create_engine_argpspec = inspect.getfullargspec(create_engine)
session_maker_argpspec = inspect.getfullargspec(sessionmaker)


def _convert_env(value: Any, type_: Any | None) -> Any:
    if isinstance(type_, str):
        if type_ == "bool":
            return value.lower() in ("true", "1", "t", "y", "yes")
        elif type_ == "int":
            return int(value)
        elif type_ == "float":
            return float(value)
        elif type_ == "str":
            return str(value)
    raise ValueError(f"Unsupported env var type: {type_}")


class Database(BaseProvider):
    env_prefix = "DATABASE"
    url: str
    async_url: str | None
    engine_params: dict[str, Any] = {}
    session_params: dict[str, Any] = {}

    engine: Engine
    async_engine: AsyncEngine | None
    
    session_maker: sessionmaker
    async_session_maker: async_sessionmaker | None

    def __init__(self) -> None:
        self.url = os.environ[f"{self.env_prefix}_ENGINE_URL"]
        self.async_url = os.environ.get(f"{self.env_prefix}_ENGINE_ASYNC_URL")

        env_prefix_engine = f"{self.env_prefix}_ENGINE_"
        env_prefix_sessions = f"{self.env_prefix}_SESSION_"
        for env, value in os.environ.items():
            if env.startswith(env_prefix_engine):
                key = env[len(env_prefix_engine):].lower()
                if key == "url" or key == "async_url":
                    continue
                if key in create_engine_argpspec.kwonlyargs:
                    type_ = create_engine_argpspec.annotations.get(key)
                    self.engine_params[key] = _convert_env(value, type_)

            elif env.startswith(env_prefix_sessions):
                key = env[len(env_prefix_sessions):].lower()
                if key in session_maker_argpspec.kwonlyargs:
                    type_ = session_maker_argpspec.annotations.get(key)
                    self.session_params[key] = _convert_env(value, type_)

        self.engine = create_engine(self.url, **self.engine_params)
        self.session_maker = sessionmaker(
            bind=self.engine,
            **self.session_params,
        )

        if self.async_url:
            self.async_engine = create_async_engine(self.async_url, **self.engine_params)
            self.async_session_maker = async_sessionmaker(
                bind=self.async_engine,
                **self.session_params,
            )
        else:
            self.async_engine = None
            self.async_session_maker = None

        with self.engine.connect() as c:
            result = c.execute(text("SELECT 1"))
            if result.fetchone() is None:
                raise RuntimeError("Database test failed")

    @init
    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        with self.session_maker() as session:
            yield session

    @init
    @asynccontextmanager
    async def async_session(self) -> AsyncGenerator[AsyncSession, None]:
        if self.async_session_maker:
            async with self.async_session_maker() as session:
                yield session
        else:
            raise RuntimeError("No async URL provided")
