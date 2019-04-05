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

import io
import os
import random
import typing

import discord
from discord.ext import commands

from .utils import escape_codeblocks, format_json


class Text(commands.Cog):

    @commands.command(
        description="A bunch of lenny faces."
    )
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
        sent = (await ctx.send(msg))
        await ctx.bot.register_response(sent, ctx.message)

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

        sent = (await ctx.send(msg))
        await ctx.bot.register_response(sent, ctx.message)

    @commands.command(
        description="Make the bot say something. Watch what you say. Has a 5 second user cooldown."
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def say(self, ctx, *, message: str):
        """Make the bot say something."""

        sent = (await ctx.send(f"{ctx.author.mention} wants me to say '{message}'"))
        await ctx.bot.register_response(sent, ctx.message)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.group(
        description="Gives the data under a message, channel, or member in a JSON format, as recieved from the Discord API."
    )
    async def raw(self, ctx):
        """Returns a dict version of some objects."""

        if ctx.invoked_subcommand is None:
            sent = (await ctx.send(":x: Please give a subcommand!"))
            await ctx.bot.register_response(sent, ctx.message)

    @raw.command(aliases=["msg"])
    async def message(self, ctx, message_id: int):
        """Return a message as a dict."""

        message = await ctx.channel.fetch_message(message_id)
        if message is None:
            sent = (await ctx.send(
                ":x: You gave an invalid message ID! If that message is not in this channel, try this command in the channel it belongs to."
            ))
            await ctx.bot.register_response(sent, ctx.message)

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

    @raw.command(aliases=["user"])
    async def member(self, ctx, user: discord.User = None):
        """Return a member as a dict."""
        if user is None:
            user = ctx.author

        route = discord.http.Route("GET", f"/users/{user.id}")
        raw = await ctx.bot.http.request(route)

        sent = (await ctx.send(f"```json\n{escape_codeblocks(format_json(raw))}```"))
        await ctx.bot.register_response(sent, ctx.message)

    @raw.command()
    async def channel(
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
        files = ["bee.txt", "uwu.txt"]
        with open(os.getcwd() + f"..\\..\\assets\\{random.choice(files)}", "rb") as fp:
            sent = (await ctx.send(file=discord.File(fp, filename="love_letter.txt")))
        await ctx.bot.register_response(sent, ctx.message)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def stretch(self, ctx, *, text):
        """Make text L O N G E R."""

        ret = ""

        for i in range(1, 10):
            spaces = " " * i
            ret += f"\n{spaces.join((letter for letter in text))}"

        for i in range(1, 10):
            spaces = " " * abs(i - 10)
            ret += f"\n{spaces.join((letter for letter in text))}"

        if len(ret) > 2000:
            fp = io.BytesIO(ret.encode("utf-8"))

            sent = (await ctx.send(
                content=":white_check_mark: Your output was longer than 2000 characters and was therefore placed in this file:",
                file=discord.File(fp, "stretch.txt")
            ))
        else:
            sent = (await ctx.send(ret))
            await ctx.bot.register_response(sent, ctx.message)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def circle(self, ctx, radius: int, *, string):
        """Print text in a circle."""

        ranges = list(range(1, radius + 1)) + list(range(radius, 0, -1))

        ret = "\n".join((string * c).center(len(radius * string)) for c in ranges)

        ret = "```\n%s\n```" % ret

        if len(ret) > 2000:
            fp = io.BytesIO(ret.encode("utf-8"))

            sent = (await ctx.send(
                content=":white_check_mark: Your output was longer than 2000 characters and was therefore placed in this file:",
                file=discord.File(fp, "circle.txt")
            ))
            await ctx.bot.register_response(sent, ctx.message)
        else:
            sent = (await ctx.send(ret))
            await ctx.bot.register_response(sent, ctx.message)


def setup(bot):
    bot.add_cog(Text())
