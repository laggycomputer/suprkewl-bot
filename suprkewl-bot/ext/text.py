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

import discord
from discord.ext import commands
from PyLyrics import PyLyrics

from .utils import async_executor


class Text(commands.Cog):

    @commands.command(description="Sends text.")
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def text(self, ctx):
        """Don't ask what this does."""

        files = ["bee.txt", "lettuce.txt", "rickroll.txt", "uwu.txt"]
        with open(os.getcwd() + f"/../assets/{random.choice(files)}", "rb") as fp:
            await ctx.send(file=discord.File(fp, filename="love_letter.txt"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def stretch(self, ctx, *, text):
        """Make text L O N G E R."""

        ret = "\n".join((" " * a).join(list(text)) for a in [*range(0, 5), *range(5, -1, -1)])

        if len(ret) > 2000:
            fp = io.BytesIO(ret.encode("utf-8"))

            await ctx.send(
                ":white_check_mark: Your output was longer than 2000 characters and was therefore placed in this"
                " file:",
                file=discord.File(fp, "stretch.txt")
            )
        else:
            await ctx.send("```\n%s\n```" % ret)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def square(self, ctx, radius: int, *, string):
        """Print text in a square."""

        ranges = list(range(1, radius + 1)) + list(range(radius, 0, -1))

        ret = "\n".join((string * c).center(len(radius * string)) for c in ranges)

        if len(ret) > 2000:
            fp = io.BytesIO(ret.encode("utf-8"))

            await ctx.send(
                ":white_check_mark: Your output was longer than 2000 characters and was therefore placed in this"
                " file:",
                file=discord.File(fp, "square.txt")
            )
        else:
            await ctx.send("```\n%s\n```" % ret)

    @commands.command(description="Format your arguments like author/song.")
    @commands.cooldown(1, 1.5, commands.BucketType.channel)
    async def lyrics(self, ctx, *, song):
        """Get lyrics for a song. See main help dialog for argument format."""

        author, song = song.split("/")

        author, song = author.strip().title(), song.strip().title()

        @async_executor()
        def get_lyrics(a, s):
            PyLyrics.getLyrics(a, s)

        try:
            lyrics = await get_lyrics(author, song)
        except ValueError:
            return await ctx.send("Your song is either invalid or missing from the database. Try again.")

        if isinstance(lyrics, bytes):  # This library can be dum-dum
            lyrics = lyrics.decode("utf-8")

        if len(lyrics) > 2048:
            by_line = lyrics.split("\n")
            current_length = 0
            current_index = 0
            while current_length <= 2048:
                current_length += len(by_line[current_index]) + len("\n")
                current_index += 1

            part1 = "\n".join(by_line[:current_index - 1])
            part2 = "\n".join(by_line[current_index:])

            emb1 = discord.Embed(description=part1, color=ctx.bot.embed_color)
            emb1.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
            emb2 = discord.Embed(description=part2, color=ctx.bot.embed_color)
            emb2.set_footer(text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            await ctx.send(embed=emb1)
            await ctx.send(embed=emb2)
        else:
            emb = discord.Embed(description=lyrics, color=ctx.bot.embed_color)

            emb.set_thumbnail(url=ctx.bot.user.avatar_url)
            emb.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
            emb.set_footer(text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(Text())
