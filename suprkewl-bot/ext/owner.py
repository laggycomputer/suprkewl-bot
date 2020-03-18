# -*- coding: utf-8 -*-

"""
Copyright (C) 2019 laggycomputer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import io
import sqlite3
import traceback
import typing

import aiohttp
import aioredis
import discord
from discord.ext import commands
from jishaku.codeblocks import codeblock_converter

from .utils import TabularData


class Owner(commands.Cog):

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    @commands.command(aliases=["procm", "procmanager", "supervisor", "supervisorctl"])
    async def proc(self, ctx, *, args):
        """Check supervisorctl on the shell."""

        conv = codeblock_converter(f"/usr/local/bin/supervisorctl {args}")
        await ctx.invoke(ctx.bot.get_command("jsk sh"), argument=conv)

    @commands.command(aliases=["redis-cli"])
    async def redis(self, ctx, *args):
        """Execute Redis code"""

        try:
            resp = await ctx.bot.redis.execute(*args)
        except aioredis.RedisError as e:
            file = io.StringIO()
            traceback.print_exception(type(e), e, e.__traceback__, file=file)
            file.seek(0)
            tb = file.read()
            return await ctx.paginate_with_embeds(tb, without_annotation=True, prefix="```py\n")

        await ctx.paginate_with_embeds(resp, without_annotation=True)

    @commands.command(name="del")
    async def deletemsg(self, ctx, message: discord.Message):
        """Delete a specific message."""

        try:
            await message.delete()
            await ctx.send(":white_check_mark:")
        except discord.Forbidden:
            await ctx.send(":x: I do not have permission to delete that message.")

    @commands.command()
    async def statustoggle(self, ctx):
        """Enable or disable status change."""

        if ctx.bot.change_status:
            resp = "Disabling status change."
        else:
            resp = "Enabling status change."
        ctx.bot.change_status = not ctx.bot.change_status

        await ctx.send(resp)

    @commands.command()
    async def statuschange(self, ctx, *, status):
        """Change playing status of the bot."""

        await ctx.bot.change_presence(activity=discord.Game(name=status), status=discord.Status.idle)
        await ctx.send(f":white_check_mark: Changed to `{status}`")

    @commands.command()
    async def log(self, ctx):
        """Show the log file."""

        conv = await codeblock_converter("cat suprkewl.log")
        await ctx.invoke(ctx.bot.get_command("jsk sh"), argument=conv)

    @commands.command()
    async def noprefix(self, ctx, *, arg: bool = None):
        """Toggle owner-only no prefix privileges."""

        if arg is not None:
            ctx.bot.owner_no_prefix = not arg

        ret = "dis" if ctx.bot.owner_no_prefix else "en"

        if arg is None:
            await ctx.send(f"Owner-only no prefix is currently **{ret}abled**.")
        else:
            await ctx.send(f"Owner-only no prefix is now **{ret}abled**.")

    @commands.command()
    async def songlist(self, ctx):
        """Bored? List every visible Spotiy status with this command."""

        seen_ids = []
        msgs = []
        for m in ctx.bot.get_all_members():
            if isinstance(m.activity, discord.Spotify):
                if m.id not in seen_ids:
                    seen_ids.append(m.id)
                    msgs.append("Artist(s): " + ", ".join(m.activity.artists) + " | Name: " + m.activity.title
                                + " | Username: " + str(m))

        ret = "\n".join(msgs)
        try:
            hastebin_url = await ctx.bot.post_to_hastebin(ret)
            await ctx.send(hastebin_url)
        except (aiohttp.ContentTypeError, AssertionError):
            fp = discord.File(io.BytesIO(ret.encode("utf-8")), "out.txt")
            await ctx.send(file=fp)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(change_nickname=True)
    async def nick(self, ctx, *, name):
        """Change my nickname on this server."""

        await ctx.guild.me.edit(nick=name)
        await ctx.send(":ok_hand:")

    @commands.command(aliases=["sup"])
    async def suppress(self, ctx, *, msg: discord.Message):
        """Suppress embeds on a message. Either the message must be owned by the bot or the bot has Manage Messages in
        that channel."""

        try:
            await msg.edit(suppress=True)
            return await ctx.send(":white_check_mark:")
        except discord.HTTPException:
            await ctx.send(":x: Permission denied or guild/channel/group/message was deleted.")

    @commands.command(aliases=["usup"])
    async def unsuppress(self, ctx, *, msg: discord.Message):
        """Unsuppress embeds on a message. Either the message must be owned by the bot or the bot has Manage Messages in
        that channel."""

        try:
            await msg.edit(suppress=False)
            return await ctx.send(":ok_hand:")
        except discord.HTTPException:
            await ctx.send(":bangbang: Permission denied or guild/channel/group/message was deleted.")

    @commands.command()
    async def sql(self, ctx, *, query):
        if query.startswith("```") and query.endswith("```"):
            query = "\n".join(query.split("\n")[1:])
        else:
            query.strip("` \n")

        try:
            cur = await ctx.bot.db.execute(query)
        except sqlite3.DatabaseError:
            return await ctx.send(f'```py\n{traceback.format_exc()}\n```')

        await ctx.bot.db.commit()
        results = await cur.fetchall()

        if not len(results):
            return await ctx.send(":white_check_mark:")

        table = TabularData()
        table.set_columns([c[0] for c in cur.description])
        table.add_rows(results)
        ret = table.render()
        to_send = f"```{ret}```"

        if len(to_send) > 2000:
            await ctx.send("Too many results! " + await ctx.bot.post_to_hastebin(ret))
        else:
            await ctx.send(to_send)

    @commands.command(aliases=["blist"])
    async def blacklist(self, ctx, *, target: typing.Union[discord.Member, discord.User]):
        """Blacklist a user from using this bot."""

        if await ctx.bot.is_owner(target):
            return await ctx.send("You cannot blacklist an owner.")

        await ctx.bot.db.execute(
            "INSERT INTO blacklist (user_id, mod_id) VALUES (?, ?) ON CONFLICT (mod_id) DO UPDATE SET "
            "mod_id = ? WHERE user_id == ?;",
            (target.id, ctx.author.id, ctx.author.id, target.id)
        )
        await ctx.bot.db.commit()
        await ctx.send(f"{target} was successfully blacklisted.")

    @commands.command(aliases=["ublist"])
    async def unblacklist(self, ctx, *, target: typing.Union[discord.Member, discord.User]):
        """Unblacklist a user from using this bot."""

        await ctx.bot.db.execute("DELETE FROM blacklist WHERE user_id == ?;", (target.id,))
        await ctx.bot.db.commit()
        await ctx.send(f"{target} was successfully removed from the blacklist.")


def setup(bot):
    bot.add_cog(Owner())
