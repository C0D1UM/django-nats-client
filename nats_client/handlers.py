import asyncio

from .registry import default_registry
from .utils import database_sync_to_async


async def nats_handler(data):
    name = data['name']
    args = data['args']
    kwargs = data['kwargs']

    func = default_registry.registry.get(name)
    if func is None:
        raise ValueError(f'No function found for "{name}"')

    if not asyncio.iscoroutinefunction(func):
        func = database_sync_to_async(func)

    return await func(*args, **kwargs)
