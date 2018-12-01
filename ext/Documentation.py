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
        await ctx.send("Join our support server! https://www.discord.gg/CRBBJVY")

    @commands.command()
    async def github(self, ctx):
        """A link to our GitHub repo."""

        emb = discord.Embed(name = "Our GitHub", color = 0xffffff)
        emb.add_field(name = "Our github", value = "Do note that the repo is often out-of-date. Nonetheless: https://www.github.com/laggycomputer/suprkewl-bot")

        await ctx.send(embed = emb)
        
def setup(bot):
    bot.add_cog(Documentation(bot))
