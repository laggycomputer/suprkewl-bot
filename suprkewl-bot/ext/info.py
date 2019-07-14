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
import typing
from urllib.parse import quote as urlquote

import discord
from discord.ext import commands

from .utils import permissions_converter, escape_codeblocks, format_json


class Info(commands.Cog):

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.group(
        description="Gives the data under a message, channel, or member in a JSON format, as received from the"
                    " Discord API."
    )
    async def raw(self, ctx):
        """Returns a dict version of some objects."""

        if ctx.invoked_subcommand is None:
            await ctx.send(":x: Please provide a valid subcommand!")

    @raw.command(name="message", aliases=["msg"])
    async def raw_message(self, ctx, *, message: discord.Message):
        """Return a message as a dict."""

        raw = await ctx.bot.http.get_message(message.channel.id, message.id)

        try:
            await ctx.send(f"```json\n{escape_codeblocks(format_json(raw))}```")
        except discord.HTTPException:
            fp = io.BytesIO(format_json(raw))
            fp = discord.File(fp, "raw.txt")

            await ctx.send("Your output was placed in the attached file:", file=fp)

    @raw.command(name="member", aliases=["user"])
    async def raw_member(self, ctx, *, user: discord.User = None):
        """Return a member as a dict."""
        if user is None:
            user = ctx.author

        route = discord.http.Route("GET", f"/users/{user.id}")
        raw = await ctx.bot.http.request(route)

        await ctx.send(f"```json\n{escape_codeblocks(format_json(raw))}```")

    @raw.command(name="channel")
    async def raw_channel(
            self, ctx, *, channel: typing.Union[
                discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel
            ] = None
    ):
        """Return a channel as a dict."""

        if channel is None:
            channel = ctx.channel

        route = discord.http.Route("GET", f"/channels/{channel.id}")
        try:
            raw = await ctx.bot.http.request(route)
        except discord.Forbidden:
            return await ctx.send(":x: I can't see info on that channel!")

        await ctx.send(f"```json\n{escape_codeblocks(format_json(raw))}```")

    # Thanks to Takaru, PendragonLore/TakaruBot
    @commands.command()
    async def pypi(self, ctx, *, name):
        data = await (await ctx.bot.http2.get(f"https://pypi.org/pypi/{urlquote(name, safe='')}/json")).json()

        embed = discord.Embed(
            title=data["info"]["name"],
            url=data["info"]["package_url"],
            color=discord.Color.dark_blue()
        )
        embed.set_author(name=data["info"]["author"])
        embed.description = data["info"]["summary"] or "No short description."
        embed.add_field(
            name="Classifiers",
            value="\n".join(data["info"]["classifiers"]) or "No classifiers.")
        embed.set_footer(
            text=f"Latest: {data['info']['version']} |"
                 f" Keywords: {data['info']['keywords'] or 'No keywords.'}"
        )
        fp = discord.File("assets/pypi.png", "image.png")
        embed.set_thumbnail(
            url="attachment://image.png"
        )

        await ctx.send(embed=embed, file=fp)


def setup(bot):
    bot.add_cog(Info())
