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

import math
import re

import discord
import lavalink
from discord.ext import commands

from .utils.errors import BotNotInVC, DJRequired, UserInWrongVC, UserNotInVC

TIME_RE = re.compile("-?[0-9]+")
URL_RE = re.compile("https?://(?:www.)?.+")


def requires_dj():
    async def pred(ctx):
        try:
            await ctx.cog.cog_check(ctx)  # hackerman
        except commands.CheckFailure as exc:
            raise exc from None

        if await ctx.bot.is_owner(ctx.author):
            return True

        player = ctx.bot.lavalink.player_manager.players.get(ctx.guild.id)
        if not player:
            return

        jammers = 0
        states = ctx.author.voice.channel.voice_states
        states.pop(ctx.bot.user.id)
        for id, state in states.items():
            if not (state.deaf or state.self_deaf):
                jammers += 1

        if jammers <= 1:
            return True
        else:
            has_dj = False
            if ctx.author.guild_permissions.administrator:
                has_dj = True
            for r in ctx.guild.roles:
                if r.name.strip().upper() == "DJ":
                    if ctx.author in r.members:
                        has_dj = True

            if ctx.command.name == "skip" and player.current.requester == ctx.author.id:
                return True
            elif ctx.command.name == "playskip":
                songs = [player.current] + player.queue
                for s in songs:
                    if s.requester != ctx.author.id and not has_dj:
                        raise DJRequired
            else:
                try:
                    assert has_dj
                    return has_dj
                except AssertionError:
                    raise DJRequired from None

    return commands.check(pred)


