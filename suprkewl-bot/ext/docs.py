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

import discord
from discord.ext import commands

class Documentation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self, ctx):
        """Invite to the support server."""

        emb = discord.Embed(author="Join our Discord server!", color=0xf92f2f)

        emb.add_field(name="\u200b", value="https://www.discord.gg/CRBBJVY")

        emb.set_thumbnail(url=self.bot.user.avatar_url)
        emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        emb.set_footer(text=f"{self.bot.description} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=emb)

    @commands.command(aliases=["git"])
    async def github(self, ctx):
        """A link to our GitHub repo."""

        emb = discord.Embed(name="Our GitHub", color=0xf92f2f)
        emb.add_field(name="Our github", value="https://www.github.com/laggycomputer/suprkewl-bot")
        emb.add_field(name="Clone it!", value="`git clone https://github.com/laggycomputer/suprkewl-bot.git`")

        emb.set_thumbnail(url=self.bot.user.avatar_url)
        emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        emb.set_footer(text=f"{self.bot.description} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(Documentation(bot))
