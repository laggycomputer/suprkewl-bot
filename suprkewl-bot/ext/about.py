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

import datetime
import inspect
import itertools
import os
import typing
import pkg_resources
import platform
import sys
import time

import discord
from discord.ext import commands
import pygit2

from .utils import linecount
from .utils import time as t_utils
import config


# Largely from R. Danny.
def format_commit(commit):
    short, _, _ = commit.message.partition("\n")
    short_sha2 = commit.hex[:6]
    commit_tz = datetime.timezone(
        datetime.timedelta(minutes=commit.commit_time_offset))
    commit_time = datetime.datetime.fromtimestamp(
        commit.commit_time).replace(tzinfo=commit_tz)

    offset = t_utils.human_timedelta(commit_time.astimezone(
        datetime.timezone.utc).replace(tzinfo=None), accuracy=1)
    return f"[`{short_sha2}`](https://github.com/laggycomputer/suprkewl-bot/commit/{commit.hex} \"Boo!\")" \
        f" {short} ({offset})"


def get_last_commits(count=5):
    repo = pygit2.Repository(".git")
    commits = list(itertools.islice(
        repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), count))
    return "\n".join(format_commit(c) for c in commits)


def current_time():
    year, month, dayofmonth, hour, minute, second, dayofweek, _, isdst = time.localtime()
    week = ["Sunday", "Monday", "Tuesday",
            "Wednesday", "Thursday", "Friday", "Saturday"]
    dayofweek = week[dayofweek]
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "November", "December"
    ]
    month = months[month - 1]
    disptime = f"{dayofweek}, {month} {dayofmonth}, {year}; {hour}:{minute}:{second}, Pacific Standard Time"
    if isdst:
        disptime += " (DST)"

    return disptime


async def get_latest_build_status(cs):
    repo_id = config.travis_repo_id
    token = config.travis_token
    time_format = "%Y-%m-%dT%H:%M:%SZ"

    def seconds_to_string(seconds):
        if seconds >= 60:
            minutes, seconds = divmod(seconds, 60)
            ret = f"{minutes} minutes" if minutes > 1 else "1 minute"

            if seconds:
                ret += f" and {seconds} seconds" if seconds > 1 else "1 second"
        else:
            ret = str(seconds) + " seconds" if seconds > 1 else "1 second"

        return ret

    headers = {"Travis-API-Version": "3", "Authorization": f"token {token}"}
    async with cs.get(
            f"https://api.travis-ci.com/repo/{repo_id}/branches?include=build.jobs", headers=headers) as resp:
        text = await resp.json()
        branches = text["branches"]
    ret = {}

    for branch in branches:
        key = branch["name"]
        ret[key] = {}

        started_at, finished_at = branch["last_build"]["started_at"], branch["last_build"]["finished_at"]

        ret[key]["link"] = f"https://travis-ci.com/" \
                           f"{branch['repository']['slug']}/builds/{branch['last_build']['id']}"

        if finished_at is not None:
            if branch["last_build"]["state"] == "canceled":
                val = "Canceled"
            else:
                duration = seconds_to_string(branch["last_build"]["duration"])
                job_times = []
                for job in branch["last_build"]["jobs"]:
                    job_times.append(round(
                        (datetime.datetime.strptime(job["finished_at"], time_format)
                         - datetime.datetime.strptime(job["started_at"], time_format))
                        .total_seconds())
                    )  # Round because greatest precision is seconds anyway. This seems to return a float.
                longest_job_time = seconds_to_string(max(job_times))

                build_status = branch["last_build"]["state"].title()
                dt = datetime.datetime.strptime(finished_at, time_format)
                offset = t_utils.human_timedelta(dt, accuracy=1)

                val = f"{build_status} {offset}. Ran for a total of {duration}. The longest job took" \
                    f" {longest_job_time}."
            ret[key]["status"] = val
        else:
            val = "Build in progress"
            if started_at is not None:

                dt = datetime.datetime.strptime(started_at, "%Y-%m-%dT%H:%M:%SZ")
                offset = t_utils.human_timedelta(dt, accuracy=1)

                val += " from " + offset
            else:
                val += " (booting VM)"

            ret[key]["status"] = val

    return ret


async def get_recent_builds_on(cs, branch):
    repo_id = 9109252
    token = config.travis_token
    headers = {"Travis-API-Version": "3", "Authorization": f"token {token}"}
    async with cs.get(
            f"https://api.travis-ci.com/repo/{repo_id}/branch/{branch}?include=branch.recent_builds", headers=headers
    ) as resp:
        branch_info = await resp.json()

    ret = []

    for build in branch_info["recent_builds"]:
        if build["finished_at"] is None:
            ret.append(":clock:")
        else:
            state_to_emoji = {"passed": ":white_check_mark:", "canceled": ":grey_question:", "errored": ":bangbang:"}

            if build["state"] in state_to_emoji:
                ret.append(state_to_emoji[build["state"]])
            else:
                ret.append(":x:")

    return ret


