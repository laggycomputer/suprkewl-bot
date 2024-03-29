# -*- coding: utf-8 -*-

"""
Copyright (C) 2021 Dante "laggycomputer" Dam

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
import uuid
from urllib.parse import quote as urlquote

import aiohttp
import discord
import gtts
import pyqrcode
import requests
from PIL import Image
import steam
from discord.ext import commands

import config
from .utils import async_executor, Embedinator, escape_codeblocks, format_json, human_join, human_timedelta
from .utils import purge_from_list

TO_READABLE_GAME = {
    "QUAKECRAFT": "Quake",
    "WALLS": "Walls",
    "PAINTBALL": "Paintball",
    "SURVIVAL_GAMES": "Blitz Survival Games",
    "TNTGAMES": "TNT Games",
    "VAMPIREZ": "VampireZ",
    "WALLS3": "Mega Walls",
    "ARCADE": "Arcade",
    "ARENA": "Arena",
    "UHC": "UHC Champions",
    "MCGO": "Cops and Crims",
    "BATTLEGROUND": "Warlords",
    "SUPER_SMASH": "Smash Heroes",
    "GINGERBREAD": "Turbo Kart Racers",
    "HOUSING": "Housing",
    "SKYWARS": "SkyWars",
    "TRUE_COMBAT": "Crazy Walls",
    "SPEED_UHC": "Speed UHC",
    "SKYCLASH": "SkyClash",
    "LEGACY": "Classic Games",
    "PROTOTYPE": "Prototype",
    "BEDWARS": "Bed Wars",
    "MURDER_MYSTERY": "Murder Mystery",
    "BUILD_BATTLE": "Build Battle",
    "DUELS": "Duels",
    "SKYBLOCK": "SkyBlock",
    "PIT": "Pit"
}

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
    qr = pyqrcode.create(data, error="L")
    qr.png(fp)
    fp.seek(0)
    img = Image.open(fp)
    img = img.resize((img.width * 4, img.height * 4))
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
                Image.open(io.BytesIO(await resp.content.read())).convert("RGB")
                is_found = True
            except OSError:
                await ctx.send(":x: That URL is not an image.")
                return
    except aiohttp.InvalidURL:
        await ctx.send(":x: That URL is invalid.")
        return

    if not is_found:
        return None

    return url


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
        ign = get_by_name["name"]
    else:
        try:
            uuid = ign
            ign = get_by_uuid[-1]["name"]
        except KeyError:
            if not silent:
                await ctx.send(":x: Your input could not be interpreted as a UUID or currently valid name.")
            return

    return uuid, ign


async def insert_past_names(db_pool, names, player_uuid):
    uuid_bytes = uuid.UUID(player_uuid).bytes
    for past_name in names:
        if not await db_pool.fetchval("SELECT EXISTS(SELECT 1 from past_igns WHERE past_ign = $1);", past_name.lower()):
            await db_pool.execute(
                "INSERT INTO past_igns (past_ign, uuid) VALUES ($1, $2) ON CONFLICT DO NOTHING;", past_name.lower(),
                uuid_bytes)


def determine_rank(player_data):
    found_rank = None
    rank_lookup = {
        "YOUTUBER": "YOUTUBE",
        "SUPERSTAR": "MVP++",
        "MVP_PLUS": "MVP+",
        "MVP": "MVP",
        "VIP_PLUS": "VIP+",
        "VIP": "VIP",
        "NONE": "NON",
        "NORMAL": "NON"
    }

    if "prefix" in player_data["player"]:
        found_rank = player_data["player"]["prefix"]
        while "§" in found_rank:
            index = found_rank.index("§")
            if index != len(found_rank) - 1:
                found_rank = found_rank[:index] + found_rank[index + 2:]
    else:
        if "rank" in player_data["player"]:
            found_rank = "[%s]" % (
                    rank_lookup.get(player_data["player"]["rank"], None) or player_data["player"]["rank"])
        else:
            if "monthlyPackageRank" in player_data["player"] and player_data["player"]["monthlyPackageRank"] != "NONE":
                found_rank = "[%s]" % rank_lookup.get(
                    player_data["player"]["monthlyPackageRank"], None
                ) or player_data["player"]["monthlyPackageRank"]
            else:
                if "newPackageRank" in player_data["player"]:
                    found_rank = "[%s]" % rank_lookup.get(
                        player_data["player"]["newPackageRank"], None) or player_data["player"]["newPackageRank"]
                else:
                    if "packageRank" in player_data["player"]:
                        found_rank = "[%s]" % rank_lookup.get(
                            player_data["player"]["packageRank"], None
                        ) or player_data["player"]["packageRank"]
                    else:
                        pass
    return found_rank or "[NON]"


def rate(good_count, bad_count, verbose=True):
    if bad_count == 0:
        bad_count = 1

    if verbose:
        return f"{round(good_count / bad_count, 3)} ({good_count:,}/{bad_count:,})"
    else:
        return f"{round(good_count / bad_count, 3)}"


async def get_econ_data_for_item(ctx, records):
    economy_ids = [ctx.cog.tf2_schema_id_to_economy_id.get(r["id"], None) for r in records]

    economy_ids_to_send = economy_ids.copy()
    purge_from_list(economy_ids_to_send, None)

    params = {"key": config.steam_key, "format": "json", "language": "en", "appid": "440",
              "class_count": len(economy_ids_to_send)}

    for i, id in enumerate(economy_ids_to_send):
        params["classid" + str(i)] = id

    ret = [(None, None) for _ in range(len(records))]

    if economy_ids_to_send:
        async with ctx.bot.session.get("https://api.steampowered.com/ISteamEconomy/GetAssetClassInfo/v0001",
                                       params=params) as resp:
            class_info = await resp.json()

        for economy_id, data in class_info["result"].items():
            if economy_id == "success":  # Wait, that's not an ID!
                continue

            icon_url = "https://steamcommunity-a.akamaihd.net/economy/image/" + data["icon_url"]
            wiki_link = data["actions"]["0"]["link"]
            ret[economy_ids.index(int(economy_id))] = icon_url, wiki_link

    return ret


async def create_embed_for_item(ctx, record, schema_overview, econ_info):
    class_key = {}

    # Sort classes by the order they appear in the class menu:
    for i, v in enumerate(("scout", "soldier", "pyro", "demoman", "heavy", "engineer", "medic", "sniper", "spy")):
        class_key[v] = i

    classes_allowed = await ctx.bot.db_pool.fetch("SELECT class FROM tf2idb_class WHERE id = $1;", record["id"])
    classes_allowed = [rec[0] for rec in classes_allowed]
    classes_allowed.sort(key=lambda c: class_key[c])
    classes_allowed = ", ".join([c.title() for c in classes_allowed])

    attrs = schema_overview["result"]["attributes"]

    attrs_to_render = []
    item_attrs = await ctx.bot.db_pool.fetch(
        "SELECT attribute, value FROM tf2idb_item_attributes WHERE id = $1;", record["id"])
    for attr_record in item_attrs:
        attr_id, values = attr_record["attribute"], attr_record["value"].split(" ")
        for attribute in attrs:
            if attribute["defindex"] == attr_id:
                attr_desc = attribute.get("description_string", None)
                if attr_desc is not None and not attribute["hidden"]:
                    if attribute["effect_type"] == "positive":
                        prefix = "+ "
                    elif attribute["effect_type"] == "negative":
                        prefix = "- "
                    else:
                        prefix = "  "

                    for i, v in enumerate(values):
                        if "percentage" in attribute.get("description_format", ""):
                            if "additive" not in attribute.get("description_format", ""):
                                attr_desc = attr_desc.replace(f"%s{i + 1}", str(round((float(v) - 1) * 100)))
                            else:
                                attr_desc = attr_desc.replace(f"%s{i + 1}", str(round(float(v) * 100)))
                        else:
                            attr_desc = attr_desc.replace(f"%s{i + 1}", str(v))

                    attrs_to_render.append(prefix + attr_desc)
    emb = ctx.default_embed()

    emb.add_field(name="Name", value=record["name"])
    emb.add_field(name="Item ID", value=record["id"])
    emb.add_field(name="Allowed classes", value=classes_allowed or "N/A")
    minlevel = record["min_ilevel"]
    maxlevel = record["max_ilevel"]
    if minlevel is None and maxlevel is None:
        fmt_level = "N/A"
    else:
        if minlevel is None:
            minlevel = maxlevel
        if maxlevel is None:
            maxlevel = minlevel
        if minlevel != maxlevel:
            fmt_level = f"{minlevel}-{maxlevel}"
        else:
            fmt_level = minlevel
    emb.add_field(name="Level", value=fmt_level)
    emb.add_field(name="Equip slot", value=(record["slot"] or "None").title())
    if attrs_to_render:
        joined = "\n".join(attrs_to_render)
        emb.add_field(name="Attributes", value=f"```diff\n{joined}\n```", inline=False)

    found_price_data = None
    for item in ctx.cog.steamodd_prices:
        if int(item.name) == record["id"]:
            found_price_data = (item.base_price[u"USD"], item.price[u"USD"])

    if found_price_data:
        base_price, current_price = found_price_data
        if base_price == current_price:
            emb.add_field(name="Price (on Steam)", value="$%.2f USD" % current_price)
        else:
            emb.add_field(name="Price (on Steam)", value="~~$%.2f~~ $%.2f USD" % (base_price, current_price))

    icon_url, wiki_link = econ_info
    if icon_url is not None:
        emb.set_image(url=icon_url)
    if wiki_link is not None:
        emb.add_field(name="Wiki page", value=f"[Click]({wiki_link})")

    return emb


class Utilities(commands.Cog):
    def __init__(self):
        self.tf2i_initialized = False
        try:
            params = dict(language="en_US", format="json", key=config.steam_key)
            resp = requests.get("https://api.steampowered.com/IEconItems_440/GetSchemaOverview/v0001/", params=params)
            self.tf2_schema_overview = resp.json()

            steam.api.key.set(config.steam_key)
            self.steamodd_prices = steam.items.assets(440, aggressive=True, currency="USD")

            resp = requests.get("https://api.steampowered.com/ISteamEconomy/GetAssetPrices/v0001/?appid=440",
                                params=params)
            econ_items = resp.json()["result"]["assets"]
            self.tf2_schema_id_to_economy_id = {}

            for item in econ_items:
                self.tf2_schema_id_to_economy_id[int(item["name"])] = int(item["classid"])

            self.tf2i_initialized = True

        except Exception:
            pass

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
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                fp = discord.File(fp, "out.mp3")
                return fp

        await ctx.send(":white_check_mark:", file=await save())

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
        sniped = await ctx.bot.db_pool.fetch(
            "SELECT * FROM snipes WHERE channel_id = $1 AND guild_id = $2;", channel.id, ctx.guild.id)

        if not sniped:
            return await ctx.send("Nothing to snipe... yet.")
        if channel.is_nsfw() is True and ctx.channel.is_nsfw() is False:
            return await ctx.send("You cannot snipe from a normal channel into an NSFW one.")

        user_perms = ctx.author.permissions_in(channel)
        if not user_perms.read_messages or not user_perms.read_message_history:
            return await ctx.send(":x: You cannot see that channel.")

        fetched = sniped[0]

        guild = ctx.bot.get_guild(fetched["guild_id"])
        if guild is None:
            return await ctx.send(":x: Unable to fetch some data.")
        user = ctx.bot.get_user(fetched["user_id"])
        if not user:
            user = await ctx.bot.fetch_user(fetched["user_id"])
            if user is None:
                return await ctx.send(":x: Unable to fetch some data.")
        chnl = discord.utils.get(guild.text_channels, id=fetched["channel_id"])
        if chnl is None:
            return await ctx.send(":x: Unable to fetch some data.")
        message_id = fetched["message_id"]
        msg_content = fetched["message"]

        e = ctx.default_embed()
        if fetched["msg_type"] == 1:
            e.description = "The image may not be visible"
            e.set_author(name=f"{user.name} sent in {chnl.name}")
            e.set_image(url=msg_content)
        elif fetched["msg_type"] == 2:
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
        sniped_from_db = await ctx.bot.db_pool.fetchrow(
            "SELECT * FROM edit_snipes WHERE channel_id = $1 AND guild_id = $2;", channel.id, ctx.guild.id)

        if not sniped_from_db:
            return await ctx.send("Nothing to snipe... yet.")
        if channel.is_nsfw() is True and ctx.channel.is_nsfw() is False:
            return await ctx.send("You cannot snipe from a normal channel into an NSFW one.")

        user_perms = ctx.author.permissions_in(channel)
        if not user_perms.read_messages or not user_perms.read_message_history:
            return await ctx.send(":x: You cannot see that channel.")

        e = ctx.default_embed()
        guild = ctx.bot.get_guild(sniped_from_db["guild_id"])
        if guild is None:
            return await ctx.send(":x: Unable to fetch some data.")
        user = ctx.bot.get_user(sniped_from_db["user_id"])
        if not user:
            user = await ctx.bot.fetch_user(sniped_from_db["user_id"])
            if user is None:
                return await ctx.send(":x: Unable to fetch some data.")
        chnl = discord.utils.get(guild.text_channels, id=sniped_from_db["channel_id"])
        if chnl is None:
            return await ctx.send(":x: Unable to fetch some data.")
        message_id = sniped_from_db["message_id"]
        before = sniped_from_db["before"]
        after = sniped_from_db["after"]

        e.add_field(name="Before", value=before, inline=False)
        e.add_field(name="After", value=after, inline=False)
        e.add_field(name="Message link",
                    value=f"[Here](https://discord.com/channels/{guild.id}/{chnl.id}/{message_id})")

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

        potential_past_uuids = []

        async with ctx.bot.db_pool.acquire() as conn:
            async with conn.transaction():
                async for record in conn.cursor("SELECT uuid from past_igns WHERE past_ign = $1;", ign.lower()):
                    potential_past_uuids.append(str(record[0]))

        names_to_use = []
        for potential_past_uuid in potential_past_uuids:
            resolved = await name_resolve(ctx, potential_past_uuid, silent=True)
            if resolved is not None:
                might_append = resolved[1].lower()
                if might_append != ign.lower():
                    names_to_use.append(might_append)

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
            emb_name = f"The name {discord.utils.escape_markdown(name)} has UUID `{human_uuid}`."
            if names_to_use:
                past_warning = f"\n(Note: `{ign}` is also a former name of {human_join(names_to_use, final='and')}.)"
        else:
            try:
                name = get_by_uuid[-1]["name"]
            except KeyError:
                return await ctx.send(":x: Your input could not be interpreted as a UUID or currently valid name.")
            player_uuid = ign
            human_uuid = '-'.join(player_uuid[i:i + 4] for i in range(0, len(player_uuid), 4))
            emb_name = f"UUID `{human_uuid}` resolves to the name {discord.utils.escape_markdown(name)}."
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

        await insert_past_names(ctx.bot.db_pool, past_names, player_uuid)

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
            await insert_past_names(ctx.bot.db_pool, [resp["name"].lower()], resp["id"])
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

        emb.description = discord.utils.escape_markdown(f"{determine_rank(data)} {ign}")

        if "networkExp" in data["player"]:
            exp = data["player"]["networkExp"]

            def calc_lev(xp):
                level_and_decimal = (math.sqrt(xp + 15312.5) - 125 / math.sqrt(2)) / (25 * math.sqrt(2))
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

        if "lastLogin" in data["player"] and "lastLogout" in data["player"]:
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
                game = status_data["session"]["gameType"]
                version = data["player"].get("mcVersionRp", None)
                converted = TO_READABLE_GAME.get(game, f"`{game.lower()}`")
                online_field = f"Yes, playing {converted}"
                if version is not None:
                    online_field += f" on game version `{version}`"
                online_field += "."
                emb.add_field(name="Online?", value=online_field)
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

    @commands.command(name="bedwars", aliases=["bw", "bedwar", "bewdar"])
    async def bedwars(self, ctx, *, ign):
        """Get BedWars statistics on an IGN."""

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

        emb = ctx.default_embed()
        emb.set_thumbnail(url=f"https://crafatar.com/renders/body/{uuid}?overlay")

        emb.description = discord.utils.escape_markdown(f"{determine_rank(data)} {ign}")

        bw_data = data["player"]["stats"]["Bedwars"]
        winstreak = bw_data.get("winstreak", 0)
        emb.add_field(name="Winstreak", value=f"{winstreak:,}")
        winloss = rate(bw_data.get("wins_bedwars", 0), bw_data.get("losses_bedwars", 0))
        emb.add_field(name="Win/Loss", value=winloss)

        def bw_stars(exp):
            level = int(100 * int(exp / 487000))
            exp %= 487000
            if exp < 500:
                return level + exp / 500
            level += 1
            if exp < 1500:
                return level + (exp - 500) / 1000
            level += 1
            if exp < 3500:
                return level + (exp - 1500) / 2000
            level += 1
            if exp < 7000:
                return level + (exp - 3500) / 3500
            level += 1
            exp -= 7000
            return level + exp / 5000

        stars = bw_stars(bw_data.get("Experience", 0))
        stars, decimal = divmod(stars, 1)
        stars = int(stars)
        emb.add_field(name="Stars", value=f"{stars:,}, {round(decimal * 100)}% to next")

        kdr = rate(bw_data.get("kills_bedwars", 0), bw_data.get("deaths_bedwars", 0))
        fkdr = rate(bw_data.get("final_kills_bedwars", 0), bw_data.get("final_deaths_bedwars", 0))
        emb.add_field(name="KDR (FKDR)", value=f"{kdr} ({fkdr})")

        bedrate = rate(bw_data.get("beds_broken_bedwars", 0), bw_data.get("beds_lost_bedwars", 0))
        emb.add_field(name="Bed rate (beds broken/beds lost)", value=bedrate)

        games_played = bw_data.get("wins_bedwars", 0) + bw_data.get("losses_bedwars", 0)

        coins = bw_data.get("coins", 0)
        emb.add_field(name="Coins", value=f"{coins:,}")

        kpg = rate(bw_data.get("kills_bedwars", 0), games_played, verbose=False)
        emb.add_field(name="Average kills/game", value=kpg)

        fkpg = rate(bw_data.get("final_kills_bedwars", 0), games_played, verbose=False)
        emb.add_field(name="Average final kills/game", value=fkpg)

        bpg = rate(bw_data.get("beds_broken_bedwars", 0), games_played, verbose=False)
        emb.add_field(name="Average beds/game", value=bpg)

        emb.add_field(name="Full stats here:",
                      value=f"[Plancke](https://plancke.io/hypixel/player/stats/{uuid}#BedWars)",
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
            "**Warning**: Not all QRs on Discord are safe! Be careful what you scan, it could compromise your account.",
            file=fp
        )

    @qr.command(name="read", aliases=["parse", "d", "decode"])
    async def qr_read(self, ctx, *, img=None):
        """Decode a QR code given an URL or attached image."""

        converted_url = await process_qr(ctx, img)
        if converted_url is None:
            return

        async with ctx.bot.session.post(
                "https://api.qrserver.com/v1/read-qr-code/", data={"fileurl": converted_url}) as resp:
            out = await resp.json()

        try:
            read_out = out[0]["symbol"][0]["data"]
            assert read_out is not None

            if not read_out:
                await ctx.send("QR empty.")

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
        async with ctx.bot.session.get(f"https://api.alexflipnote.dev/color/{code}",
                                       headers=dict(Authorization=config.flipnote_key)
                                       ) as resp:
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

    @commands.command(aliases=["tf2i"])
    async def tf2item(self, ctx, limit: typing.Optional[int] = 10, *, query):
        """Search for TF2 items."""

        if not 0 < limit <= 25:
            return await ctx.send("Invalid limit, use something between 1 and 25 inclusive.")

        if not ctx.cog.tf2i_initialized:
            return await ctx.send("This command is not available at this time. Blame Valve's API.")

        sent = await ctx.send("Fetching...")

        items = await ctx.bot.db_pool.fetch(
            "SELECT * FROM tf2idb_item WHERE similarity(name, $1) > 0.1 ORDER BY similarity(name, $1) DESC LIMIT $2;",
            query, limit)

        try:
            int(query)
            by_exact_id = await ctx.bot.db_pool.fetchrow("SELECT * FROM tf2idb_item WHERE id = $1;", int(query))
            if by_exact_id and int(query) not in [r["id"] for r in items]:
                items = [by_exact_id] + items
        except ValueError:
            pass

        if not items:
            return await ctx.send(f"{ctx.author.mention} No items found. Try something else?")

        econ_data = await get_econ_data_for_item(ctx, items)

        embeds = []
        for record, econ_info in zip(items, econ_data):
            embeds.append(await create_embed_for_item(ctx, record, self.tf2_schema_overview, econ_info))

        emb = Embedinator(ctx.bot, ctx, ctx.author, color=ctx.bot.embed_color)
        emb.embed_list = embeds

        emb.set_footer(text="When's the heavy update?", icon_url=ctx.me.avatar_url)
        await sent.delete()
        await emb.send()
        await emb.handle()


def setup(bot):
    bot.add_cog(Utilities())
