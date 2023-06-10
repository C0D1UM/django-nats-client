import json

from asgiref.sync import SyncToAsync
from django.core.serializers.json import DjangoJSONEncoder
from django.db import close_old_connections


def parse_arguments(args: tuple, kwargs: dict) -> bytes:
    msg = {
        'args': args,
        'kwargs': kwargs,
    }
    return json.dumps(msg, cls=DjangoJSONEncoder).encode()


# pylint: disable=invalid-name
class DatabaseSyncToAsync(SyncToAsync):
    """
    SyncToAsync version that cleans up old database connections when it exits.
    """

    def thread_handler(self, loop, *args, **kwargs):
        close_old_connections()
        try:
            return super().thread_handler(loop, *args, **kwargs)
        finally:
            close_old_connections()


# The class is TitleCased, but we want to encourage use as a callable/decorator
database_sync_to_async = DatabaseSyncToAsync