class Music(commands.Cog):
    """Some commands require a role called "DJ" when multiple people are in the same voice channel."""

    def __init__(self, bot):
        self.bot = bot

    def cog_load(self):
        self.bot.lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def track_hook(self, event):
        if isinstance(event, lavalink.TrackStartEvent):
            channel = event.player.fetch("channel")
            if channel:
                channel = self.bot.get_channel(channel)
                if channel:
                    duration = lavalink.utils.format_time(event.track.duration)
                    await channel.send(
                        f"Now playing `{event.track.title}` of duration `{duration}`."
                    )
        elif isinstance(event, lavalink.TrackEndEvent):
            channel = event.player.fetch("channel")
            if channel:
                channel = self.bot.get_channel(channel)
                if len(event.player.queue) == 0:
                    await event.player.stop()
                    await self.connect_to(channel.guild.id, None)
                    return await channel.send("Queue is empty, disconnecting.")

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    async def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage

        if (isinstance(ctx.guild.region, str)):
            region = ctx.guild.region
        else:
            region = ctx.guild.region.value

        player = self.bot.lavalink.player_manager.create(
            ctx.guild.id, endpoint=region
        )

        should_connect = ctx.command.name in [
            "play",
            "playskip",
            "nowplaying",
            "seek",
            "skip",
            "stop",
            "pause",
            "volume",
            "disconnect",
            "queue",
            "remove",
            "musicplayer",
        ]

        does_not_require_user_connect = ctx.command.name in [
            "nowplaying",
            "queue",
            "musicplayer"
        ]

        if (ctx.author.voice is None or ctx.author.voice.channel is None) and not does_not_require_user_connect:
            if not (player.is_connected and await ctx.bot.is_owner(ctx.author)):
                raise UserNotInVC

        if not player.is_connected:
            if not should_connect:
                raise BotNotInVC

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect:
                raise commands.BotMissingPermissions(["connect"])

            if not permissions.speak:
                raise commands.BotMissingPermissions(["speak"])

            player.store("channel", ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        if ctx.author.voice and player.is_connected and int(player.channel_id) != ctx.author.voice.channel.id:
            raise UserInWrongVC

        return True

    @commands.command(aliases=["p", "pl", "ply"])
    async def play(self, ctx, *, query):
        """Play or enqueue a track."""

        player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

        query = query.strip("<>")

        if not URL_RE.match(query):
            query = f"ytsearch:{query}"

        results = await player.node.get_tracks(query)

        if not results or not results["tracks"]:
            return await ctx.send(":grey_question: No track found.")

        e = ctx.colored_embed

        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            e.set_author(name=f"Playlist queued by {ctx.author}")
            e.description = f"{results['playlistInfo']['name']} - {len(tracks)} tracks"
            e.set_footer(text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)
        else:
            track = results["tracks"][0]
            e.set_author(name=f"Track queued by {ctx.author}")
            e.description = f"[{track['info']['title']}]({track['info']['uri']})"
            e.set_footer(text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            player.add(requester=ctx.author.id, track=track)
            await ctx.send(embed=e)

        if not player.is_playing:
            await player.play()

    @commands.command(aliases=["ps", "plys"])
    @requires_dj()
    async def playskip(self, ctx, *, query: str):
        """Play a track, skipping through all tracks in the queue, if any."""

        player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

        query = query.strip("<>")

        if not URL_RE.match(query):
            query = f"ytsearch:{query}"

        results = await player.node.get_tracks(query)

        if not results or not results["tracks"]:
            return await ctx.send(":grey_question: No track found.")

        await player.stop()

        e = ctx.colored_embed

        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            e.set_author(name=f"Skipping to playlist queued by {ctx.author}")
            e.description = f"{results['playlistInfo']['name']} - {len(tracks)} tracks"
            e.set_footer(text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)
        else:
            track = results["tracks"][0]
            e.set_author(name=f"Skipping to track queued by {ctx.author}")
            e.description = f"[{track['info']['title']}]({track['info']['uri']})"
            e.set_footer(text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=e)
            player.add(requester=ctx.author.id, track=track)

        await player.play()

    @commands.command(aliases=["np", "n", "playing", "now"])
    async def nowplaying(self, ctx):
        """Show the track currently playing in this server."""

        player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

        position = lavalink.utils.format_time(player.position)
        if player.current and player.current.stream:
            duration = "Live"
        else:
            duration = lavalink.utils.format_time(player.current.duration)

        e = discord.Embed(
            color=ctx.bot.embed_color,
            description=f"[{player.current.title}]({player.current.uri})",
        )
        e.add_field(name="Duration", value=f"[{position}/{duration}]")
        e.set_footer(text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=e)

    @commands.command()
    @requires_dj()
    async def seek(self, ctx, *, time):
        """Move to a different point in the track."""

        player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

        if player.current is None:
            return await ctx.send(":x: Nothing is playing!")

        seconds = TIME_RE.search(time)
        if not seconds:
            return await ctx.send(
                ":grey_question: Please specify a time in seconds to seek to."
            )

        seconds = int(seconds.group()) * 1000
        if time.startswith("-"):
            seconds *= -1

        track_time = player.position + seconds
        if not 0 <= track_time <= player.current.duration:
            return await ctx.send(":x: You can't seek that far!")

        await player.seek(track_time)
        await ctx.send(f":ok_hand: Moved track to `{lavalink.utils.format_time(track_time)}`")

    @commands.command(aliases=["sk", "s"])
    @requires_dj()
    async def skip(self, ctx):
        """Skip the track currently playing."""

        player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

        await player.skip()
        await ctx.send(":track_next: Skipped.")

    @commands.command(aliases=["st"])
    @requires_dj()
    async def stop(self, ctx):
        """Stops the track currently playing and empties the queue."""

        player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

        player.queue.clear()
        await player.stop()
        await ctx.send(":stop_button: Stopped.")

    @commands.command(aliases=["resume", "res", "r"])
    @requires_dj()
    async def pause(self, ctx):
        """Pause the track currently playing."""

        player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

        if player.paused:
            await player.set_pause(False)
            await ctx.send(":play_pause: Resumed.")
        else:
            await player.set_pause(True)
            await ctx.send(":pause_button: Paused.")

    @commands.command(aliases=["vol"])
    @requires_dj()
    async def volume(self, ctx, volume: int = None):
        """Change the volume level of the music player."""

        player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

        if not volume:
            return await ctx.send(
                f":speaker: My current player volume is `{player.volume}`%."
            )

        await player.set_volume(volume)
        await ctx.send(f":speaker: Set player volume to `{player.volume}`%.")

    @commands.command(aliases=["dc", "dcon"])
    @requires_dj()
    async def disconnect(self, ctx):
        """Disconnect from the voice channel and empty the queue."""

        player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx.guild.id, None)
        await ctx.send(":ok_hand: Disconnected.")

    @commands.command(aliases=["q"])
    async def queue(self, ctx, page: int = 1):
        """Show the player's queue."""

        player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send(":x: Nothing queued.")

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_list = ""
        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f"{index + 1} - [{track.title}]({track.uri})\n"

        e = discord.Embed(colour=ctx.bot.embed_color, description=queue_list)
        e.set_author(name=f"There are {len(player.queue)} tracks in the queue (page {page}/{pages}):")
        e.set_footer(
            text=f"To change pages use \"{ctx.prefix}{ctx.command} page\", replacing page with the desired page number."
        )
        await ctx.send(embed=e)

    @commands.command(aliases=["rm"])
    @requires_dj()
    async def remove(self, ctx, index: int):
        """Remove a certain track from the queue."""

        player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

        if index > len(player.queue) or index < 1:
            return await ctx.send(
                f":grey_question: Invalid index, please use an index in the range `1`-`{len(player.queue)}`."
            )

        index -= 1
        removed = player.queue.pop(index)

        await ctx.send(f":eject: Removed `{removed.title}` from the queue.")

    @commands.command(name="musicplayer", aliases=["mp"])
    async def music_player(self, ctx):
        """Get info on the server music player."""

        player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)

        position = lavalink.utils.format_time(player.position)
        if player.current and player.current.stream:
            duration = "Live"
        else:
            duration = lavalink.utils.format_time(player.current.duration)

        is_paused = "Yes" if player.paused else "No"
        e = ctx.colored_embed
        e.set_author(name=f"Player info for {ctx.guild}")
        e.add_field(name="Volume", value=f"{player.volume}%/1000%", inline=False)
        e.add_field(
            name="Current track", value=f"[{player.current.title}]({player.current.uri})",
            inline=False
        )
        e.add_field(name="Duration", value=f"[{position}/{duration}]")
        e.add_field(name="Paused?", value=is_paused, inline=False)
        e.add_field(name="Shuffling queue?", value="Yes" if player.shuffle else "No")
        e.add_field(name="Looping queue?", value="Yes" if player.repeat else "No")

        e.set_footer(text=f"{ctx.bot.embed_footer} Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)

    @commands.command(name="shuffle", aliases=["shuf"])
    @requires_dj()
    async def shuffle_(self, ctx, *, shuffle: bool = None):
        """Toggle shuffle play."""

        player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)
        proposed_state = shuffle if shuffle is not None else not player.shuffle

        player.shuffle = proposed_state
        await ctx.send(f":twisted_rightwards_arrows: Shuffle play is now {'on' if proposed_state else 'off'}.")

    @commands.command(name="loop", aliases=["lp", "repeat", "rp"])
    @requires_dj()
    async def loop_(self, ctx, *, loop: bool = None):
        """Toggle shuffle play."""

        player = self.bot.lavalink.player_manager.players.get(ctx.guild.id)
        proposed_state = loop if loop is not None else not player.repeat

        player.repeat = proposed_state
        await ctx.send(f":repeat_one: Queue loop is now {'on' if proposed_state else 'off'}.")


def setup(bot):
    bot.add_cog(Music(bot))
