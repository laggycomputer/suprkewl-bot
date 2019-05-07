# -*- coding: utf-8 -*-

"""
Copyright (C) 2019  laggycomputer

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

import codecs
import datetime
import itertools
import os
import pathlib
import pkg_resources
import platform
import time

import discord
from discord.ext import commands
import pygit2

from .utils import time as t_utils


class About(commands.Cog):

    # Largely from R. Danny.
    def format_commit(self, commit):
        short, _, _ = commit.message.partition("\n")
        short_sha2 = commit.hex[0:6]
        commit_tz = datetime.timezone(
            datetime.timedelta(minutes=commit.commit_time_offset))
        commit_time = datetime.datetime.fromtimestamp(
            commit.commit_time).replace(tzinfo=commit_tz)

        offset = t_utils.human_timedelta(commit_time.astimezone(
            datetime.timezone.utc).replace(tzinfo=None), accuracy=1)
        return f"[`{short_sha2}`](https://github.com/laggycomputer/suprkewl-bot/commit/{commit.hex}) {short} ({offset})"

    def _get_last_commits(self, count=3):
        repo = pygit2.Repository("../.git")
        commits = list(itertools.islice(
            repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), count))
        return "\n".join(self.format_commit(c) for c in commits)

    def _linecount(self):
        path_to_search = "./"
        total = 0
        file_amount = 0
        for path, subdirs, files in os.walk(path_to_search):
            for name in files:
                    if name.endswith(".py"):
                        file_amount += 1
                        with codecs.open(path_to_search + str(pathlib.PurePath(path, name)), "r", "utf-8") as f:
                            for i, l in enumerate(f):
                                if l.strip().startswith("#") or len(l.strip()) is 0:
                                    pass
                                else:
                                    total += 1

        return f"I am made of {total:,} lines of Python, spread across {file_amount:,} files!"

    def _current_time(self):
        year, month, dayofmonth, hour, minute, second, dayofweek, _, isdst = time.localtime()
        week = ["Sunday", "Monday", "Tuesday",
                "Wednesday", "Thursday", "Friday", "Saturday"]
        dayofweek = week[dayofweek]
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "November", "December"
        ]
        month = months[month]
        disptime = f"{dayofweek}, {month} {dayofmonth}, {year}; {hour}:{minute}:{second}, Pacific Standard Time"
        if isdst:
            disptime += " (DST)"

        return disptime

    @commands.command()
    async def about(self, ctx):
        """Give some bot info."""

        emb = discord.Embed(
            name="Bot info", color=0xf92f2f,
            description=self._get_last_commits()
        )

        emb.add_field(name="Support Server", value="https://www.discord.gg/CRBBJVY")
        emb.add_field(name="Line count", value=self._linecount())
        emb.add_field(name="System Time", value=self._current_time())
        emb.add_field(name="Processor Type", value=platform.machine().lower())
        emb.add_field(
            name="OS version (short)",
            value=platform.system() + " " + platform.release()
        )
        emb.add_field(
            name="OS version (long)",
            value=platform.platform(aliased=True)
        )
        emb.add_field(
            name="Python Version", value=f"Python {platform.python_branch()}, build date {platform.python_build()[1]}"
        )
        emb.add_field(
            name="discord.py version",
            value=pkg_resources.get_distribution("discord.py").version
        )
        emb.add_field(
            name="Jishaku version",
            value=pkg_resources.get_distribution("jishaku").version
        )
        emb.add_field(name="Processor name", value=platform.processor())
        emb.add_field(
            name="Current server count",
            value=str(len(ctx.bot.guilds))
        )
        emb.add_field(name="Total Users", value=str(len(ctx.bot.users)))
        emb.set_thumbnail(url=ctx.bot.user.avatar_url)
        emb.set_author(
            name=ctx.bot.user.name,
            icon_url=ctx.bot.user.avatar_url
        )
        emb.set_footer(
            text=f"{ctx.bot.description} Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url
        )

        sent = (await ctx.send(embed=emb))
        await ctx.bot.register_response(sent, ctx.message)

    @commands.command()
    async def ping(self, ctx):
        """Check the bot's latency."""

        latency = ctx.bot.latency * 1000
        latency = round(latency, 4)
        emb = discord.Embed(
            description=f":ping_pong: My current latency is {latency} milliseconds.", color=0xf92f2f)
        emb.set_image(
            url="https://images-ext-2.discordapp.net/external/pKGlPehvn1NTxya18d7ZyggEm4pKFakjbO_sYS-pagM/https/media.giphy.com/media/nE8wBpOIfKJKE/giphy.gif"
        )

        sent = (await ctx.send(embed=emb))
        await ctx.bot.register_response(sent, ctx.message)

def setup(bot):
    bot.add_cog(About())
