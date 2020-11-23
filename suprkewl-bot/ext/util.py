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
import math
import os
import random
import re
import typing
import unicodedata
from urllib.parse import quote as urlquote
import uuid

import aiohttp
import discord
from discord.ext import commands
import gtts
from PIL import Image
import pyqrcode

from .utils import async_executor, Embedinator, escape_codeblocks, format_json, human_join, human_timedelta
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
    cs = ctx.bot.session
    async with cs.post(f"http://{config.rtex_server}/api/v2", data=dict(code=data, format="png")) as resp:
        data = await resp.json()
    return data


@async_executor()
def create_qr(data):
    fp = io.BytesIO()
    qr = pyqrcode.create(data, error="H")
    qr.png(fp)
    fp.seek(0)
    img = Image.open(fp)
    img = img.resize((550, 550))
    fp = io.BytesIO()
    img.save(fp, "png")
    fp.seek(0)

    return fp


async def process_qr(ctx, argument):
    is_found = False
    url = None
    for att in ctx.message.attachments:
        if att.height is not None and not is_found:
            url = att.proxy_url
            is_found = True

    if not is_found:
        url = argument

    try:
        async with ctx.bot.session.get(url) as resp:
            try:
                img = Image.open(io.BytesIO(await resp.content.read())).convert("RGB")
                is_found = True
            except OSError:
                await ctx.send(":x: That URL is not an image.")
                return
    except aiohttp.InvalidURL:
        await ctx.send(":x: That URL is invalid.")
        return

    if not is_found:
        return None

    fp = io.BytesIO()
    img.save(fp, "png")
    fp.seek(0)

    return fp


async def name_resolve(ctx, ign, *, silent=False):
    ign = ign.replace("-", "")  # This has no affect on names, but works on UUIDs

    async with ctx.bot.session.get(f"https://api.mojang.com/users/profiles/minecraft/{ign}") as resp:
        if resp.status not in [204, 400, 404]:
            get_by_name = await resp.json()
        else:
            get_by_name = None

    if get_by_name is not None:
        proposed_uuid = get_by_name["id"]
    else:
        proposed_uuid = ign
    async with ctx.bot.session.get(f"https://api.mojang.com/user/profiles/{proposed_uuid}/names") as resp:
        if resp.status not in [204, 404]:
            get_by_uuid = await resp.json()
        else:
            if not silent:
                await ctx.send(":x: Your input could not be interpreted as a UUID or currently valid name.")
            return

    if get_by_name is not None:
        uuid = get_by_name["id"]
    else:
        try:
            uuid = ign
            ign = get_by_uuid[-1]["name"]
        except KeyError:
            if not silent:
                await ctx.send(":x: Your input could not be interpreted as a UUID or currently valid name.")
            return

    return uuid, ign


async def insert_past_names(db, names, player_uuid):
    uuid_bytes = uuid.UUID(player_uuid).bytes
    must_commit = False
    for past_name in names:
        if not await (await db.execute(
                "SELECT uuid1, uuid2 from past_igns WHERE past_ign == ?;", (past_name.lower(),))).fetchall():
            must_commit = True
            await db.execute(
                "INSERT INTO past_igns (past_ign, uuid1, uuid2) VALUES (?, ?, ?) ON CONFLICT DO NOTHING;",
                (past_name, uuid_bytes[:8], uuid_bytes[8:]))
    if must_commit:
        await db.commit()


