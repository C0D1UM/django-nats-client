import asyncio
import json

from asgiref.sync import SyncToAsync
from django.conf import settings
from django.core.management import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db import close_old_connections
from django.utils import autoreload
from nats.aio.client import Client
from nats.aio.client import Msg
from nats.aio.errors import ErrNoServers
from nats.aio.errors import ErrTimeout

from nats_client.registry import default_registry


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


class Command(BaseCommand):
    help = "Starts a NATS listener."

    nats = Client()

    def add_arguments(self, parser):
        parser.add_argument(
            "--reload",
            action="store_true",
            dest="reload",
            help="Enable autoreload in development environment.",
        )

    def handle(self, *args, **options):
        reload = options.get('reload', False)
        print('** Starting NATS listener' + (' with reload enabled' if reload else ''))
        if reload:
            autoreload.run_with_reloader(self.inner_run, *args, **options)
        else:
            self.inner_run(*args, **options)

    def inner_run(self, *args, **options):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print('** Initializing Loop')
        try:
            asyncio.ensure_future(self.nats_coroutine())
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(self.clean())
        finally:
            loop.close()

    async def nats_coroutine(self):
        try:
            await self.nats.connect(**settings.NATS_OPTIONS)
            print('** Connected to NATS server')
            if not default_registry.registry:
                print('** No function found!')
            else:
                print('** Listened on:')
                for func_name in default_registry.registry.keys():
                    print('     - ', func_name)
        except (ErrNoServers, ErrTimeout) as e:
            raise e

        async def callback(msg: Msg):
            data = msg.data.decode()
            reply = msg.reply
            print(f'Received a message: {data}')
            await self.nats_handler(data, reply=reply)

        subject = getattr(settings, 'NATS_LISTENING_SUBJECT', 'default')
        await self.nats.subscribe(subject, cb=callback)

    async def clean(self):
        await self.nats.close()

    async def nats_handler(self, body, reply=None):
        data = json.loads(body)

        name = data['name']
        args = data['args']
        kwargs = data['kwargs']

        func = default_registry.registry.get(name)
        if func is None:
            print(f'No function found for "{name}"')
            return

        if not asyncio.iscoroutinefunction(func):
            func = database_sync_to_async(func)
        r = await func(*args, **kwargs)

        if reply:
            await self.nats.publish(reply, json.dumps({'result': r}, cls=DjangoJSONEncoder).encode())
