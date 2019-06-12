# -*- coding: utf-8 -*-

"""
Copyright (C) 2019 laggycomputer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import io
import os

import discord
from discord.ext import commands
import matplotlib.pyplot as plt


class Stats(commands.Cog):

    async def cog_before_invoke(self, ctx):
        if ctx.guild is not None:
            if ctx.guild.large:
                await ctx.bot.request_offline_members(ctx.guild)

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage
        else:
            return True

    @commands.group(aliases=["chart", "stat"], description="Generate a pie chart for guild attributes.")
    @commands.cooldown(1, 2, commands.BucketType.channel)
    async def pie(self, ctx):
        """Generate pie charts."""

        if ctx.invoked_subcommand is None:
            sent = await ctx.send(":x: You must specify a subcommand.")
            await ctx.register_response(sent)

    @pie.command(
        name="role",
        description="Generates a pie chart of those with a role and those without. If no role is specified, a pie-chart"
                    " is generated of members by their top role."
    )
    async def pie_role(self, ctx, *, role: discord.Role = None):
        """Generate a piechart of those who have <role>."""

        def pie_gen(ctx, role=None):
            m = ctx.guild.members
            guild_size = len(m)

            if role is None:
                roles = list(reversed(ctx.guild.roles))
                m_sorted = {}

                for r in roles:
                    m_sorted[r] = 0

                for member in m:
                    m_sorted[member.top_role] += 1

                to_del = []

                for r in m_sorted:
                    if m_sorted[r] == 0:
                        to_del.append(r)

                for t_d in to_del:
                    del m_sorted[t_d]

                prc = list(m_sorted[r] / guild_size * 100 for r in m_sorted)
                user_friendly_prc = list(f"{r.name}: {prc[list(m_sorted.keys()).index(r)]}%" for r in m_sorted)

                labels = list(r.name for r in roles)
                sizes = prc
                patches, _ = plt.pie(sizes, startangle=90)
                plt.legend(patches, labels, loc="best")
                plt.axis("equal")
                plt.tight_layout()

                fname = str(ctx.message.id) + ".png"

                plt.savefig(fname)

                fmt = "\n" + "\n".join(user_friendly_prc)
                fmt = fmt.replace("@everyone", "\\@everyone")

                return [fmt, fname]
            else:
                def _piegenerate(name1, name2, prc, fname):
                    labels = [name1, name2]
                    sizes = [prc, 100 - prc]
                    colors = ["lightcoral", "lightskyblue"]
                    patches, _ = plt.pie(sizes, colors=colors, startangle=90)
                    plt.legend(patches, labels, loc="best")
                    plt.axis("equal")
                    plt.tight_layout()
                    fname += ".png"
                    plt.savefig(fname)

                    return fname

                prc = (sum(member._roles.has(role.id) for member in m) / guild_size) * 100

                names = [f"Members with '{role.name}' role",
                         f"Members without '{role.name}' role"]
                fname = str(ctx.message.id)
                img_out = _piegenerate(names[0], names[1], prc, fname)
                fmt = f":white_check_mark: {prc}% of the server has the chosen role."

                return [fmt, img_out]

        fmt, fname = await ctx.bot.loop.run_in_executor(None, pie_gen, ctx, role)

        fp = discord.File(fname, filename="chart.png")

        if len(fmt) > 2000:
            fmt = io.BytesIO(fmt.encode("utf-8"))
            fp2 = discord.File(fmt, "key.txt")

            sent = await ctx.send(":white_check_mark: Attached is your output and pie-chart.", files=[fp, fp2])
        else:
            sent = await ctx.send(fmt, file=fp)

        await ctx.register_response(sent)
        os.remove(fname)

    @pie.command(
        name="bot",
        aliases=["bots"], description="Sends a pie chart of users that are bots and those that are otherwise."
    )
    async def pie_bot(self, ctx):
        """Make a pie chart of server bots."""

        def pie_gen():
            prc = sum(m.bot for m in ctx.guild.members) / len(ctx.guild.members) * 100

            labels = ["Bots", "Non-Bots"]
            sizes = [prc, 100 - prc]
            colors = ["lightcoral", "lightskyblue"]
            patches, _ = plt.pie(sizes, colors=colors, startangle=90)
            plt.legend(patches, labels, loc="best")
            plt.axis("equal")
            plt.tight_layout()
            fname = str(ctx.message.id) + ".png"
            plt.savefig(fname)

            return [fname, prc]

        fname, prc = await ctx.bot.loop.run_in_executor(None, pie_gen)

        fp = discord.File(fname, filename="piechart.png")

        sent = await ctx.send(f":white_check_mark: {prc}% of the server's members are bots.", file=fp)
        os.remove(fname)
        await ctx.register_response(sent)

    @pie.command(
        name="status", description="Sends a pie chart of users by status (online, idle, do-not-disturb, etc).")
    async def pie_status(self, ctx):
        """Generate a pie chart for the status of server members."""

        members = ctx.guild.members
        offline_count = sum(m.status == discord.Status.offline for m in members) / len(members) * 100
        idle_count = sum(m.status == discord.Status.idle for m in members) / len(members) * 100
        dnd_count = sum(m.status == discord.Status.dnd for m in members) / len(members) * 100
        online_count = sum(m.status == discord.Status.online for m in members) / len(members) * 100
        other_count = sum(isinstance(m.status, str) for m in members) / len(members) * 100

        def pie_gen():
            labels = ["Offline", "Idle", "Do Not Disturb", "Online"]
            sizes = [offline_count, idle_count, dnd_count, online_count]
            colors = ["gray", "#f1c40f", "#e74c3c", "#2ecc71"]
            if other_count:
                labels.append("Other/Unknown")
                sizes.append(other_count)
                colors.append("blue")
            patches, _ = plt.pie(sizes, colors=colors, startangle=90)
            plt.legend(patches, labels, loc="best")
            plt.axis("equal")
            plt.tight_layout()
            fname = str(ctx.message.id) + ".png"
            plt.savefig(fname)

            return fname

        fname = await ctx.bot.loop.run_in_executor(None, pie_gen)

        fp = discord.File(fname, filename="piechart.png")

        ret = f":white_check_mark:\n{offline_count}% of the server's members are offline.\n{idle_count}% of the" \
              f" server is idle.\n{dnd_count}% of the server is on do not disturb.\n{online_count}% of the server is" \
              f" online."
        if other_count:
            ret += f"\n{other_count}% of the server has an unknown status."

        sent = await ctx.send(ret, file=fp)
        os.remove(fname)
        await ctx.register_response(sent)

    @commands.command(
        description="Checks the number of people in the server that are listening to a certain song on Spotify."
                    " Defaults to the one you are listening to. The song name is case-insensitive."
    )
    async def songcount(self, ctx, *, song=None):
        """Count members listening to a certain song on Spotify."""

        def is_listening(member):
            if not len(member.activities):  # Member has no active activities
                return False

            return any(isinstance(a, discord.Spotify) for a in member.activities)

        def song_name_from(member):
            for activity in member.activities:
                if isinstance(activity, discord.Spotify):
                    return activity.title

        if song is None:
            if is_listening(ctx.author):
                song = song_name_from(ctx.author)
            else:
                sent = await ctx.send(
                    "You did not specify a song to count, and you are not listening to a song yourself. Please provide"
                    " a song name, or start listening to a song and try again."
                )
                return await ctx.register_response(sent)

        # The case insensitivity is for Spotify songs that have identical names but different cases
        count = sum(is_listening(m) and song_name_from(m).lower() == song.lower() for m in ctx.guild.members)

        if not count:
            msg = "Nobody is"
        elif count == 1:
            msg = "One member is"
        else:
            msg = str(count) + "members are"

        msg += f" listening to the song `{song}`."

        await ctx.register_response(await ctx.send(msg))

    @commands.command(
        description="Checks the number of people in the server that are playing a certain game."
                    " Defaults to the game you are playing, if any. The game name is case-insensitive."
    )
    async def gamecount(self, ctx, *, game=None):
        """Count members playing a certain game."""

        if ctx.guild.large:
            await ctx.bot.request_offline_members(ctx.guild)

        def has_game(member):
            if not len(member.activities):  # Member has no active activities
                return False

            return any(isinstance(a, discord.Game) for a in member.activities)

        def game_name_from(member):
            for activity in member.activities:
                if isinstance(activity, discord.Game):
                    return activity.name

        if game is None:
            if has_game(ctx.author):
                game = game_name_from(ctx.author)
            else:
                sent = await ctx.send(
                    "You did not specify a game, and you are not playing one yourself. Please provide"
                    " a game name, or start playing a game and try again."
                )
                return await ctx.register_response(sent)

        # Case insensitivity just in case
        count = sum(has_game(m) and game_name_from(m).lower() == game.lower() for m in ctx.guild.members)

        if not count:
            msg = "Nobody is"
        elif count == 1:
            msg = "One member is"
        else:
            msg = str(count) + "members are"

        msg += f" playing the game `{game}`."

        await ctx.register_response(await ctx.send(msg))

    @commands.command(
        description="Count the number of users in the guild with nicknames that start with common characters used to"
                    " name-hoist."
    )
    async def hoistcount(self, ctx):
        """Get potential name hoisters on the server."""

        cnt = 0
        hoist_chars = ["(", "/", "%", "-", "#", "$", "'", "*", "+", ".", "!"]
        for member in ctx.guild.members:
            if member.nick is not None:
                if member.nick[0] in hoist_chars:
                    cnt += 1

        chars = ", ".join(f"`{c}`" for c in hoist_chars)

        msg = f"{cnt} members have nicknames that start with one of the following characters: {chars}"

        sent = await ctx.send(msg)
        await ctx.register_response(sent)


def setup(bot):
    bot.add_cog(Stats())
