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

import asyncio
import logging
import os
import platform
import random
import textwrap
import traceback

import aiohttp
import asyncpg
import discord
import lavalink
from discord.ext import commands

import config
import redis
from ext.utils import BotNotInVC, Context, DJRequired, human_join, IsCustomBlacklisted, linecount, permissions_converter
from ext.utils import UserInWrongVC, UserNotInVC


class SuprKewlBot(commands.Bot):
    def __init__(self, extra_owners=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        extra_owners = extra_owners or []
        self.extra_owners = extra_owners

        self.embed_color = 0xf92f2f

        self.commands_used = 0
        self.messages_seen = 0

        self.redis = None
        self.session = None
        self.db_pool = None
        self.lavalink = None

        self.ps_task = self.loop.create_task(self.playingstatus())
        self.dbl_task = self.loop.create_task(self.dbl_guild_update())
        self.change_status = True
        self.owner_no_prefix = False

        startup_extensions = [
            "ext.about",
            "ext.crypto",
            "ext.econ",
            "ext.fun",
            "ext.help",
            "ext.img",
            "ext.markov",
            "ext.mod",
            "ext.music",
            "ext.owner",
            "ext.settings",
            "ext.stats",
            "ext.text",
            "ext.util",
            "jishaku"
        ]

        loaded = []
        for extension in startup_extensions:
            try:
                self.load_extension(extension)
                loaded.append(extension)
            except Exception as e:
                exc = f"{e.__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exc}")

        print("Loaded extensions: " + "\n" + "\n".join(textwrap.wrap(", ".join(loaded))))

    async def on_connect(self):
        if not self.redis:
            self.redis = redis.Redis()
            await self.redis.connect()
            await self.redis.execute("FLUSHDB")
        if not self.session:
            self.session = aiohttp.ClientSession()
        if not self.db_pool:
            self.db_pool = await asyncpg.create_pool(config.db_uri)
        if not self.lavalink:
            self.lavalink = lavalink.Client(self.user.id)
            self.lavalink.add_node(
                config.lavalink_ip,
                config.lavalink_port,
                config.lavalink_pw,
                "us",
                "us-west",
            )
            self.add_listener(
                self.lavalink.voice_update_handler, "on_socket_response"
            )

    async def on_ready(self):
        print(f"Logged in as {self.user.name} (UID {self.user.id})")
        print("-" * 8)
        print(f"discord.py {discord.__version__} | Python {platform.python_version()}")
        print("-" * 8)
        print("Use this link to invite this bot:")
        print(discord.utils.oauth_url(self.user.id))
        print("-" * 8)

    async def on_message(self, message):
        if not self.is_ready():
            return

        self.messages_seen += 1

        if message.author.bot:
            return
        else:
            ctx = await self.get_context(message)
            is_blacklisted, mod_id = await self.is_blacklisted(message.author.id)
            if ctx.valid and is_blacklisted:
                try:
                    await message.channel.send(
                        f"You are not allowed to use this bot. You were blacklisted by {mod_id}."
                    )
                except discord.Forbidden:
                    try:
                        await message.author.send(
                            f"You are not allowed to use this bot. You were blacklisted by {mod_id}."
                        )
                    except discord.Forbidden:  # NOT COOL
                        pass

                return

            await self.track_message(f"tracked_message {message.id}")

            if message.guild:
                if message.channel.permissions_for(message.guild.me).send_messages:
                    if message.guild.me in message.mentions:
                        ping_images = ("angery.gif", "eyes.png")

                        resp = await self.db_pool.fetchval(
                            "SELECT prefix FROM guilds WHERE guild_id = $1;", message.guild.id)

                        if resp:
                            emb = discord.Embed(
                                color=self.embed_color,
                                description=f":eyes: Who pinged? My prefix is `sk!` and the custom server prefix is "
                                            f"`{resp}`. If you are in a DM with me, or you are my owner, I do "
                                            f"not require a prefix."
                            )
                        else:
                            emb = discord.Embed(
                                color=self.embed_color,
                                description=":eyes: Who pinged? My prefix is `sk!`. If you are in a DM with me, or you "
                                            "are my owner, I do not require a prefix."
                            )
                        fname = os.path.join("assets", random.choice(ping_images))
                        ext = fname.split(".")[-1]
                        fname_finished = f"image.{ext}"
                        fp = discord.File(fname, fname_finished)
                        emb.set_image(url="attachment://" + fname_finished)

                        await message.channel.send(embed=emb, file=fp)

                    for m in message.mentions:
                        if await self.is_owner(m) and not await self.is_owner(message.author):
                            if message.guild.id in config.ignore_guilds:
                                break
                            try:
                                await message.channel.send("<:pingsock:700885664601997363>")
                            except discord.HTTPException:
                                pass

                    await self.process_commands(message)

                else:
                    if ctx.valid:
                        try:
                            await message.author.send(":x: I can't send messages there! Perhaps try again elsewhere?")
                        except discord.Forbidden:
                            pass
            else:
                await self.process_commands(message)

    async def on_command_completion(self, ctx):
        self.commands_used += 1

    async def on_message_edit(self, before, after):
        if not self.is_ready():
            return

        if after.author.bot or not before.content or not after.content or not after.guild:
            return

        if before.content == after.content or after.type != discord.MessageType.default:
            return

        await self.db_pool.execute(
            "INSERT INTO edit_snipes (guild_id, user_id, channel_id, message_id, before, after) VALUES "
            "($1, $2, $3, $4, $5, $6) ON CONFLICT (channel_id) DO UPDATE SET guild_id = $1, user_id = $2, "
            "message_id = $4, before = $5, after = $6;", after.guild.id, after.author.id, after.channel.id,
            after.id, before.content, after.content)

    async def on_message_delete(self, message):
        if not self.is_ready():
            return

        if message.guild:
            content = message.content
            message_type = 0
            if message.attachments:
                content = message.attachments[0].proxy_url
                message_type = 1
            if message.embeds:
                content = message.embeds[0].description
                if (content == discord.Embed.Empty):
                    content = "<unknown>"
                message_type = 2

            await self.db_pool.execute(
                "INSERT INTO snipes (guild_id, user_id, channel_id, message_id, message, msg_type) VALUES "
                "($1, $2, $3, $4, $5, $6) ON CONFLICT (channel_id) DO UPDATE SET user_id = $2, message_id = $4,"
                " message = $5, msg_type = $6;", message.guild.id, message.author.id, message.channel.id, message.id,
                content, message_type)

    async def on_raw_message_edit(self, payload):
        if not self.is_ready():
            return

        if "content" not in payload.data:
            return

        channel = self.get_channel(int(payload.data["channel_id"]))

        if channel is None:
            return

        message = channel._state._get_message(payload.message_id)
        if message is None:
            try:
                message = await channel.fetch_message(payload.message_id)
            except discord.HTTPException:
                return

        if await self.redis.exists(f"tracked_message {payload.message_id}"):
            await self.clear_messages(f"tracked_message {payload.message_id}")
        await self.process_commands(message)

    async def on_raw_message_delete(self, payload):
        if not self.is_ready():
            return

        if await self.redis.exists(payload.message_id):
            await self.clear_messages(payload.message_id)
            await self.redis.delete(payload.message_id)

    async def on_guild_remove(self, guild):
        await self.prune_tables(guild.id)

    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, "on_error"):
            return

        ignored = (commands.CommandNotFound,)
        quote_errors = (
            commands.UnexpectedQuoteError, commands.InvalidEndOfQuotedStringError, commands.ExpectedClosingQuoteError
        )
        bad_arg_errors = (commands.BadArgument, commands.BadUnionArgument)

        error = getattr(error, "original", error)

        def perms_list(perms):
            return human_join([permissions_converter[i] for i in perms], final="or")

        if isinstance(error, ignored):
            return

        elif isinstance(error, quote_errors):
            await ctx.send(
                "Your argument(s) had too many or too few quotes. Remember to match all opening quotes with closing"
                " quotes.")

        elif isinstance(error, (commands.MemberNotFound, commands.UserNotFound)):
            emb = ctx.default_embed()
            emb.add_field(
                name="Invalid/unknown user",
                value=":x: I could not find the user you are looking for. Check your spelling, or use an ID instead. "
                      "(Alternatively, I do not share any servers with that user.)"
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.MessageNotFound):
            emb = ctx.default_embed()
            emb.add_field(
                name="Invalid message",
                value=":x: I could not find that message. Do I have permission to read it?"
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.EmojiNotFound):
            emb = ctx.default_embed()
            emb.add_field(
                name="Unknown emoji",
                value=":x: I cannot use that emoji - am I in that emoji's server?"
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.ChannelNotFound):
            emb = ctx.default_embed()
            emb.add_field(
                name="Unknown channel",
                value=":x: I don't know what that channel is. Am I in its server?"
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.RoleNotFound):
            emb = ctx.default_embed()
            emb.add_field(
                name="Unknown role",
                value=":x: I don't know what that role is. Am I in its server?"
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, bad_arg_errors):
            await ctx.send(":x: Your argument(s) could not be converted.")

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"`{error.param.name}` is a missing required argument.")
            await ctx.send_help(ctx.command)

        elif isinstance(error, commands.DisabledCommand):
            emb = ctx.default_embed()
            emb.add_field(name="Disabled Command", value=f":x: `{ctx.prefix}{ctx.command}` has been disabled!")

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.NoPrivateMessage):
            emb = ctx.default_embed()
            emb.add_field(
                name="This command is disabled in DMs",
                value=f":x: `{ctx.prefix}{ctx.command}` can only be used in servers, not in DMs or DM groups."
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.CommandOnCooldown):
            retry = round(error.retry_after, 2)

            human_readable_cooldown = {
                commands.BucketType.default: "bot-wide",
                commands.BucketType.user: "per-user",
                commands.BucketType.guild: "server-wide",
                commands.BucketType.channel: "per-channel",
                commands.BucketType.member: "per-server, per-user",
                commands.BucketType.category: "per-category"
            }

            cooldown_type = human_readable_cooldown[error.cooldown.type]

            emb = ctx.default_embed()
            emb.add_field(
                name="Command on Cooldown",
                value=f"Woah there! You just triggered a {cooldown_type} cooldown trying to run "
                      f"`{ctx.prefix}{ctx.command}`. Wait {retry} seconds."
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.MissingPermissions):
            emb = ctx.default_embed()
            missing_perms = perms_list(error.missing_perms)
            emb.add_field(
                name="User Missing Permissions",
                value=f":x: Permission denied to run `{ctx.prefix}{ctx.command}`."
                      f" You need to be able to {missing_perms}."
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.BotMissingPermissions):
            emb = ctx.default_embed()
            missing_perms = perms_list(error.missing_perms)
            emb.add_field(
                name="Bot Missing Permissions",
                value=f":x: I don't have the proper permissions to run `{ctx.prefix}{ctx.command}`."
                      f" I need to be allowed to {missing_perms}."
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, commands.NotOwner):
            emb = ctx.default_embed()
            emb.add_field(
                name="Permission denied",
                value=f":x: You must be a bot owner to run `{ctx.prefix}{ctx.command}`."
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, UserNotInVC):
            emb = ctx.default_embed()
            emb.add_field(
                name="Not in voice channel",
                value=f":x: You must be connected to a voice channel to run `{ctx.prefix}{ctx.command}`."
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, BotNotInVC):
            emb = ctx.default_embed()
            emb.add_field(
                name="Bot not in voice channel",
                value=f":x: I must be connected to a voice channel to run `{ctx.prefix}{ctx.command}`."
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, UserInWrongVC):
            emb = ctx.default_embed()
            emb.add_field(
                name="User in wrong channel",
                value=f":x: You must be in the same voice channel as the bot to run `{ctx.prefix}{ctx.command}`."
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, DJRequired):
            emb = ctx.default_embed()
            emb.add_field(
                name="DJ role required",
                value=f":x: There are multiple people listening to music, so you need a role called 'DJ' to run "
                      f"`{ctx.prefix}{ctx.command}`."
            )

            return await ctx.send(embed=emb)

        elif isinstance(error, IsCustomBlacklisted):
            emb = ctx.default_embed()
            emb.add_field(
                name="Blacklisted command",
                value=f":x: `{ctx.prefix}{ctx.command}` has been disabled in this context. Have another user try again, "
                      f"or try again in another channel, server, or DM."
            )

            return await ctx.send(embed=emb)

        print(f"Ignoring exception in command {ctx.prefix}{ctx.command}:")

        traceback.print_exception(type(error), error, error.__traceback__)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)
        await self.invoke(ctx)

    async def is_owner(self, user):
        return await super().is_owner(user) or user.id in self.extra_owners

    async def track_message(self, message):
        if await self.redis.exists(message):
            return

        await self.redis.rpush(message, 0)
        await self.redis.expire(message, 3600)

    async def clear_messages(self, tracked_message):
        for message_data in await self.redis.lrange(tracked_message, 1, -1):
            channel_id, message_id = message_data.split(":")
            try:
                await self.http.delete_message(
                    int(channel_id), int(message_id))
            except discord.NotFound:
                pass

        await self.redis.execute("LTRIM", tracked_message, 0, 0)

    async def register_response(self, response, request):
        if await self.redis.exists(f"tracked_message {request.id}"):
            await self.redis.rpush(
                f"tracked_message {request.id}",
                f"{response.channel.id}:{response.id}"
            )

    async def playingstatus(self):
        await self.wait_until_ready()
        await asyncio.sleep(3)  # Sleep such that all users are loaded
        playing_statuses = [
            "",
            "and plotting pranks",
            "among us or whatever it's called",
            "at a robot party, brb",
            "attempting to find love",
            "being improved!",
            "being open source",
            "being SuprKewl!",
            "bit.ly/sk-bot",
            "chess with Carlsen",
            "chess with Fischer",
            "chess with Kasparov",
            "creeper? aw man",
            "creeping through the shadows",
            "doom",
            "eating robot food, brb",
            "help im stuck at this computer pretending to be a discord bot",
            "helping the community",
            "I don't game...",
            "idling",
            "living under the AGPL3!",
            "mafia",
            "minecraft",
            "meme-scrolling",
            "ping and run",
            "tag with other robots",
            "the attention game",
            "waiting for you to call me!",
            "werewolf",
            "with fire (i don't feel pain)",
            "with my dad, Too Laggy",
            "with my food",
            "with my Raspberry Pi",
            "with the community",
            "with the Discord API",
            "with your emotions",
            "you'd think these statuses would have more variety..."
        ]

        while self.is_ready() and self.change_status:
            status = random.choice(playing_statuses)
            status += f" | lurking in {len(self.guilds)} servers and watching over {len(self.users)} users..."

            await self.change_presence(activity=discord.Game(name=status), status=discord.Status.idle)
            await asyncio.sleep(120)

    async def dbl_guild_update(self):
        await self.wait_until_ready()

        while not self.is_closed():
            await self.session.post(
                f"https://discordbots.org/api/bots/{self.user.id}/stats",
                json=dict(server_count=len(self.guilds)),
                headers={"Content-Type": "application/json", "Authorization": config.dbl_token}
            )
            await asyncio.sleep(1800)

    async def close(self):
        if not self.session.closed:
            await self.session.close()
            await asyncio.sleep(0)
        self.redis.disconnect()  # yes this not a coro

        await self.prune_tables()

        await asyncio.wait_for(self.db_pool.close(), timeout=10.0)
        await super().close()

    async def post_to_hastebin(self, data):
        data = data.encode("utf-8")
        async with self.session.post("https://hastebin.com/documents", data=data) as resp:
            out = await resp.json()

        assert "key" in out

        return "https://hastebin.com/" + out["key"]

    @property
    def embed_footer(self):
        return random.choice((
            "Baby it's COOOOVID-19 outside...",
            "Did you know? If you are in a DM with me, you don't need to use a prefix.",
            "Don't run the code and no errors will appear.",
            "Don't watch the clock. Do what it does - keep moving.",
            "Everything in this universe is either a potato or not a potato.",
            "Hey babe! Can I buy- sorry- ship you a drink?",
            "I am Nobody, nobody is perfect, therefore I am perfect. - Dandi Daley Mackall",
            "I ate a clock just now - it was rather time-consuming.",
            "I dream of a better world where chickens can cross the road without having their motives called into"
            " serious question by members of another species.",
            "I think you're hot... but you're a dumpster fire.",
            "If coronavirus doesn't take you out... can I?",
            "If plan A fails, don't worry; there are still 25 more letters in the alphabet.",
            "I saw you from across the bar. Stay there.",
            "If two wrongs don't make a right, try three.",
            "If you work 8 hours a day as a regular worker, you may one day be promoted to boss and work 12 hours a"
            " day.",
            "Instant gratification takes too long - Carrie Fisher",
            "Interestingly enough, Moses owned the first cloud-synced tablet.",
            "It's called a miracle because it doesn't happen.",
            "Just read that 4,153,237 people got married last year, not to cause any trouble but shouldn't that be an"
            " even number?",
            "Man cannot live by bread alone; he must have peanut butter.",
            "May all your bacon burn.",
            "Regex by trial and error: Combining dots slashes and dots until a thing happens.",
            "The center of a donut is 100% fat free.",
            "The first law is that a robot shall not harm a human, or by inaction allow a human to come to harm.",
            "The second law is that a robot shall obey any instruction given to it by a human.",
            "The third law is that a robot shall avoid actions or situations that could cause it to come to harm "
            "itself.",
            "The word utopia is derived from the Latin 'Utopia', meaning 'nothing, impossible'.",
            "This sentence hass tree errors.",
            "There are two kinds of people at a party; the ones that want to stay and those who want to leave. The"
            " problem is they are usually married to each other.",
            "To succeed in life, you need three things; a wishbone, a backbone and a funny bone. - Reba McEntire",
            linecount(),
            "Without you my life is as empty as the supermarket shelf.",
            "You can edit a command invocation to change my response.",
            "You can't spell coronavirus without U and I.",
            "You can't spell quarantine without URAQT."
        ))

    async def is_blacklisted(self, user_id):
        blacklisted_by = await self.db_pool.fetchval("SELECT mod_id FROM blacklist WHERE user_id = $1;", user_id)

        if not blacklisted_by:
            return False, 0
        else:
            if not await self.is_owner(await self.fetch_user(user_id)):
                return True, blacklisted_by
            return False, 0

    async def prune_tables(self, guild_id=None):
        TO_PRUNE = ("guilds", "snipes", "edit_snipes")

        if guild_id is None:
            for table in TO_PRUNE:
                guilds_in_db = []
                async with self.db_pool.acquire() as conn:
                    async with conn.transaction():
                        async for record in conn.cursor(f"SELECT guild_id FROM {table}"):
                            guilds_in_db.append(record[0])
                guilds_to_remove = []

                for guild_id in guilds_in_db:
                    if not self.get_guild(guild_id):
                        guilds_to_remove.append(guild_id)

                if guilds_to_remove:
                    removal_count = len(guilds_to_remove)
                    await self.db_pool.execute(f"DELETE FROM {table} WHERE guild_id = any($1::bigint[])",
                                               guilds_to_remove)
                    logging.info(f"Removed {removal_count} guilds from table '{table}'.")
        else:
            for table in TO_PRUNE:
                await self.db_pool.execute(f"DELETE FROM {table} WHERE guild_id IN ($1);", guild_id)


async def get_pre(bot, message):
    pre = ["sk!"]
    if message.guild:
        set_prefix = await bot.db_pool.fetchval("SELECT prefix FROM guilds WHERE guild_id = $1;", message.guild.id)

        if set_prefix:
            pre.append(set_prefix)

    is_owner = await bot.is_owner(message.author)
    if isinstance(message.channel, discord.DMChannel) or (is_owner and not bot.owner_no_prefix):
        pre.append("")

    return pre
