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

import datetime
import inspect
import itertools
import os
import typing
import pkg_resources
import platform
import sys
import time

import dateutil.parser
import discord
from discord.ext import commands
import pygit2

from .utils import linecount
from .utils import time as t_utils


# Largely from R. Danny.
def format_commit(commit):
    short, _, _ = commit.message.partition("\n")
    short = discord.utils.escape_markdown(short)
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
    def seconds_to_string(seconds):
        if seconds >= 60:
            minutes, seconds = divmod(seconds, 60)
            ret = f"{minutes} minutes" if minutes > 1 else "1 minute"

            if seconds:
                ret += f" and {seconds} seconds" if seconds > 1 else "1 second"
        else:
            ret = str(seconds) + " seconds" if seconds > 1 else "1 second"

        return ret

    headers = {"Accept": "application/vnd.github.v3+json"}
    async with cs.get("https://api.github.com/repos/laggycomputer/suprkewl-bot/branches", headers=headers) as resp:
        branches = await resp.json()
    ret = {}

    for branch in branches:
        key = branch["name"]
        ret[key] = {}

        headers = {"Accept": "application/vnd.github.v3+json"}
        params = dict(branch=key, event="push", per_page="1", page="1")
        async with cs.get("https://api.github.com/repos/laggycomputer/suprkewl-bot/actions/runs",
                          headers=headers, params=params) as resp:
            out = await resp.json()
            run_id = out["workflow_runs"][0]["id"]

        async with cs.get(
                f"https://api.github.com/repos/laggycomputer/suprkewl-bot/actions/runs/{run_id}/jobs",
                headers=headers, params=params) as resp:
            out = await resp.json()
            workflow_run_info = out["jobs"][0]

        started_at, completed_at = workflow_run_info["started_at"], workflow_run_info["completed_at"]

        ret[key]["link"] = workflow_run_info["html_url"]

        if completed_at is not None:
            if workflow_run_info["conclusion"] == "cancelled":
                val = "Canceled"
            else:
                duration = seconds_to_string(round(
                    (dateutil.parser.parse(completed_at, ignoretz=True)
                     - dateutil.parser.parse(started_at, ignoretz=True)).total_seconds()))
                step_times = []
                for step in workflow_run_info["steps"]:
                    if step["conclusion"] == "skipped":  # This job did not need to be run and should be ignored
                        continue
                    step_times.append(round(
                        (dateutil.parser.parse(step["completed_at"], ignoretz=True)
                         - dateutil.parser.parse(step["started_at"], ignoretz=True))
                        .total_seconds())
                    )  # Round because greatest precision is seconds anyway. This seems to return a float.
                longest_job_time = seconds_to_string(max(step_times))

                build_status = workflow_run_info["conclusion"].title()
                dt = dateutil.parser.parse(completed_at, ignoretz=True)
                offset = t_utils.human_timedelta(dt, accuracy=1)

                val = f"{build_status} {offset}. Ran for a total of {duration}. The longest step took" \
                    f" {longest_job_time}."
            ret[key]["status"] = val
        else:
            val = "Build in progress"
            if started_at is not None:
                dt = dateutil.parser.parse(started_at, ignoretz=True)
                offset = t_utils.human_timedelta(dt, accuracy=1)

                val += " from " + offset
            else:
                val += " (queued/booting VM)"

            ret[key]["status"] = val

    return ret


async def get_recent_builds_on(cs, branch):
    headers = {"Accept": "application/vnd.github.v3+json"}
    params = dict(branch=branch, event="push", per_page="10", page="1")
    async with cs.get("https://api.github.com/repos/laggycomputer/suprkewl-bot/actions/runs",
                      headers=headers, params=params) as resp:
        branch_info = await resp.json()

    ret = []

    for build in branch_info["workflow_runs"]:
        if build["status"] != "completed":
            ret.append(":clock:")
        else:
            state_to_emoji = {
                "success": ":white_check_mark:", "cancelled": ":stop_button:", "failure": ":bangbang:",
                "skipped": ":fast_forward:", "action_required": ":thinking:", "timed_out": ":bangbang:"
            }

            if build["conclusion"] in state_to_emoji:
                ret.append(state_to_emoji[build["conclusion"]])
            else:
                ret.append(":x:")

    if len(ret) < 10:  # There may be less than 10 builds total on this branch, in this case add more emojis
        ret += [":grey_question:"] * (10 - len(ret))

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
        """Gets GitHub Actions info for the bot."""

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

        try:
            lines, firstlineno = inspect.getsourcelines(src)
        except OSError:
            return await ctx.send(":x: This command was declared inline, so source code is not available.")

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
    async def invite(self, ctx, *, id: typing.Union[discord.Member, discord.User, int] = None):
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
