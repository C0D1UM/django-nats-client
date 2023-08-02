import asyncio
import json

import jsonpickle
import nats.errors
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import autoreload
from nats.aio.client import Client
from nats.aio.errors import ErrNoServers
from nats.aio.errors import ErrTimeout
from nats.aio.msg import Msg

from ...clients import get_nc_client
from ...handlers import nats_handler
from ...registry import default_registry


class Command(BaseCommand):
    help = "Starts a NATS listener."

    def __init__(self, *args, **kwargs):
        self.nats = Client()
        self.js = None

        super().__init__(*args, **kwargs)

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
        print('** Initializing Loop')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            asyncio.ensure_future(self.nats_coroutine())
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(self.nats.close())
        finally:
            loop.close()

    async def nats_coroutine(self):
        namespace = getattr(settings, 'NATS_NAMESPACE', 'default')
        durable_name = getattr(settings, 'NATS_JETSTREAM_DURABLE_NAME', namespace)
        create_stream = getattr(settings, 'NATS_JETSTREAM_CRATE_STREAM', True)
        stream_config = getattr(settings, 'NATS_JETSTREAM_CONFIG', {})

        try:
            await get_nc_client(self.nats)
            print('** Connected to NATS server')

            if getattr(settings, 'NATS_JETSTREAM_ENABLED', True):
                self.js = self.nats.jetstream()
                print('** Initialized JetStream')
        except (ErrNoServers, ErrTimeout) as e:
            raise e

        if not default_registry.registry:
            print('** No function found!')
            return

        if self.js is not None and create_stream:
            print('** Creating stream')
            stream_config.pop('name', None)
            stream_config.pop('subjects', None)
            await self.js.add_stream(
                name=namespace,
                subjects=[f'{namespace}.js.>'],
                **stream_config,
            )

        async def callback(msg: Msg):
            data = msg.data.decode()
            reply = msg.reply
            func_name = msg.subject
            print(f'Received a message on function `{func_name}`: {data}')
            asyncio.ensure_future(self.handler(func_name, data, reply=reply))

        async def fetch(psub):
            try:
                msgs = await psub.fetch(timeout=1)
                for msg in msgs:
                    data = msg.data.decode()
                    func_name = msg.subject
                    print(f'Received a message on JetStream function `{func_name}`: {data}')
                    asyncio.ensure_future(self.handler(func_name, data))
                    await msg.ack()
            except nats.errors.TimeoutError:
                pass
            asyncio.ensure_future(fetch(psub))

        print('** Listened on:')
        for data in default_registry.registry.values():
            if data['js']:
                full_name = f'{data["namespace"]}.js.{data["name"]}'
                if self.js is None:
                    continue

                full_name_no_dot = full_name.replace('.', '-')
                psub = await self.js.pull_subscribe(
                    full_name,
                    f'{durable_name}-{full_name_no_dot}',
                )
                asyncio.ensure_future(fetch(psub))
            else:
                full_name = f'{data["namespace"]}.{data["name"]}'
                await self.nats.subscribe(full_name, cb=callback)
            print(f'     - {full_name}' + (' (JetStream)' if data['js'] else ''))

    async def handler(self, func_name: str, body, reply=None):
        try:
            data = json.loads(body)
            r = await nats_handler(func_name, data)
        except Exception as e:  # pylint: disable=broad-except
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
            raise e

        if reply:
            await self.nats.publish(reply, json.dumps({'success': True, 'result': r}, cls=DjangoJSONEncoder).encode())
