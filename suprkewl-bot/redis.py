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

    async def execute(self, command, *args):
        value = await self.connection.execute(command, *args)

        return self.decode_value(value)

    def decode_value(self, value):
        if type(value) is list:
            return [self.decode_value(v) for v in value]
        elif type(value) is bytes:
            return value.decode()

        return value
