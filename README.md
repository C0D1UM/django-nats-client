# Django NATS

[![GitHub](https://img.shields.io/github/license/C0D1UM/django-nats)](https://github.com/C0D1UM/django-nats/blob/main/LICENSE)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/C0D1UM/django-nats/CI)](https://github.com/C0D1UM/django-nats/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/C0D1UM/django-nats/branch/main/graph/badge.svg?token=PN19DJ3SDF)](https://codecov.io/gh/C0D1UM/django-nats)
[![PyPI](https://img.shields.io/pypi/v/django-nats)](https://pypi.org/project/django-nats/)  
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-nats)](https://github.com/C0D1UM/django-nats)
[![Django Version](https://img.shields.io/badge/django-3.1%20%7C%203.2%20%7C%204.0-blue)](https://github.com/C0D1UM/django-nats)

## Features

- Wrapper of NATS's [nats-py](https://github.com/nats-io/nats.py)
- Django management command to listen for incoming NATS messages
- Automatically serialize/deserialize message from/to JSON format
- Easy-to-call method for sending NATS messages

## Installation

```bash
pip install django-nats
```

## Setup

1. Add `django_nats` into `INSTALLED_APPS`

   ```python
   # settings.py

   INSTALLED_APPS = [
       ...
       'django_nats',
   ]
   ```

3. Put NATS connection configuration in settings

   ```python
   # settings.py

   NATS_OPTIONS = {
       'servers': ['nats://localhost:4222'],
       'max_reconnect_attempts': 2,
       'connect_timeout': 1,
       ...
   }
   NATS_SUBJECT_HANDLERS = ['default']
   ```

## Usage

### Listen for messages

1. Create a new callback method in `[app_dir]/nats_callback.py` and register

   ```python
   # common/nats_callback.py

   from django_nats import register_callback

   @register_callback
   def get_year_from_date(date: str):
       return date.year

   # custom method name
   @register_callback('get_current_time')
   def current_time():
       return datetime.datetime.now().strftime('%H:%M')
   ```
   
2. Run listener management command

   ```bash
   python manage.py nats_listener
   ```

### Sending message

```python
from django_nats import nats_client

arg = 'some arg'
nats_client.send(
    'subject_name',
    'method_name',
    arg,
    keyword_arg=1,
    another_keyword_arg=2,
)
```

Examples

```python
from django_nats import nats_client

year = nats_client.send('default', 'get_year_from_date', datetime.date(2022, 1, 1))  # 2022
current_time = nats_client.send('default', 'get_current_time')  # 12:11
```

## Settings

| Key                     | Required | Default | Description                                    |
|-------------------------|----------|---------|------------------------------------------------|
| `NATS_OPTIONS`          | Yes      |         | Configuration to be passed in `nats.connect()` |
| `NATS_SUBJECT_HANDLERS` | No       | []      | List of subject name to listen                 |

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