class BotMeta(commands.Cog, name="Bot Meta"):

    @commands.command(aliases=["github", "branches"])
    async def git(self, ctx):
        """Get info about the Git repository for this bot."""

        emb = ctx.default_embed()
        emb.title = "GitHub Info"
        emb.description = get_last_commits()
        emb.add_field(name="Build status", value=f"See `{ctx.prefix}buildinfo` for build status.")

        await ctx.send(embed=emb)

    @commands.command(aliases=["bi", "buildhistory", "bh", "builds"])
    async def buildinfo(self, ctx):
        """Gets Travis CI info for the bot."""

        status = await get_latest_build_status(ctx.bot.session)
        emb = ctx.default_embed()

        desc = ""

        for k, v in status.items():
            desc += f"`{k}`:\n"
            desc += f"**[Latest build]({v['link']}):** {v['status']}\n"

            past_status = await get_recent_builds_on(ctx.bot.session, k)
            desc += f"**10 most recent builds:** {''.join(past_status)}\n\n"
        emb.description = desc

        await ctx.send(embed=emb)

    @commands.command()
    async def stats(self, ctx):
        """Get some bot stats."""

        emb = ctx.default_embed()
        emb.title = "Bot Stats"
        emb.add_field(name="Line count", value=linecount())
        cmds_used = ctx.bot.commands_used + 1  # + this one
        msgs_seen = ctx.bot.messages_seen
        guilds = len(ctx.bot.guilds)
        all_members = len(set(ctx.bot.get_all_members()))
        emb.add_field(
            name="Stats",
            value=f"{cmds_used} commands used and {msgs_seen} messages seen since start.\n{guilds} guilds with a "
                  f"combined total of {all_members} members (average of about {round(all_members / guilds, 2)} per "
                  f"guild).\n{len(ctx.bot.commands)} commands registered."
        )

        await ctx.send(embed=emb)

    @commands.command(aliases=["info"])
    async def about(self, ctx):
        """Give some general bot info."""

        async with ctx.typing():
            emb = ctx.default_embed()
            emb.title = "Bot info"

            emb.add_field(name="Support Server", value="[Here](https://www.discord.gg/CRBBJVY \"Boo!\")")
            emb.add_field(name="System Time", value=current_time())
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
                name="Python Version", value=f"Python {'.'.join(map(str, sys.version_info[:3]))}-{sys.version_info[3]},"
                f" build date {platform.python_build()[1]}"
            )
            emb.add_field(
                name="discord.py version",
                value=pkg_resources.get_distribution("discord.py").version
            )
            emb.add_field(
                name="Jishaku version",
                value=pkg_resources.get_distribution("jishaku").version
            )
            if platform.processor():
                emb.add_field(name="Processor name", value=platform.processor())
            emb.add_field(
                name="Current server count",
                value=str(len(ctx.bot.guilds))
            )
            owner_id = ctx.bot.owner_id
            if ctx.guild is not None:
                owner = await ctx.guild.fetch_member(owner_id)
            else:
                owner = None
            if owner is not None:
                emb.add_field(name="Bot owner", value=f"<@{owner_id}>")

        await ctx.send(embed=emb)

    @commands.command()
    async def ping(self, ctx):
        """Check the bot's latency."""

        latency = ctx.bot.latency * 1000
        latency = round(latency, 4)
        emb = ctx.colored_embed
        emb.description = f":ping_pong: My current latency is {latency} milliseconds."
        fp = discord.File(os.path.join("assets", "catping.gif"), "image.gif")
        emb.set_image(
            url="attachment://image.gif"
        )

        await ctx.send(embed=emb, file=fp)

    # From R. Danny
    @commands.command(
        aliases=["sauce"],
        description="Use dots or spaces to find source code for subcommands, e.g. `clear info` or `clear.info`."
    )
    async def source(self, ctx, *, command=None):
        """Find my source code for a specific command."""

        source_url = "https://github.com/laggycomputer/suprkewl-bot/blob/untested"
        if command is None:
            return await ctx.send("https://github.com/laggycomputer/suprkewl-bot/tree/untested")

        if command == "help":
            src = type(ctx.bot.help_command)
            module = src.__module__
            filename = inspect.getsourcefile(src)
        else:
            obj = ctx.bot.get_command(command.replace(".", " "))
            if obj is None:
                return await ctx.send("Could not find command.")

            # since we found the command we're looking for, presumably anyway, let's
            # try to access the code itself
            src = obj.callback.__code__
            module = obj.callback.__module__
            filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith("discord"):
            if module.startswith("jishaku"):
                source_url = "https://github.com/Gorialis/jishaku/blob/master"
                location = module.replace(".", "/") + ".py"
            else:
                location = os.path.relpath(filename).replace("\\", "/")
        else:
            location = module.replace(".", "/") + ".py"
            source_url = 'https://github.com/Rapptz/discord.py/blob/master'

        final_url = f"<{source_url}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>"

        await ctx.send(final_url)

    @commands.command()
    async def invite(self, ctx, *, id: typing.Union[discord.Member, discord.User, int]):
        """Get a link to invite this bot or another."""

        if id:
            if isinstance(id, (discord.Member, discord.User)):
                if not id.bot:
                    return await ctx.send(":x: That's not a bot.")
                id = id.id  # :exploding_head:

        id = id or ctx.bot.user.id

        await ctx.send(discord.utils.oauth_url(id))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def privacy(self, ctx):
        """Links privacy information for the bot."""

        await ctx.send("https://github.com/laggycomputer/suprkewl-bot/blob/untested/privacy.md")


def setup(bot):
    bot.add_cog(BotMeta())
