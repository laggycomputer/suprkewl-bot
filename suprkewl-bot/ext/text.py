# -*- coding: utf-8 -*-

"""
Copyright (C) 2020 Dante "laggycomputer" Dam

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
import os
import random

import aiohttp
import discord
from discord.ext import commands
from PyLyrics import PyLyrics

from .utils import async_executor


class Text(commands.Cog):

    @commands.command(description="Sends text.")
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def text(self, ctx):
        """Don't ask what this does."""

        files = ["bee.txt", "lettuce.txt", "rickroll.txt", "tnt.txt", "uwu.txt"]
        with open(os.path.join("assets", "random-text", random.choice(files), "rb")) as fp:
            await ctx.send(file=discord.File(fp, filename="love_letter.txt"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def stretch(self, ctx, *, text):
        """Make text L O N G E R."""

        ret = "\n".join((" " * a).join(list(text)) for a in [*range(0, 5), *range(5, -1, -1)])
        to_send = f"```\n{ret}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(ret)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(ret.encode("utf-8")), "out.txt")
                await ctx.send("Your output was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def square(self, ctx, radius: int, *, string):
        """Print text in a square."""

        ranges = list(range(1, radius + 1)) + list(range(radius, 0, -1))

        ret = "\n".join((string * c).center(len(radius * string)) for c in ranges)
        to_send = f"```\n{ret}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(ret)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(ret.encode("utf-8")), "out.txt")
                await ctx.send("Your output was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @commands.command(description="Format your arguments like author/song.")
    @commands.cooldown(1, 1.5, commands.BucketType.channel)
    async def lyrics(self, ctx, *, song):
        """Get lyrics for a song. See main help dialog for argument format."""

        author, song = song.split("/")

        author, song = author.strip().title(), song.strip().title()

        @async_executor()
        def get_lyrics(a, s):
            return PyLyrics.getLyrics(a, s)

        try:
            lyrics = await get_lyrics(author, song)
        except ValueError:
            return await ctx.send("Your song is either invalid or missing from the database. Try again.")

        if isinstance(lyrics, bytes):  # This library can be dum-dum
            lyrics = lyrics.decode("utf-8")

        if lyrics is None:
            return await ctx.send("Your song seems to have no lyrics on record.")

        await ctx.paginate_with_embeds(lyrics, prefix="", suffix="")

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def wbrb(self, ctx):
        """We'll Be Right Back"""

        await ctx.send("We'll\nBe\nRight\nBack")

    @commands.command()
    @commands.cooldown(3, 2, commands.BucketType.channel)
    async def dab(self, ctx):
        """ASCII dabs"""

        await ctx.send("<o/\n\\o>")


def setup(bot):
    bot.add_cog(Text())
