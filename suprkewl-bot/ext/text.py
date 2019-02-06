# -*- coding: utf-8 -*-
"""Copyright 2018 Dante Dam
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

import asyncio
import time

import discord
from discord.ext import commands

class Text():
    def __init__(self, bot):
        self.bot = bot
    @commands.command(description="A bunch of lenny faces. This command has a 10-second cooldown per channel, as it produces a lot of output.")
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def lenny(self, ctx):
        """( ͡° ͜ʖ ͡°) """

        msg = """**LENNY FACES**
Regular:( ͡° ͜ʖ ͡°)
Eyebrow Lenny: ( ͠° ͜ʖ ͡°)
chienese lenny: （͡°͜ʖ͡°）
TAKE THAT: ( ͡0 ͜ʖ ͡ 0)----@-
The generic tf2 pyro lenny:( ͡w ͜+ ͡m1)
2long4u:( ͡0 ͜ʖ ͡ 0)
Confused:( ͠° ͟ʖ ͡°)
Jew Lenny: (͡ ͡° ͜ つ ͡͡°)
Strong:ᕦ( ͡° ͜ʖ ͡°)ᕤ
The Mino Lenny: ˙͜>˙
Nazi Lenny: ( ͡卐 ͜ʖ ͡卐)
Cat Lenny:( ͡° ᴥ ͡°)
Praise the sun!: [T]/﻿
Dorito Lenny: ( ͡V ͜ʖ ͡V )
Wink:( ͡~ ͜ʖ ͡°)
swiggity swootey:( ͡o ͜ʖ ͡o)
ynneL:( ͜。 ͡ʖ ͜。)﻿
Wink 2: ͡° ͜ʖ ͡ -
I see u:( ͡͡ ° ͜ ʖ ͡ °)﻿
Alien:( ͡ ͡° ͡° ʖ ͡° ͡°)
U WOT M8:(ง ͠° ͟ل͜ ͡°)ง
Lenny Gang: ( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)
dErP:( ͡° ͜ʖ ͡ °)
Kitty?:(ʖ ͜° ͜ʖ)
monster lenny: ( ͜。 ͡ʖ ͡O)
Square:[ ͡° ͜ʖ ͡°]
Raise Your Donger:ヽ༼ຈل͜ຈ༽ﾉ
Imposter:{ ͡• ͜ʖ ͡•}
Voldemort:( ͡° ͜V ͡°)
Happy:( ͡^ ͜ʖ ͡^)
Satisfied:( ‾ʖ̫‾)
Sensei dong:( ͡°╭͜ʖ╮͡° )
Sensei doing Dong dong woo:ᕦ( ͡°╭͜ʖ╮͡° )ᕤ
Donger bill:[̲̅$̲̅(̲̅ ͡° ͜ʖ ͡°̲̅)̲̅$̲̅]
Spider lenny://( ͡°͡° ͜ʖ ͡°͡°)/\
The noseless lenny:( ͡° ͜ ͡°)
Cool lenny: (⌐■_■)
Cheeky Lenny:: (͡o‿O͡)
Arrow Lenny: ⤜( ͠° ͜ʖ °)⤏
Table Lenny: (╯°□°)╯︵ ┻━┻
cONFUSED lenny乁( ⁰͡ Ĺ̯ ⁰͡ ) ㄏ
nazi lennys: ( ͡° ͜ʖ ͡°)/ ( ͡° ͜ʖ ͡°)/ ( ͡° ͜ʖ ͡°)/ ( ͡° ͜ʖ ͡°)/ 卐卐卐
Oh hay: (◕ ◡ ◕)
Manly Lenny: ᕦ( ͡͡~͜ʖ ͡° )ᕤ
Put ur dongers up or I'll shoot:(ง ͡° ͜ʖ ͡°)=/̵͇̿/'̿'̿̿̿ ̿ ̿̿
Badass Lenny: ̿ ̿'̿'̵͇̿з=(⌐■ʖ■)=ε/̵͇̿/'̿̿ ̿
"""
        async with ctx.channel.typing():
            await asyncio.sleep(1)
            await ctx.send(msg)

    @commands.command(description="LMAO! Has a 5-second channel cooldown to keep things calm.")
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def lmao(self, ctx):
        """A nice and long lmao"""
        msg = """
L
    M
        A
          O
            o
           o
          o
         。
        。
       ."""

        async with ctx.typing():
            await asyncio.sleep(1)
            await ctx.send(msg)

    @commands.command(description="Make the bot say something. Watch what you say. Has a 5 second user cooldown.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def say(self, ctx, *, message: str):
        """Make the bot say something."""

        await ctx.send(f"{ctx.author.mention} wants me to say '{message}'")

def setup(bot):
    bot.add_cog(Text(bot))
