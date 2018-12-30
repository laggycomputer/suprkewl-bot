# -*- coding: utf-8 -*-
"""Copyright 2018 Dante Dam
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

import discord
from discord.ext import commands

class Documentation():
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def invite(self, ctx):
        """Invite to the support server."""

        emb = discord.Embed(author="Join our Discord server!")

        emb.add_field(name="\u200b", value="https://www.discord.gg/CRBBJVY")
        emb.set_footer(text=f"Requested by {ctx.author.mention}.", icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=emb)

    @commands.command(aliases=["git"])
    async def github(self, ctx):
        """A link to our GitHub repo."""

        emb = discord.Embed(name="Our GitHub", color=0xffffff)
        emb.add_field(name="Our github", value="https://www.github.com/laggycomputer/suprkewl-bot")
        emb.add_field(name="Clone it!", value="`git clone https://github.com/laggycomputer/suprkewl-bot.git`")

        await ctx.send(embed=emb)
        
def setup(bot):
    bot.add_cog(Documentation(bot))
