# Pikados

Pikados is a wrapper around Pika, providing a more asyncio-compatible syntax
for channels and connections.
An effort is made to keep the syntax close to Pika, but simply provide async
functions as many developers expect.

## Usage

Pikados still uses Pika's `AsyncioConnection` internally.
Pika is very clever with its usage of callbacks,
allowing its implementation to start a connection with its' `#!python __init__` implementation.

```python
import asyncio

from pika import URLParameters
from pikados.connection import connect, AsyncConnection

url = URLParameters("amqp://guest:guest@localhost:5672/%2F")


async def main():
    con: AsyncConnection = await connect(url, 'MyApp')

```

## Docs

Please install using `requirements-docs.txt` and run using `mkdocs serve`.