import asyncio
import json

import jsonpickle
from django.conf import settings
from nats.aio.client import Client

from .types import ResponseType
from .utils import parse_arguments

DEFAULT_REQUEST_TIMEOUT = 1


async def request_async(
    subject_name: str, method_name: str, *args, _timeout: float = None, _raw=False, **kwargs
) -> ResponseType:
    payload = parse_arguments(method_name, args, kwargs)

    nc = Client()
    await nc.connect(**settings.NATS_OPTIONS)

    timeout = _timeout or getattr(settings, 'NATS_REQUEST_TIMEOUT', DEFAULT_REQUEST_TIMEOUT)
    try:
        response = await nc.request(subject_name, payload, timeout=timeout)
    finally:
        await nc.close()

    data = response.data.decode()
    parsed = json.loads(data)

    if _raw:
        parsed.pop('pickled_exc', None)
        return parsed

    if not parsed['success']:
        exc = jsonpickle.decode(parsed['pickled_exc'])
        raise exc

    return parsed['result']


async def send_async(subject_name: str, method_name: str, *args, **kwargs) -> None:
    payload = parse_arguments(method_name, args, kwargs)

    nc = Client()
    await nc.connect(**settings.NATS_OPTIONS)

    try:
        await nc.publish(subject_name, payload)
    finally:
        await nc.close()


def request(*args, **kwargs):
    return asyncio.run(request_async(*args, **kwargs))


def send(*args, **kwargs):
    return asyncio.run(send_async(*args, **kwargs))
