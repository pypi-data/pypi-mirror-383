<h1><code>init-provider-sqlalchemy</code></h1>

Database provider implemented using [`init-provider`](https://github.com/vduseev/init-provider).

![PyPI - Version](https://img.shields.io/pypi/v/init-provider-sqlalchemy)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/init-provider-sqlalchemy)
![PyPI - Status](https://img.shields.io/pypi/status/init-provider-sqlalchemy)
![PyPI - License](https://img.shields.io/pypi/l/init-provider-sqlalchemy)

Table of Contents

- [Quick start](#quick-start)
- [Installation](#installation)
- [License](#license)

## Quick start

Below is a full runnable example that uses everything in this library.

```python
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
```

## Installation

Using `pip`:

```shell
pip install init-provider-sqlalchemy
```

Using `uv`:

```shell
uv add init-provider-sqlalchemy
```

## License

Licensed under the [Apache-2.0 License](./LICENSE).