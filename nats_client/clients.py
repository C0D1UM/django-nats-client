__all__ = ['request', 'request_sync', 'publish', 'publish_sync', 'js_publish', 'js_publish_sync']

import asyncio
import functools
import json

import jsonpickle
from django.conf import settings
from nats.aio.client import Client

from .exceptions import NatsClientException
from .types import ResponseType
from .utils import parse_arguments

DEFAULT_REQUEST_TIMEOUT = 1


async def get_nc_client(nc: Client = None):
    if nc is None:
        nc = Client()

    server = getattr(settings, 'NATS_SERVER', None)
    servers = [server] if server else getattr(settings, 'NATS_SERVERS', [])
    options = getattr(settings, 'NATS_OPTIONS', {})

    await nc.connect(servers=servers, **options)
    return nc


async def request(
        namespace: str, method_name: str, *args, _timeout: float = None, _raw=False, **kwargs
) -> ResponseType:
    payload = parse_arguments(args, kwargs)

    nc = await get_nc_client()

    timeout = _timeout or getattr(settings, 'NATS_REQUEST_TIMEOUT', DEFAULT_REQUEST_TIMEOUT)
    try:
        response = await nc.request(f'{namespace}.{method_name}', payload, timeout=timeout)
    finally:
        await nc.close()

    data = response.data.decode()
    parsed = json.loads(data)

    if _raw:
        parsed.pop('pickled_exc', None)
        return parsed

    if not parsed['success']:
        try:
            exc = jsonpickle.decode(parsed['pickled_exc'])
        except TypeError:
            exc = NatsClientException(parsed['error'] + ': ' + parsed['message'])

        raise exc

    return parsed['result']


def request_sync(*args, **kwargs):
    return asyncio.run(request(*args, **kwargs))


async def publish(namespace: str, method_name: str, *args, _js=False, **kwargs) -> None:
    payload = parse_arguments(args, kwargs)

    nc = await get_nc_client()

    try:
        if _js:
            js = nc.jetstream()
            await js.publish(f'{namespace}.js.{method_name}', payload)
        else:
            await nc.publish(f'{namespace}.{method_name}', payload)
    finally:
        await nc.close()


def publish_sync(*args, **kwargs):
    return asyncio.run(publish(*args, **kwargs))


js_publish = functools.partial(publish, _js=True)
js_publish_sync = functools.partial(publish_sync, _js=True)
