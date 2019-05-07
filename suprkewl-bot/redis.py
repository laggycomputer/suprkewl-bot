# -*- coding: utf-8 -*-

"""
Copyright (C) 2019  laggycomputer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
