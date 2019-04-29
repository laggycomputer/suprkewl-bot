# -*- coding: utf-8 -*-

"""
The MIT License (MIT)
Copyright (c) 2018-2019 laggycomputer
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import aioredis
import config

class Redis:
    def __init__(self):
        self.connection = None

    async def connect(self):
        if self.connection is not None and not self.connection.closed:
            return

        if any(config.redis_password):
            passwd = config.redis_password
        else:
            passwd = None
        self.connection = await aioredis.create_connection(
            (config.redis_host, config.redis_port),
            password=passwd
        )

    async def reconnect(self):
        self.connection = await aioredis.create_connection(
            self.connection.address
        )

    def disconnect(self):
        if self.connection is None:
            return

        self.connection.close()

    async def rpush(self, key, *values):
        return await self.execute("RPUSH", key, *values)

    async def lrange(self, key, start, end):
        return await self.execute("LRANGE", key, start, end)

    async def expire(self, key, seconds):
        return await self.execute("EXPIRE", key, seconds)

    async def delete(self, *keys):
        return await self.execute("DEL", *keys)

    async def exists(self, *values):
        return await self.execute("EXISTS", *values) == len(values)

    async def get(self, key):
        return await self.execute("GET", key)

    async def execute(self, command, *args):
        value = await self.connection.execute(command, *args)

        return self.decode_value(value)

    def decode_value(self, value):
        if type(value) is list:
            return [self.decode_value(v) for v in value]
        elif type(value) is bytes:
            return value.decode()

        return value
