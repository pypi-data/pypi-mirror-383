import asyncio
import os
from init_provider import setup, dispose
from init_provider_sqlalchemy import Database
from sqlalchemy import text


@setup
def configure() -> None:
    os.environ["DATABASE_ENGINE_URL"] = "sqlite:///example.db"
    os.environ["DATABASE_ENGINE_ASYNC_URL"] = "sqlite+aiosqlite:///example.db"
    os.environ["DATABASE_ENGINE_ECHO"] = "False"
    os.environ["DATABASE_SESSION_EXPIRE_ON_COMMIT"] = "False"


@dispose
def cleanup() -> None:
    os.unlink("example.db")


def sync_test() -> None:
    with Database.session() as session:
        result = session.execute(text("SELECT 1"))
        print(result.scalar())


async def async_test() -> None:
    async with Database.async_session() as session:
        result = await session.execute(text("SELECT 1"))
        print(result.scalar())


async def main() -> None:
    sync_test()
    await async_test()


if __name__ == "__main__":
    asyncio.run(main())
