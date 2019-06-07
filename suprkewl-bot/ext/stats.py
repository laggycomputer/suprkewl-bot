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

    @commands.command(
        description="Generates a pie chart of those with a role and those without. If no role is specified, a pie-chart"
                    " is generated of members by their top role."
    )
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.guild_only()
    async def rolepie(self, ctx, *, role: discord.Role = None):
        """Generate a piechart of those who have <role>."""

        if ctx.guild.large:
            await ctx.bot.request_offline_members(ctx.guild)

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

    @commands.command(description="Sends a pie chart of users that are bots and those that are otherwise.")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.guild_only()
    async def botpie(self, ctx):
        """Make a pie chart of server bots."""

        if ctx.guild.large:
            await ctx.bot.request_offline_members(ctx.guild)

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

    @commands.command(
        description="Checks the number of people in the server that are listening to a certain song on Spotify."
                    " Defaults to the one you are listening to. The song name is case-insensitive."
    )
    @commands.guild_only()  # Member.activities seems to have no counterpart on User
    async def songcount(self, ctx, *, song=None):
        """Count members listening to a certain song on Spotify."""

        if ctx.guild.large:
            await ctx.bot.request_offline_members(ctx.guild)

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


def setup(bot):
    bot.add_cog(Stats())
