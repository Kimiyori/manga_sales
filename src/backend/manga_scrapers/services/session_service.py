from typing import Any


async def session_factory(session: Any, *args: Any, **kwargs: Any) -> Any:
    async with session(*args, **kwargs) as obj:
        yield obj