class Utilities(commands.Cog):

    @commands.command(
        description="Renders LaTeX code."
    )
    async def latex(self, ctx, *, code):
        """Render LaTeX code."""

        async with ctx.typing():
            with open(os.path.join("assets", "latex", "template.tex")) as fp:
                template = fp.read()
            template = re.sub(r"%.*\n", "", template)

            with open(os.path.join("assets", "latex", "replacements.json")) as fp:
                replacements = json.loads(fp.read())

            for key, value in replacements.items():
                code = code.replace(key, value)

            ret = await download_rtex_file(ctx, template.replace("#CONTENT", code))
            log = ret.pop("log")

        if ret["status"] == "error":
            data = log.encode("utf-8")
            async with ctx.bot.session.post("https://hastebin.com/documents", data=data) as resp:
                out = await resp.json()
                if "key" not in out:
                    return await ctx.send("Something wrong happened while rendering. Perhaps your input was invalid?")
                else:
                    pasted_url = "https://hastebin.com/" + out["key"]
            return await ctx.send(
                f"Something wrong happened while rendering. The render log is available at {pasted_url}.")

        async with ctx.typing():

            fname = ret["filename"]

            async with ctx.bot.session.get(f"http://{config.rtex_server}/api/v2/" + fname) as resp:
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
        async with ctx.bot.session.get(f"https://xkcd.com/{number}/info.0.json") as resp:
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

        async with ctx.bot.session.get("https://xkcd.com/info.0.json") as resp:
            text = await resp.json()
        latest_comic = text["num"]

        comic_to_get = random.randint(0, int(latest_comic))

        await self.xkcd_get(ctx, comic_to_get)

    async def xkcd_latest(self, ctx):
        async with ctx.bot.session.get("https://xkcd.com/info.0.json") as resp:
            text = await resp.json()

        await self.xkcd_get(ctx, text["num"])

    @commands.group(aliases=["sftime", "snowtime", "snowstamp", "ss"])
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

        worker_info = id & ((1 << 22) - 1)
        worker_id = worker_info >> 17
        worker_pid = (worker_info >> 12) & ((1 << 5) - 1)
        gen_num = id & ((1 << 12) - 1)

        await ctx.send(
            f"This object with ID {id} was created {delta}, on {human_readable} in {dt.year}. That's Unix time"
            f" {unix_time}.\n\nInternal worker info:\nThe ID of the worker that generated this ID is {worker_id} with "
            f"PID {worker_pid}. This ID is #{gen_num} generated by this worker."
        )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.group(
        description="Gives the data under a message, channel, or member in a JSON format, as received from the"
                    " Discord API.",
        invoke_without_command=True
    )
    async def raw(self, ctx):
        """Returns a dict version of some objects."""

        await ctx.send(":x: Please provide a valid subcommand!")
        await ctx.send_help(ctx.command)

    @raw.command(name="message", aliases=["msg"])
    async def raw_message(self, ctx, *, message: discord.Message):
        """Return a message as a dict."""

        raw = await ctx.bot.http.get_message(message.channel.id, message.id)
        ret = format_json(raw)
        to_send = f"```json\n{escape_codeblocks(ret)}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(ret)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(ret.encode("utf-8")), "out.txt")
                await ctx.send(file=fp)
        else:
            await ctx.send(to_send)

    @raw.command(name="member", aliases=["user"])
    async def raw_member(self, ctx, *, user: discord.User = None):
        """Return a member as a dict."""

        user = user or ctx.author

        route = discord.http.Route("GET", f"/users/{user.id}")
        raw = await ctx.bot.http.request(route)
        ret = format_json(raw)
        to_send = f"```json\n{escape_codeblocks(ret)}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(ret)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(ret.encode("utf-8")), "out.txt")
                await ctx.send(file=fp)
        else:
            await ctx.send(to_send)

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

        ret = format_json(raw)
        to_send = f"```json\n{escape_codeblocks(ret)}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(ret)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(ret.encode("utf-8")), "out.txt")
                await ctx.send(file=fp)
        else:
            await ctx.send(to_send)

    @commands.command(aliases=["pfp"])
    @commands.cooldown(3, 1, commands.BucketType.user)
    async def profile(self, ctx, *, user: typing.Union[discord.Member, discord.User] = None):
        """Get a user's profile picture in various formats."""

        user = user or ctx.author

        emb = ctx.default_embed()

        formats = ["webp", "jpg", "png"]
        if user.is_avatar_animated():
            formats += ["gif"]
            preview_url = user.avatar_url_as(format="gif", size=4096)
            fp = discord.File(io.BytesIO(await preview_url.read()), "avatar.gif")
            emb.set_image(url="attachment://avatar.gif")
        else:
            preview_url = user.avatar_url_as(format="png", size=4096)
            fp = discord.File(io.BytesIO(await preview_url.read()), "avatar.png")
            emb.set_image(url="attachment://avatar.png")

        def make_link(format, size):
            if size:
                url = str(user.avatar_url_as(format=format, size=size))
            else:
                url = str(user.avatar_url_as(format=format)).rstrip("?size=1024")
            link_name = f"{size}x" if size else "Direct"
            return f"[{link_name}]({url})"

        emb.add_field(name="Member", value=f"{user.mention} ({user})", inline=False)
        for fmt in formats:
            links = []
            for size in [None] + [2 ** x for x in range(7, 13)]:
                links.append(make_link(fmt, size))

            emb.add_field(name=fmt.upper(), value=" | ".join(links), inline=False)

        await ctx.send(embed=emb, file=fp)

    # Thanks to Takaru, PendragonLore/TakaruBot
    @commands.command()
    async def pypi(self, ctx, *, name):
        data = await (await ctx.bot.session.get(f"https://pypi.org/pypi/{urlquote(name, safe='')}/json")).json()

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
        fp = discord.File(os.path.join("assets", "pypi.png"), "image.png")
        embed.set_thumbnail(
            url="attachment://image.png"
        )

        await ctx.send(embed=embed, file=fp)

    @commands.command(aliases=["sniperino"])
    @commands.cooldown(3, 2, commands.BucketType.channel)
    @commands.guild_only()
    async def snipe(self, ctx, *, channel: discord.TextChannel = None):
        """Snipe a deleted message"""

        channel = channel or ctx.channel
        sniped = await ctx.bot.db.execute(
            "SELECT * FROM snipes WHERE channel_id == ? AND guild_id == ?;",
            (channel.id,
             ctx.guild.id)
        )
        fetched = await sniped.fetchone()
        if not fetched:
            return await ctx.send("Nothing to snipe... yet.")
        if channel.is_nsfw() is True and ctx.channel.is_nsfw() is False:
            return await ctx.send("You cannot snipe from a normal channel into an NSFW one.")

        user_perms = ctx.author.permissions_in(channel)
        if not user_perms.read_messages or not user_perms.read_message_history:
            return await ctx.send(":x: You cannot see that channel.")

        desc = [c_name[0] for c_name in sniped.description]
        guild = ctx.bot.get_guild(fetched[desc.index("guild_id")])
        user = ctx.bot.get_user(fetched[desc.index("user_id")])
        if not user:
            user = await ctx.bot.fetch_user(fetched[desc.index("user_id")])
        chnl = discord.utils.get(guild.text_channels, id=fetched[desc.index("channel_id")])
        message_id = fetched[desc.index("message_id")]
        msg_content = fetched[desc.index("message")]

        e = ctx.default_embed()
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

    @commands.command(aliases=["esnipe", "es"])
    @commands.cooldown(3, 2, commands.BucketType.channel)
    async def editsnipe(self, ctx, *, channel: discord.TextChannel = None):
        """Snipe the former content of an edited message"""

        channel = channel or ctx.channel
        sniped = await ctx.bot.db.execute(
            "SELECT * FROM edit_snipes WHERE channel_id == ? AND guild_id == ?;",
            (channel.id,
             ctx.guild.id)
        )
        fetched = await sniped.fetchone()
        if not fetched:
            return await ctx.send("Nothing to snipe... yet.")
        if channel.is_nsfw() is True and ctx.channel.is_nsfw() is False:
            return await ctx.send("You cannot snipe from a normal channel into an NSFW one.")

        user_perms = ctx.author.permissions_in(channel)
        if not user_perms.read_messages or not user_perms.read_message_history:
            return await ctx.send(":x: You cannot see that channel.")

        e = ctx.default_embed()
        desc = [c_name[0] for c_name in sniped.description]
        guild = ctx.bot.get_guild(fetched[desc.index("guild_id")])
        user = ctx.bot.get_user(fetched[desc.index("user_id")])
        if not user:
            user = await ctx.bot.fetch_user(fetched[desc.index("user_id")])
        chnl = discord.utils.get(guild.text_channels, id=fetched[desc.index("channel_id")])
        message_id = fetched[desc.index("message_id")]
        before = fetched[desc.index("before")]
        after = fetched[desc.index("after")]

        e.add_field(name="Before", value=before, inline=False)
        e.add_field(name="After", value=after, inline=False)

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

    @commands.group(invoke_without_command=True, aliases=["namemc", "mcname", "mcign", "ign"])
    @commands.cooldown(5, 1, commands.BucketType.user)
    async def minecraftign(self, ctx, *, ign):
        """Get history on a Minecraft name."""

        ign = ign.replace("-", "")  # This has no affect on names, but works on UUIDs

        potential_past_uuids = await (await ctx.bot.db.execute(
            "SELECT uuid1, uuid2 from past_igns WHERE past_ign == ?;", (ign.lower(),))).fetchall()
        if potential_past_uuids is not None:
            potential_past_uuids = [uuid.UUID(bytes=b"".join(x)).hex for x in potential_past_uuids]
            names_to_use = []
            for potential_past_uuid in potential_past_uuids:
                might_append = (await name_resolve(ctx, potential_past_uuid, silent=True))[1].lower()
                if might_append != ign.lower():
                    names_to_use.append(might_append)
        else:
            names_to_use = []

        async with ctx.bot.session.get(f"https://api.mojang.com/users/profiles/minecraft/{ign}") as resp:
            if resp.status not in [204, 400, 404]:
                get_by_name = await resp.json()
            else:
                get_by_name = None

        if get_by_name is not None:
            proposed_uuid = get_by_name["id"]
        else:
            proposed_uuid = ign
        async with ctx.bot.session.get(f"https://api.mojang.com/user/profiles/{proposed_uuid}/names") as resp:
            if resp.status not in [204, 400, 404]:
                get_by_uuid = await resp.json()
            else:
                error_content = ":x: Your input could not be interpreted as a UUID or currently valid name."
                if names_to_use:
                    error_content += f" However, `{ign}` is a former username of " \
                                     f"{human_join(names_to_use, final='and')}. Try " \
                                     f"`{ctx.prefix}{ctx.invoked_with} <name>` again."
                return await ctx.send(error_content)

        emb = Embedinator(ctx.bot, ctx, color=ctx.bot.embed_color, member=ctx.author)
        past_warning = ""
        if get_by_name is not None:
            name = ign
            player_uuid = get_by_name["id"]
            human_uuid = "-".join(player_uuid[i:i + 4] for i in range(0, len(player_uuid), 4))
            emb_name = f"The name {name} has UUID `{human_uuid}`."
            if names_to_use:
                past_warning = f"\n(Note: `{ign}` is also a former name of {human_join(names_to_use, final='and')}.)"
        else:
            try:
                name = get_by_uuid[-1]["name"]
            except KeyError:
                return await ctx.send(":x: Your input could not be interpreted as a UUID or currently valid name.")
            player_uuid = ign
            human_uuid = '-'.join(player_uuid[i:i + 4] for i in range(0, len(player_uuid), 4))
            emb_name = f"UUID `{human_uuid}` resolves to the name {name}."
        emb.add_field(
            name=emb_name,
            value=f"[Plancke](https://plancke.io/hypixel/player/stats/{player_uuid}) "
                  f"[NameMC](https://namemc.com/name/{name}){past_warning}\n\nUsername history:",
            inline=False
        )

        past_names = []

        for name_time_pair in reversed(get_by_uuid):
            iter_name = name_time_pair["name"]
            if iter_name.lower() != name.lower():
                past_names.append(iter_name.lower())
            timestamp = name_time_pair.get("changedToAt", None)
            if timestamp is None:
                emb.add_field(name=f"Created as `{iter_name}`", value="\u200b", inline=False)
                break
            else:
                timestamp = datetime.datetime.utcfromtimestamp(timestamp / 1000).strftime("%c")
                emb.add_field(name=f"Changed to `{iter_name}`", value=f"On {timestamp}", inline=False)

        await insert_past_names(ctx.bot.db, past_names, player_uuid)

        emb.set_footer(text="All timestamps are in UTC.", icon_url=ctx.me.avatar_url)
        emb.set_thumbnail(url=f"https://crafatar.com/renders/body/{player_uuid}?overlay")
        await emb.send()
        await emb.handle()

    @minecraftign.command(name="at", description="Time format is mm/dd/yy.")
    async def minecraftign_at(self, ctx, ign, *, time=None):
        """See the UUID for an IGN at a different point in time, default the *nix epoch."""

        try:
            time = datetime.datetime.strptime(time, "%m/%d/%y") or datetime.datetime.fromtimestamp(0)
        except ValueError:
            return await ctx.send(":x: Is that timestamp valid?")

        if time > datetime.datetime.now():
            return await ctx.send(":x: That timestamp appears to be in the future. Is it valid?")

        timestamp = int(time.timestamp())

        async with ctx.bot.session.get(f"https://api.mojang.com/users/profiles/minecraft/{ign}?at={timestamp}") as resp:
            if resp.status not in [204, 400]:
                resp = await resp.json()
            else:
                resp = None
        if resp is None:
            return await ctx.send(f":x: It doesn't appear that IGN was ever valid.\n"
                                  f"(Alternately, the only person who has used this name is also still using it, in "
                                  f"which case see `{ctx.prefix}ign {ign}`.)")

        if resp["name"].lower() != ign.lower():
            await ctx.send(f"IGN {ign} was held by the player now known as {resp['name']} at the given time.")
            await insert_past_names(ctx.bot.db, [resp["name"].lower()], resp["id"])
        else:
            await ctx.send(f"IGN {ign} was held by its current owner at this timestamp.")

    @commands.group(aliases=["craftatar", "skinrender", "sr", "rs"], invoke_without_command=True)
    @commands.cooldown(3, 5, commands.BucketType.user)
    async def renderskin(self, ctx):
        """Render a Minecraft skin."""

        await ctx.send(":x: Please provide a valid render mode!")
        await ctx.send_help(ctx.command)

    @renderskin.command(name="flat", aliases=["raw", "default", "r", "d", "s"])
    async def renderskin_flat(self, ctx, *, ign):
        """Render as the .png used to set your skin."""

        resolve_resp = await name_resolve(ctx, ign)
        if resolve_resp is None:
            return
        uuid, ign = resolve_resp

        emb = ctx.default_embed()
        emb.description = "Renders provided by [Crafatar](https://crafatar.com/). If this user's skin was updated " \
                          "recently, it may take some time for caches to flush and for the render to update."
        emb.set_image(url=f"https://crafatar.com/skins/{uuid}")

        await ctx.send(embed=emb)

    @renderskin.command(name="cape", aliases=["c"])
    async def renderskin_cape(self, ctx, *, ign):
        """Render the user's cape."""

        resolve_resp = await name_resolve(ctx, ign)
        if resolve_resp is None:
            return
        uuid, ign = resolve_resp

        emb = ctx.default_embed()
        emb.description = "Renders provided by [Crafatar](https://crafatar.com/). If this user's skin was updated " \
                          "recently, it may take some time for caches to flush and for the render to update."
        emb.set_image(url=f"https://crafatar.com/capes/{uuid}")

        await ctx.send(embed=emb)

    @renderskin.command(name="avatar", aliases=["avy", "a", "flathead", "fh", "headflat", "hf"])
    async def renderskin_avatar(self, ctx, *, ign):
        """Render the front of the user's head."""

        resolve_resp = await name_resolve(ctx, ign)
        if resolve_resp is None:
            return
        uuid, ign = resolve_resp

        emb = ctx.default_embed()
        emb.description = "Renders provided by [Crafatar](https://crafatar.com/). If this user's skin was updated " \
                          "recently, it may take some time for caches to flush and for the render to update."
        emb.set_image(url=f"https://crafatar.com/avatars/{uuid}?overlay")

        await ctx.send(embed=emb)

    @renderskin.command(name="head",
                        aliases=["h", "headiso", "headisometric", "hi", "isometrichead", "ih"])
    async def renderskin_head(self, ctx, *, ign):
        """Render the user's head isometrically."""

        resolve_resp = await name_resolve(ctx, ign)
        if resolve_resp is None:
            return
        uuid, ign = resolve_resp

        emb = ctx.default_embed()
        emb.description = "Renders provided by [Crafatar](https://crafatar.com/). If this user's skin was updated " \
                          "recently, it may take some time for caches to flush and for the render to update."
        emb.set_image(url=f"https://crafatar.com/renders/head/{uuid}?overlay")

        await ctx.send(embed=emb)

    @renderskin.command(name="body",
                        aliases=["b", "bodyiso", "bodyisometric", "bi", "isometricbody", "ib"])
    async def renderskin_body(self, ctx, *, ign):
        """Render the user's body isometrically."""

        resolve_resp = await name_resolve(ctx, ign)
        if resolve_resp is None:
            return
        uuid, ign = resolve_resp

        emb = ctx.default_embed()
        emb.description = "Renders provided by [Crafatar](https://crafatar.com/). If this user's skin was updated " \
                          "recently, it may take some time for caches to flush and for the render to update."
        emb.set_image(url=f"https://crafatar.com/renders/body/{uuid}?overlay")

        await ctx.send(embed=emb)

    @commands.command(aliases=["hyp"])
    @commands.cooldown(3, 5, commands.BucketType.user)
    async def hypixel(self, ctx, *, ign):
        """Look up Hypixel stats for a user."""

        resolve_resp = await name_resolve(ctx, ign)
        if resolve_resp is None:
            return
        uuid, ign = resolve_resp

        params = dict(key=config.hypixel_key, uuid=uuid)
        async with ctx.bot.session.get("https://api.hypixel.net/player", params=params) as resp:
            data = await resp.json()

        if not data["success"]:
            return await ctx.send(":x: Something went wrong fetching your data.")

        if data["player"] is None:  # Either this account is not in the Hypixel DB or Mojang is returning garbage.
            return await ctx.send(
                "Interesting, a new error. Either the account you requested has never logged into Hypixel, or "
                "something else went very wrong on Mojang's end."
            )

        msg = await ctx.send("Fetching...")

        date_format = "%a %b %d, %Y at %H:%M:%S"
        emb = ctx.default_embed()
        emb.set_thumbnail(url=f"https://crafatar.com/renders/body/{uuid}?overlay")

        found_rank = None
        rank_lookup = {
            "SUPERSTAR": "MVP++",
            "MVP_PLUS": "MVP+",
            "MVP": "MVP",
            "VIP_PLUS": "VIP+",
            "VIP": "VIP",
            "NONE": "NON",
            "NORMAL": "NON"
        }

        if "prefix" in data["player"]:
            found_rank = data["player"]["prefix"]
            while "§" in found_rank:
                index = found_rank.index("§")
                if index != len(found_rank) - 1:
                    found_rank = found_rank[:index] + found_rank[index + 2:]
        else:
            if "rank" in data["player"]:
                found_rank = "[%s]" % rank_lookup.get(data["player"]["rank"], None) or data["player"]["rank"]
            else:
                if "monthlyPackageRank" in data["player"]:
                    found_rank = "[%s]" % rank_lookup.get(
                        data["player"]["monthlyPackageRank"], None
                    ) or data["player"]["monthlyPackageRank"]
                else:
                    if "newPackageRank" in data["player"]:
                        found_rank = "[%s]" % rank_lookup.get(
                            data["player"]["newPackageRank"], None) or data["player"]["newPackageRank"]
                    else:
                        if "packageRank" in data["player"]:
                            found_rank = "[%s]" % rank_lookup.get(
                                data["player"]["packageRank"], None
                            ) or data["player"]["packageRank"]
                        else:
                            pass
        emb.description = f"{found_rank or '[NON]'} {ign}"

        if "networkExp" in data["player"]:
            exp = data["player"]["networkExp"]

            def calc_lev(xp):
                level_and_decimal = (math.sqrt(xp + 15312.5) - 125 / math.sqrt(2))/(25 * math.sqrt(2))
                return level_and_decimal // 1, level_and_decimal - math.floor(level_and_decimal)
            lev, dec_to_next_lev = calc_lev(exp)
            dec_to_next_lev = round(dec_to_next_lev * 100)
            lev, dec_to_next_lev = map(int, [lev, dec_to_next_lev])
            emb.add_field(name="Network Level:", value=f"{lev}, {dec_to_next_lev}% to level {lev + 1}")
        if "karma" in data["player"]:
            emb.add_field(name="Karma", value=data["player"]["karma"])
        first_login = datetime.datetime.utcfromtimestamp(data["player"]["firstLogin"] // 1000)
        emb.add_field(name="First login",
                      value=f"{first_login.strftime(date_format)} ({human_timedelta(first_login, brief=True)})")
        is_online = False

        if "lastLogin" in data["player"]:
            last_login = datetime.datetime.utcfromtimestamp(data["player"]["lastLogin"] // 1000)
            emb.add_field(name="Last login",
                          value=f"{last_login.strftime(date_format)} ({human_timedelta(last_login, brief=True)})")
            is_online = data["player"]["lastLogin"] - data["player"]["lastLogout"] >= 0

        if is_online:
            async with ctx.bot.session.get("https://api.hypixel.net/status", params=params) as resp:
                status_data = await resp.json()
            should_brk = False
            if not status_data["success"]:
                should_brk = True
            else:
                if not status_data["session"]["online"]:
                    # What?!
                    should_brk = True
            if not should_brk:
                game = status_data["session"]["gameType"].lower()
                version = data["player"]["mcVersionRp"]
                emb.add_field(name="Online?", value=f"Yes, in game `{game}` on game version `{version}`.")
        else:
            if "lastLogout" in data["player"]:
                logged_out_at = datetime.datetime.utcfromtimestamp(data["player"]["lastLogout"] // 1000)
                emb.add_field(name="Online?",
                              value=f"No, logged out on "
                                    f"{logged_out_at.strftime(date_format)} "
                                    f"({human_timedelta(logged_out_at, brief=True)})")

            else:
                emb.add_field(name="Online?", value="Unknown, player has disabled online/offline API")

        async with ctx.bot.session.get(f"https://api.hypixel.net/guild?player={uuid}", params=params) as resp:
            guild_data = await resp.json()
        if guild_data["success"] and guild_data.get("guild", None) is not None:
            g_name = guild_data["guild"]["name"]
            emb.add_field(name="Guild",
                          value=f"[{g_name}](https://plancke.io/hypixel/guild/name/{urlquote(g_name, safe='')})")

        emb.add_field(name="Full stats here:", value=f"[Plancke](https://plancke.io/hypixel/player/stats/{uuid})",
                      inline=False)
        await msg.edit(content=None, embed=emb)

    @commands.group(invoke_without_command=True)
    @commands.cooldown(10, 10, commands.BucketType.user)
    async def qr(self, ctx):
        """Create or read QR codes."""

        await ctx.send(":x: Please provide a valid subcommand!")
        await ctx.send_help(ctx.command)

    @qr.command(name="create", aliases=["make", "e", "encode"])
    async def qr_create(self, ctx, *, text):
        """Create a QR code based on input text."""

        try:
            text = int(text)
        except ValueError:
            pass

        try:
            file = await create_qr(text)
        except ValueError:
            return await ctx.send(":x: Your text does not fit into a valid QR code.")

        fp = discord.File(file, "qr.png")

        await ctx.send(
            "**Warning**: Not all QRs on DIscord are safe! Be careful what you scan, it could compromise your account.",
            file=fp
        )

    @qr.command(name="read", aliases=["parse", "d", "decode"])
    async def qr_read(self, ctx, *, img):
        """Decode a QR code given an URL or attached image."""

        converted_img = await process_qr(ctx, img)
        if converted_img is None:
            return

        async with ctx.bot.session.post(
                "https://api.qrserver.com/v1/read-qr-code/", data={"file": converted_img}) as resp:
            out = await resp.json()

        try:
            read_out = out[0]["symbol"][0]["data"]
            assert read_out is not None
            # Escaping mentions is normally not needed. Then again, why the hell did you make a QR to ping someone?
            to_send = discord.utils.escape_mentions(discord.utils.escape_markdown(read_out))
            if len(read_out) > 6000:
                try:
                    hastebin_url = await ctx.bot.post_to_hastebin(read_out)
                    await ctx.send(hastebin_url)
                except (aiohttp.ContentTypeError, AssertionError):
                    fp = discord.File(io.BytesIO(read_out.encode("utf-8")), "out.txt")
                    await ctx.send("Your output was too long for Discord, and hastebin is not working.", file=fp)
            else:
                emb = discord.Embed(color=ctx.bot.embed_color, description=to_send)
                await ctx.send(embed=emb)
        except (KeyError, AssertionError):
            await ctx.send(":x: Unable to read QR code.")

    @commands.command()
    async def color(self, ctx, *, code):
        """Get some information on a hex color."""

        code = code.lstrip("#").replace("0x", "")
        async with ctx.bot.session.get(f"https://api.alexflipnote.dev/color/{code}") as resp:
            if resp.status in [400, 404]:
                return await ctx.send("Hex code appears invalid.")
            out = await resp.json()

        emb = ctx.default_embed()
        emb.color = int(code, 16)

        async with ctx.bot.session.get(out["image_gradient"]) as resp:
            img = await resp.content.read()

        fp = discord.File(io.BytesIO(img), "gradient.png")
        emb.set_image(url="attachment://gradient.png")

        emb.add_field(name="Hex code", value=out["hex"])
        emb.add_field(name="Int code", value=out["int"])
        rgb_list = out["rgb"][3:]
        emb.add_field(name="RGB values", value=rgb_list)
        emb.add_field(name="Name", value=out["name"])
        emb.add_field(name="Brightness", value=out["brightness"])
        best_color = "Lighter" if out["blackorwhite_text"] == "#ffffff" else "Darker"
        emb.add_field(name="Text color", value=f"{best_color} text works best over this color.")

        await ctx.send(embed=emb, file=fp)


def setup(bot):
    bot.add_cog(Utilities())
