from discord.ext import commands


class Context(commands.Context):
    async def register_response(self, msg):
        await self.bot.register_response(msg, self.message)

    async def send(self, *args, **kwargs):
        try:
            register = kwargs.pop("register_response")
        except KeyError:
            register = True

        sent = await super().send(
            *args, **kwargs
        )

        if register:
            await self.register_response(sent)
