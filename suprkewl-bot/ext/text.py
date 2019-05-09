# -*- coding: utf-8 -*-

"""
Copyright (C) 2019 laggycomputer

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

import io
import os
import random
import typing

import discord
from discord.ext import commands

from .utils import escape_codeblocks, format_json


class Text(commands.Cog):

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.group(
        description="Gives the data under a message, channel, or member in a JSON format, as recieved from the Discord API."
    )
    async def raw(self, ctx):
        """Returns a dict version of some objects."""

        if ctx.invoked_subcommand is None:
            sent = (await ctx.send(":x: Please give a subcommand!"))
            await ctx.bot.register_response(sent, ctx.message)

    @raw.command(name="message", aliases=["msg"])
    async def raw_message(self, ctx, message: discord.Message):
        """Return a message as a dict."""

        raw = await ctx.bot.http.get_message(message.channel.id, message.id)

        try:
            sent = (await ctx.send(f"```json\n{escape_codeblocks(format_json(raw))}```"))
            await ctx.bot.register_response(sent, ctx.message)
        except discord.HTTPException:
            raw_string = "```json\n{}```".format(escape_codeblocks(format_json(raw)))
            half = int(len(raw_string) / 2)
            raw_string = [raw_string[0:half] + "```", "```json\n" + raw_string[half:len(raw_string)]]
            await ctx.send(raw_string[0])
            await ctx.send(raw_string[1])

    @raw.command(name="member", aliases=["user"])
    async def raw_member(self, ctx, user: discord.User = None):
        """Return a member as a dict."""
        if user is None:
            user = ctx.author

        route = discord.http.Route("GET", f"/users/{user.id}")
        raw = await ctx.bot.http.request(route)

        sent = (await ctx.send(f"```json\n{escape_codeblocks(format_json(raw))}```"))
        await ctx.bot.register_response(sent, ctx.message)

    @raw.command(name="channel")
    async def raw_channel(
            self, ctx, channel: typing.Union[
                discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel
            ]=None
    ):
        """Return a channel as a dict."""

        if channel is None:
            channel = ctx.channel

        route = discord.http.Route("GET", f"/channels/{channel.id}")
        try:
            raw = await ctx.bot.http.request(route)
        except discord.Forbidden:
            sent = (await ctx.send(":x: I can't see info on that channel!"))
            await ctx.bot.register_response(sent, ctx.message)

            return

        sent = (await ctx.send(f"```json\n{escape_codeblocks(format_json(raw))}```"))
        await ctx.bot.register_response(sent, ctx.message)

    @commands.command(description="Sends text. Strict cooldown.")
    @commands.cooldown(1, 120, commands.BucketType.channel)
    async def text(self, ctx):
        """Don't ask what this does."""

        files = ["bee.txt", "uwu.txt"]
        with open(os.getcwd() + f"..\\..\\assets\\{random.choice(files)}", "rb") as fp:
            sent = (await ctx.send(file=discord.File(fp, filename="love_letter.txt")))
        await ctx.bot.register_response(sent, ctx.message)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def stretch(self, ctx, *, text):
        """Make text L O N G E R."""

        ret = "\n".join((" " * a).join(list(text)) for a in [*range(0, 5), *range(5, -1, -1)])

        if len(ret) > 2000:
            fp = io.BytesIO(ret.encode("utf-8"))

            sent = (await ctx.send(
                content=":white_check_mark: Your output was longer than 2000 characters and was therefore placed in this file:",
                file=discord.File(fp, "stretch.txt")
            ))
        else:
            sent = (await ctx.send("```\n%s\n```" % ret))
            await ctx.bot.register_response(sent, ctx.message)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def square(self, ctx, radius: int, *, string):
        """Print text in a square."""

        ranges = list(range(1, radius + 1)) + list(range(radius, 0, -1))

        ret = "\n".join((string * c).center(len(radius * string)) for c in ranges)

        if len(ret) > 2000:
            fp = io.BytesIO(ret.encode("utf-8"))

            sent = (await ctx.send(
                content=":white_check_mark: Your output was longer than 2000 characters and was therefore placed in this file:",
                file=discord.File(fp, "square.txt")
            ))
            await ctx.bot.register_response(sent, ctx.message)
        else:
            sent = (await ctx.send("```\n%s\n```" % ret))
            await ctx.bot.register_response(sent, ctx.message)


def setup(bot):
    bot.add_cog(Text())
