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

import base64
import binascii
import datetime
import io
import json
import os
import random
import re
import typing
import unicodedata
from urllib.parse import quote as urlquote

import discord
from discord.ext import commands
import gtts

from .utils import async_executor, escape_codeblocks, format_json, human_timedelta
import config


token_re = re.compile(r"[a-zA-Z0-9]{24}\.[a-zA-Z0-9]{6}\.[a-zA-Z0-9_\-]{27}|mfa\.[a-zA-Z0-9_\-]{84}")
EPOCH = 1420070400000


def to_datetime(obj):
    if not isinstance(obj, int):
        id_ = obj.id
    else:
        id_ = obj

    unix_time = ((id_ >> 22) + EPOCH) / 1000

    return unix_time, datetime.datetime.utcfromtimestamp(unix_time)


async def download_rtex_file(ctx, data):
    cs = ctx.bot.http2
    async with cs.post(f"http://{config.rtex_server}/api/v2", data=dict(code=data, format="png")) as resp:
        data = await resp.json()
    return data


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

            ret = await download_rtex_file(ctx, template.replace("#CONTENT", code))
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
            return await ctx.send("Not a valid token.")

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
            timestamp = datetime.datetime.utcfromtimestamp(decoded)
            if timestamp.year < 2015:
                timestamp = datetime.datetime.utcfromtimestamp(decoded + token_epoch)
            date = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except binascii.Error:
            return await ctx.send("Failed to decode timestamp.")

        fmt = f"**Valid token: **\n\n**User ID is**: {id_} ({user or '*Not fetchable*.'}).\n" \
              f"**Token created at (yyyy-mm-dd)**: {date}\n**Cryptographic component**: {t[2]}\n"

        if user:
            if not user.bot:
                fmt += f"** Invite **: {discord.utils.oauth_url(id_)}"

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

        await ctx.send(asset or "This guild has no set icon!")

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

        dt = datetime.datetime(int(year), int(month), int(day))
        delta = human_timedelta(dt, accuracy=4)
        date = dt.strftime("%B %d, %Y")

        emb = discord.Embed(
            color=ctx.bot.embed_color,
            description=f"Here you are! xkcd comic #{number}, published {date} ({delta})."
            f" Credits to [xkcd](https://xkcd.com/{number})."
        )

        emb.set_image(url=text["img"])

        emb.set_author(name=ctx.me.name,
                       icon_url=ctx.me.avatar_url)
        emb.set_footer(
            text=f"{text['alt']} Requested by {ctx.author}",
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

        await self.xkcd_get(ctx, comic_to_get)

    async def xkcd_latest(self, ctx):
        async with ctx.bot.http2.get("https://xkcd.com/info.0.json") as resp:
            text = await resp.json()

        await self.xkcd_get(ctx, text["num"])

    @commands.group(
        aliases=["sftime", "snowtime", "snowstamp", "ss"],
        description="NOTE: If you use `compare`, `c`, or `cmp` as an argument, I will try to invoke the subcommand. If"
                    " this happens, try using the actual ID instead of the name.")
    async def snowflaketime(
            self, ctx, *,
            id: typing.Union[
                int, discord.Member, discord.User, discord.Message, discord.TextChannel, discord.VoiceChannel,
                discord.CategoryChannel, discord.Role, discord.Emoji, discord.PartialEmoji]):  # Yuck.
        """Get the creation date of a Discord ID/Snowflake."""

        if not isinstance(id, int):
            id = id.id

        unix_time, dt = to_datetime(id)

        if dt <= datetime.datetime.utcfromtimestamp(EPOCH / 1000):
            return await ctx.send("That object seems like it was created on the Discord epoch. Is the ID valid?")
        human_readable = dt.strftime("%A, %B %d, at %H:%M:%S UTC")

        delta = human_timedelta(dt)

        await ctx.send(
            f"This object with ID {id} was created {delta}, on {human_readable} in {dt.year}. That's Unix time"
            f" {unix_time}.\n\nP.S. Looking for the formula? See `{ctx.prefix}source {ctx.invoked_with}`."
        )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.group(
        description="Gives the data under a message, channel, or member in a JSON format, as received from the"
                    " Discord API."
    )
    async def raw(self, ctx):
        """Returns a dict version of some objects."""

        if ctx.invoked_subcommand is None:
            await ctx.send(":x: Please provide a valid subcommand!")
            await ctx.send_help(ctx.command)

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

    @commands.command(description="Snipe a deleted message", aliases=["sniperino"])
    @commands.guild_only()
    async def snipe(self, ctx, *, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        sniped = await ctx.bot.db.execute(
            "SELECT * FROM snipes WHERE channel_id=? AND guild_id=?;",
            (channel.id,
             ctx.guild.id)
        )
        fetched = await sniped.fetchone()
        if not fetched:
            return await ctx.send("Nothing to snipe... yet.")
        if channel.is_nsfw() is True and ctx.channel.is_nsfw() is False:
            return await ctx.send("You cannot snipe from a normal channel into an NSFW one.")

        desc = [c_name[0] for c_name in sniped.description]
        guild = ctx.bot.get_guild(fetched[desc.index("guild_id")])
        user = ctx.bot.get_user(fetched[desc.index("user_id")])
        chnl = discord.utils.get(guild.text_channels, id=fetched[desc.index("channel_id")])
        message_id = fetched[desc.index("message_id")]
        msg_content = fetched[desc.index("message")]

        e = ctx.default_embed
        if fetched[desc.index("msg_type")] == 1:
            e.description = "The image may not be visible"
            e.set_author(name=f"{user.name} sent in {chnl.name}")
            e.set_image(url=msg_content)
        elif fetched[desc.index("msg_type")] == 2:
            e.set_author(name=f"{user.name} said in an embed in #{chnl.name}:")
            e.description = msg_content
        else:
            e.description = msg_content
            e.set_author(name=f"{user.name} said in #{chnl.name}")

        e.set_footer(text=f"Message ID {message_id} | User ID {user.id} | Channel ID {chnl.id} | Guild ID {guild.id}")
        await ctx.send(embed=e)

    @commands.command(aliases=["ci", "char", "ch", "c"])
    async def charinfo(self, ctx, *, characters):
        """Shows you Unicode information about the given characters."""

        def to_string(c):
            digit = f"{ord(c):x}"
            name = unicodedata.name(c, "Name not found.")
            return f"`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>"
        msg = ctx.author.mention + "\n" + "\n".join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send(":x: Output too long to display, try using less characters.")
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Utilities())
