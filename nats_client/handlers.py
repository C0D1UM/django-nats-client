import asyncio

from .registry import default_registry
from .utils import database_sync_to_async


async def nats_handler(key: str, data):
    args = data.get('args', [])
    kwargs = data.get('kwargs', {})

    data = default_registry.registry.get(key)
    if data is None:
        raise ValueError(f'No function found for `{key}`')

    func = data['func']
    if not asyncio.iscoroutinefunction(func):
        func = database_sync_to_async(func)

    return await func(*args, **kwargs)
