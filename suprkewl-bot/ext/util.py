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

import base64
import binascii
from datetime import datetime
import io
import json
import os
import random
import re

import discord
from discord.ext import commands
import gtts

from .utils import async_executor
import config


async def download_file(ctx, data):
    cs = ctx.bot.http2
    async with cs.post(f"http://{config.rtex_server}/api/v2", data={
        "code": data,
        "format": "png"
    }) as resp:
        data = await resp.json()
    return data

token_re = re.compile(r"[a-zA-Z0-9]{24}\.[a-zA-Z0-9]{6}\.[a-zA-Z0-9_\-]{27}|mfa\.[a-zA-Z0-9_\-]{84}")


class Utilities(commands.Cog):
    @commands.command(
        description="Renders LaTeX code."
    )
    async def latex(self, ctx, *, code):
        """Render LaTeX code."""

        async with ctx.typing():
            with open("assets/latex/template.tex", "r") as fp:
                template = fp.read()
            template = re.sub(r"%.*\n", "", template)

            with open("assets/latex/replacements.json", "r") as fp:
                replacements = json.loads(fp.read())

            for key, value in replacements.items():
                code = code.replace(key, value)

            ret = await download_file(ctx, template.replace("#CONTENT", code))
            log = ret.pop("log")

        if ret["status"] == "error":
            data = log.encode("utf-8")
            async with ctx.bot.http2.post("https://hastebin.com/documents", data=data) as resp:
                out = await resp.json()
                if "key" not in out:
                    return await ctx.send("Something wrong happened while rendering. Perhaps your input was invalid?")
                else:
                    pasted_url = "https://hastebin.com/" + out["key"]
            return await ctx.send(
                f"Something wrong happened while rendering. The render log is available at {pasted_url}.")

        async with ctx.typing():

            fname = ret["filename"]

            async with ctx.bot.http2.get(f"http://{config.rtex_server}/api/v2/" + fname) as resp:
                fp = io.BytesIO(await resp.content.read())

        await ctx.send(
            ":white_check_mark: Like it or not, this image is better viewed on light theme.",
            file=discord.File(fp, "latex.png")
        )

    @commands.command(aliases=["tokenparse", "ptoken"])
    @commands.cooldown(1, 2.5, commands.BucketType.member)
    async def parsetoken(self, ctx, *, token):
        """Parse a Discord auth token."""

        if not token_re.match(token):
            await ctx.send("Not a valid token.")

        t = token.split(".")
        if len(t) != 3:
            return await ctx.send("Not a valid token.")

        try:
            id_ = base64.standard_b64decode(t[0]).decode("utf-8")
            try:
                user = await ctx.bot.fetch_user(int(id_))
            except discord.HTTPException:
                user = None
        except binascii.Error:
            return await ctx.send("Failed to decode user ID.")

        try:
            token_epoch = 1293840000
            decoded = int.from_bytes(base64.standard_b64decode(t[1] + "=="), "big")
            timestamp = datetime.utcfromtimestamp(decoded)
            if timestamp.year < 2015:
                timestamp = datetime.utcfromtimestamp(decoded + token_epoch)
            date = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except binascii.Error:
            return await ctx.send("Failed to decode timestamp.")

        invite = discord.utils.oauth_url(id_, discord.Permissions.none())

        fmt = f"**Valid token: **\n\n**User ID is**: {id_} ({user or '*Not fetchable*.'}).\n" \
              f"**Created at**: {date}\n**Cryptographic component**: {t[2]}\n**Invite**: {invite}"

        await ctx.send(fmt)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def tts(self, ctx, *, message):
        """Make me speak a message."""

        async with ctx.typing():
            try:
                tts = gtts.gTTS(text=message)
            except AssertionError:
                return await ctx.send(":x: There was nothing speakable in that message.")

            @async_executor()
            def save():
                fname = f"{ctx.message.id}.mp3"
                tts.save(fname)
                fp = discord.File(fname, "out.mp3")
                return [fname, fp]

            fname, fp = await save()

        await ctx.send(":white_check_mark:", file=fp)
        os.remove(fname)

    @commands.command()
    @commands.guild_only()
    async def serverbanner(self, ctx):
        """Gets the guild banner."""

        if ctx.guild.banner is None:
            await ctx.send("This guild has no banner!")
        else:
            await ctx.send(ctx.guild.banner_url_as(format="png"))

    @commands.command()
    @commands.guild_only()
    async def servericon(self, ctx):
        """Gets the server icon."""

        asset = ctx.guild.icon_url_as(format="png")

        if asset is None:
            await ctx.send("This guild has no icon!")
        else:
            await ctx.send(asset)

    @commands.group(description="Gets an xkcd comic.", invoke_without_command=True)
    @commands.cooldown(1, 3, commands.BucketType.channel)
    async def xkcd(self, ctx, arg: int = None):
        """Gets xkcd comics. Specify a number to get that comic, no number to get the latest comic."""

        if arg is None:
            await self.xkcd_latest(ctx)
        else:
            if arg <= 0:
                return await ctx.send(":x: Invalid comic number.")

            await self.xkcd_get(ctx, arg)

    async def xkcd_get(self, ctx, number):
        async with ctx.bot.http2.get(f"https://xkcd.com/{number}/info.0.json") as resp:
            if resp.status == 404:
                return await ctx.send(":x: Comic not found!")
            text = await resp.json()

        month, day, year = text["month"], text["day"], text["year"]

        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        month = months[month - 1]

        date = f"{month} {day}, {year}"

        emb = discord.Embed(
            color=ctx.bot.embed_color,
            description=f"Here you are! xkcd comic #{number}, published {date}."
            f" Credits to [xkcd](https://xkcd.com/{number})."
        )

        emb.set_image(url=text["img"])

        emb.set_author(name=ctx.me.name,
                       icon_url=ctx.me.avatar_url)
        emb.set_footer(
            text=f"{text['alt']}; Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url
        )

        await ctx.send(embed=emb)

    @xkcd.command(name="random", aliases=["rand"], description="Get a random xkcd comic.")
    async def xkcd_random(self, ctx):
        """Gets a random comic."""

        async with ctx.bot.http2.get("https://xkcd.com/info.0.json") as resp:
            text = await resp.json()
        latest_comic = text["num"]

        comic_to_get = random.randint(0, int(latest_comic))

        async with ctx.bot.http2.get(f"https://xkcd.com/{comic_to_get}/info.0.json") as resp:
            text = await resp.json()

        emb = discord.Embed(
            color=ctx.bot.embed_color,
            description=f"Here you are! xkcd comic #{comic_to_get}. Credits to [xkcd](https://xkcd.com/{comic_to_get})."
        )
        emb.set_image(url=text["img"])

        emb.set_author(
            name=ctx.me.name,
            icon_url=ctx.me.avatar_url
        )
        emb.set_footer(
            text=f"{ctx.bot.embed_footer} Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url
        )

        await ctx.send(embed=emb)

    async def xkcd_latest(self, ctx):
        async with ctx.bot.http2.get("https://xkcd.com/info.0.json") as resp:
            text = await resp.json()

        await self.xkcd_get(ctx, text["num"])


def setup(bot):
    bot.add_cog(Utilities())
