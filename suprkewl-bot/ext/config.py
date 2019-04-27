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

# Not to be confused with the global configuration file, ../config.py.

import aiosqlite
from discord.ext import commands

import config

class Config(commands.Cog):
    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def prefix(self, ctx, subc=None, subcarg=None):
        """Perform operations on the guild custom prefix."""

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
        """Query the guild custom prefix."""

        if not await ctx.command.parent.can_run(ctx):
            return
        async with aiosqlite.connect(config.db_path) as db:
            async with db.execute(f"SELECT prefix FROM guilds WHERE id = {ctx.guild.id}") as cur:
                fetched = (await cur.fetchall())

        sent = (await ctx.send(f"The prefix is `{fetched[0][0]}`."))
        await ctx.bot.register_response(sent, ctx.message)

    @prefix.command(name="set", description="Sets your prefix. Limit 10 characters.")
    async def prefix_set(self, ctx, prefix):
        """Set the custom guild prefix."""

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
