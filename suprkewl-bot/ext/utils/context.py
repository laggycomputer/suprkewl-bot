from discord.ext import commands


class Context(commands.Context):
    async def register_response(self, msg):
        await self.bot.register_response(msg, self.message)
