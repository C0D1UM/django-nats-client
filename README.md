# Django NATS Client

[![GitHub](https://img.shields.io/github/license/C0D1UM/django-nats-client)](https://github.com/C0D1UM/django-nats-client/blob/main/LICENSE)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/C0D1UM/django-nats-client/ci.yml?branch=main)](https://github.com/C0D1UM/django-nats-client/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/C0D1UM/django-nats-client/branch/main/graph/badge.svg?token=PN19DJ3SDF)](https://codecov.io/gh/C0D1UM/django-nats-client)
[![PyPI](https://img.shields.io/pypi/v/django-nats-client)](https://pypi.org/project/django-nats-client/)  
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-nats-client)](https://github.com/C0D1UM/django-nats-client)

## Important Notes

> 🚨 The latest major version of this package, `v0.4.0`, has a numerous breaking changes.
> Please review its [release note](https://github.com/C0D1UM/django-nats-client/releases/tag/v0.4.0).

## Features

- Wrapper of NATS's [nats-py](https://github.com/nats-io/nats.py)
- Django management command to listen for incoming NATS messages
- Automatically serialize/deserialize message from/to JSON format
- Easy-to-call method for publishing NATS messages
- Support NATS JetStream pull subscription

## Installation

```bash
pip install django-nats-client
```

## Setup

1. Add `nats_client` into `INSTALLED_APPS`

   ```python
   # settings.py

   INSTALLED_APPS = [
       ...
       'nats_client',
   ]
   ```

1. Put NATS connection configuration in settings

   ```python
   # settings.py

   NATS_SERVERS = 'nats://localhost:4222'
   NATS_NAMESPACE = 'foo'
   ```

## Usage

### Listen for messages

1. Create a new callback method and register

   ```python
   # common/nats.py

   import nats_client
   
   @nats_client.register
   def new_message(message: str):
       print(message)

   @nats_client.register
   def get_year_from_date(date: str):
       return date.year

   # custom name
   @nats_client.register('get_current_time')
   def current_time():
       return datetime.datetime.now().strftime('%H:%M')

   # without decorator
   def current_time():
       return datetime.datetime.now().strftime('%H:%M')
   nats_client.register('get_current_time', current_time)
   
   # JetStream
   @nats_client.register(js=True)
   def new_message(message: str):
       print(message)
   
   # JetStream from other namespace
   @nats_client.register(namespace='bar', js=True)
   def new_message_from_bar(message: str):
       print(message)
   ```

1. Import previously file in `ready` method of your `apps.py`

   ```python
   # common/apps.py

   class CommonConfig(AppConfig):
       ...

       def ready(self):
           import common.nats
   ```

1. Run listener management command

   ```bash
   python manage.py nats_listener

   # or with autoreload enabled (suite for development)
   python manage.py nats_listener --reload
   ```

### Publishing message

```python
import nats_client

arg = 'some arg'
await nats_client.publish(
    'subject_name',
    'method_name',
    arg,
    keyword_arg=1,
    another_keyword_arg=2,
)
```

Examples

```python
import nats_client

await nats_client.publish('default', 'new_message', 'Hello, world!')
await nats_client.publish('default', 'project_created', 1, name='ACME')

# JetStream
await nats_client.publish('default', 'new_message', 'Hello, world!', _js=True)
await nats_client.js_publish('default', 'new_message', 'Hello, world!')
```

### Request-Reply

```python
import nats_client

arg = 'some arg'
await nats_client.request(
    'subject_name',
    'method_name',
    arg,
    keyword_arg=1,
    another_keyword_arg=2,
)
```

Examples

```python
import nats_client

year = await nats_client.request('default', 'get_year_from_date', datetime.date(2022, 1, 1))  # 2022
current_time = await nats_client.request('default', 'get_current_time')  # 12:11
```

## Settings

| Key                            | Type        | Required                      | Default                   | Description                                                       |
|--------------------------------|-------------|-------------------------------|---------------------------|-------------------------------------------------------------------|
| `NATS_SERVER`                  | `str`       | Required if no `NATS_SERVERS` |                           | NATS server's host                                                |
| `NATS_SERVERS`                 | `list[str]` | Required if no `NATS_SERVER`  |                           | NATS server's hosts (for NATS cluster)                            |
| `NATS_NAMESPACE`               | `str`       | No                            | `'default'`               | Main namespace using for prefixing subject, stream name, and etc. |
| `NATS_REQUEST_TIMEOUT`         | `int`       | No                            | `1`                       | Timeout when using `request()` (in seconds)                       |
| `NATS_OPTIONS`                 | `dict`      | No                            | `{}`                      | Other configuration to be passed in `nats.connect()`              |
| `NATS_JETSTREAM_ENABLED`       | `bool`      | No                            | `True`                    | Enable JetStream                                                  |
| `NATS_JETSTREAM_DURABLE_NAME`  | `str`       | No                            | `settings.NATS_NAMESPACE` | Durable name which is unique across all subscriptions             |
| `NATS_JETSTREAM_CREATE_STREAM` | `bool`      | No                            | `True`                    | Automatically create stream named in `NATS_NAMESPACE`             |
| `NATS_JETSTREAM_CONFIG`        | `dict`      | No                            | `{}`                      | Extra configuration for JetStream streams                         |

## Development

### Requirements

- Docker
- Python
- Poetry

### Linting

```bash
make lint
```

### Testing

```bash
make test
```

### Fix Formatting

```bash
make yapf
```
