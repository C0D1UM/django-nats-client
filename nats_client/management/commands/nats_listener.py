import asyncio
import json
import traceback

import jsonpickle
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import autoreload
from nats.aio.client import Client
from nats.aio.client import Msg
from nats.aio.errors import ErrNoServers
from nats.aio.errors import ErrTimeout

from ...registry import default_registry
from ...handlers import nats_handler


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
        subject = getattr(settings, 'NATS_LISTENING_SUBJECT', 'default')

        try:
            await self.nats.connect(**settings.NATS_OPTIONS)
            print('** Connected to NATS server')
            if not default_registry.registry:
                print('** No function found!')
            else:
                print('** Listened on:')
                for func_name in default_registry.registry.keys():
                    print(f'     - {subject}.{func_name}')
        except (ErrNoServers, ErrTimeout) as e:
            raise e

        async def callback(msg: Msg):
            data = msg.data.decode()
            reply = msg.reply
            func_name = msg.subject[len(subject) + 1:]
            print(f'Received a message on function `{func_name}`: {data}')
            await self.handler(func_name, data, reply=reply)

        await self.nats.subscribe(f'{subject}.>', cb=callback)

    async def clean(self):
        await self.nats.drain()

    async def handler(self, func_name: str, body, reply=None):
        data = json.loads(body)

        try:
            r = await nats_handler(func_name, data)
        except Exception as e:  # pylint: disable=broad-except
            traceback.print_exc()
            if reply:
                if isinstance(e, ValidationError):
                    message = e.message_dict
                else:
                    message = str(e)
                    try:
                        message = json.loads(message)
                    except json.JSONDecodeError:
                        pass

                await self.nats.publish(
                    reply,
                    json.dumps({
                        'success': False,
                        'error': e.__class__.__name__,
                        'message': message,
                        'pickled_exc': jsonpickle.encode(e),
                    }).encode()
                )
            return

        if reply:
            await self.nats.publish(reply, json.dumps({'success': True, 'result': r}, cls=DjangoJSONEncoder).encode())
