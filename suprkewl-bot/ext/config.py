# Not to be confused with the global configuration file, ../config.py.

import aiosqlite
from discord.ext import commands

import config

class Config(commands.Cog):
    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def prefix(self, ctx, subc=None, subcarg=None):
        if subc is None:
            sent = (await ctx.send(":x: This command requires a subcommand!"))
            await ctx.bot.register_response(sent, ctx.message)
            return
        if subc.startswith("get"):
            await self.prefix_get.invoke(ctx)
        elif subc.startswith("set"):
            await self.prefix_set.invoke(ctx)
        else:
            sent = (await ctx.send(":x: You need a subcommand, and have specified an invalid one."))
            await ctx.bot.register_response(sent, ctx.message)

    @prefix.command(name="get")
    async def prefix_get(self, ctx):
        if not await ctx.command.parent.can_run(ctx):
            return
        async with aiosqlite.connect(config.db_path) as db:
            async with db.execute(f"SELECT prefix FROM guilds WHERE id = {ctx.guild.id}") as cur:
                fetched = (await cur.fetchall())

        sent = (await ctx.send(f"The prefix is `{fetched[0][0]}`."))
        await ctx.bot.register_response(sent, ctx.message)

    @prefix.command(name="set", description="Sets your prefix. Limit 10 characters.")
    async def prefix_set(self, ctx, prefix):
        if not await ctx.command.parent.can_run(ctx):
            return
        if len(prefix) <= 10:
            async with aiosqlite.connect(config.db_path) as db:
                query = f"UPDATE guilds SET prefix = '$1' WHERE id = {ctx.guild.id};"
                await db.execute(query, prefix)

            sent = (await ctx.send(":white_check_mark: Updated!"))
        else:
            sent = (await ctx.send(":x: THe prefix must be 10 characters or shorter."))

        await ctx.bot.register_response(sent, ctx.message)

def setup(bot):
    bot.add_cog(Config())
