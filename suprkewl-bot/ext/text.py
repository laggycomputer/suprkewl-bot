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


class Text(commands.Cog):

    @commands.command(description="Sends text.")
    @commands.cooldown(1, 1, commands.BucketType.member)
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
                content=":white_check_mark: Your output was longer than 2000 characters and was therefore placed in"
                        " this file:",
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
                content=":white_check_mark: Your output was longer than 2000 characters and was therefore placed in"
                        " this file:",
                file=discord.File(fp, "square.txt")
            ))
            await ctx.bot.register_response(sent, ctx.message)
        else:
            sent = (await ctx.send("```\n%s\n```" % ret))
            await ctx.bot.register_response(sent, ctx.message)


def setup(bot):
    bot.add_cog(Text())
