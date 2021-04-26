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

import discord
from discord.ext import commands


class Moderation(commands.Cog):

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage
        else:
            return True

    @commands.group(
        aliases=["purge"], invoke_without_command=True,
        description="Clear <count> messages from the bottom of the current channel, excluding the message used to run"
                    " the command."
    )
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, count: int):
        """Delete messages. See full command help for more."""

        await ctx.message.delete()

        messages_deleted = await ctx.channel.purge(limit=count)

        await ctx.send(delete_after=5, content="Clearing...", register_response=False)

        deleted = len(messages_deleted)
        errorcnt = count - deleted

        await ctx.send(
            f"<:suprKewl:508479728613851136> Done! Deleted {deleted} messages, failed to delete {errorcnt} messages."
            f" See `{ctx.prefix}{ctx.invoked_with} info` for more."
        )

    @clear.command(name="info")
    async def clear_info(self, ctx):
        """Shows info on clearing limitations."""

        await ctx.send(
            "If messages do not disappear when deleted, refresh Discord (Ctrl R) and they should disappear. Remember"
            " that bots cannot delete messages older than 2 weeks, and cannot delete messages faster than 5 per five"
            " seconds."
        )

    @clear.command(
        name="user",
        description="Delete messages within the past <count> messages, but only if they are from <user>."
                    " See the info subcommand of clear for more info."
    )
    async def clear_user(self, ctx, count: int, *, user: discord.Member):
        """Clear messages by user."""

        if not await ctx.command.parent.can_run(ctx):
            return

        await ctx.message.delete()

        messages = await ctx.history(limit=count).flatten()

        await ctx.send(delete_after=5, content="Clearing...")
        total = 0
        errorcnt = 0

        for message in messages:
            if message.author == user:
                try:
                    await message.delete()
                except discord.HTTPException:
                    errorcnt += 1
                total += 1

        await ctx.send(
            f"<:suprKewl:508479728613851136> Done! Tried to delete {total} messages, failed to delete {errorcnt}"
            f" messages. See `{ctx.prefix}clear info` for info on Discord client bugs and limitations."
        )

    @clear.command(
        name="role",
        description="Delete all messages within the given limit that were sent by members with the given role. See the"
                    " info subcommand of clear for more info."
    )
    async def clear_role(self, ctx, count: int, *, role: discord.Role):
        """Clear messages by role."""

        if not await ctx.command.parent.can_run(ctx):
            return

        await ctx.message.delete()

        messages = await ctx.history(limit=count).flatten()

        await ctx.send(delete_after=5, content="Clearing...")
        total = 0
        errorcnt = 0

        for message in messages:
            if message.author in role.members:
                try:
                    await message.delete()
                except discord.HTTPException:
                    errorcnt += 1
                total += 1

        await ctx.send(
            f"<:suprKewl:508479728613851136> Done! Tried to delete {total} messages, failed to delete {errorcnt}"
            f" messages. See `{ctx.prefix}clear info` for info on Discord client bugs and limitations."
        )

    @commands.command(
        description="Kicks the given <target>. Also notifies <target> of kick."
    )
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, *, target: discord.Member):
        """Kick someone. See full help command."""

        if target == ctx.guild.owner:
            await ctx.send(":x: I can't kick the server owner!")
        else:
            if target == ctx.me:
                await ctx.send(":x: I can't kick myself!")
            else:
                if ctx.author == target:
                    await ctx.send(":x: I'm not kicking you! If you hate this place that much, just leave!")
                else:
                    if ctx.me.top_role < ctx.author.top_role:
                        try:
                            await target.send(f"You've been kicked from `{ctx.guild}`. :slight_frown:")
                            sent = None
                        except discord.Forbidden:
                            sent = await ctx.send(
                                ":x: ?! The kicked user's priviacy settings deny me from telling them they have"
                                " been kicked."
                            )

                        await target.kick()

                        if sent is None:
                            await ctx.send(f":boom: RIP {target.mention}.")
                        else:
                            await sent.edit(content=f":boom: RIP {target.mention}.")

                    else:
                        await ctx.send(
                            ":x: The passed member has a higher/equal top role than/to me, meaning I can't kick 'em."
                        )

    @commands.command(
        description="Bans the given <target> with reason <reason>, deleteing all messages sent from that user over the"
                    " last <deletedays> days."
    )
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, target: discord.Member, deletedays: int, *, reason: str):
        """Ban someone. See main help dialog."""

        if isinstance(ctx.channel, discord.abc.GuildChannel):
            if target == ctx.guild.owner:
                await ctx.send(":x: The server owner can't be banned!")
            else:
                if target == ctx.me:
                    await ctx.send(":x: Oopsie! Can't ban myself...")
                else:
                    if target == ctx.author:
                        await ctx.send(":x: I'm not banning you! Just leave if you hate this place so much!")
                    else:
                        if ctx.me.top_role > target.top_role:
                            if 7 >= deletedays >= 0:
                                try:
                                    await target.send(
                                        f"Looks like you were banned from `{ctx.guild}`, {target.mention}."
                                        f" :slight_frown:")
                                    sent = None
                                except discord.Forbidden:
                                    sent = await ctx.send(
                                        ":x: Oh noes! The banned member's priviacy settings forbid me from notifying"
                                        " them of the ban."
                                    )
                                await ctx.guild.ban(
                                    target, delete_message_days=deletedays, reason=reason
                                )
                                if sent is None:
                                    sent = await ctx.send(f":boom: Swung the ban hammer on {target.mention}.")
                                else:
                                    await sent.edit(content=f":boom: Swung the ban hammer on {target.mention}.")

                            else:
                                await ctx.send(
                                    f"Oops! You specified an out-of-range integer for <deletedays>! See"
                                    f" `{ctx.prefix}help {ctx.invoked_with}` for info on limits."
                                )
                        else:
                            await ctx.send(
                                ":x: Oops! That member has a higher or equal top role to me, meaning I can't ban"
                                " him/her!"
                            )

    @commands.command(
        description="Unbans the given <target>. The target must be banned from the current server. <target> will be"
                    " DM'd once they are unbanned."
    )
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, target: discord.User):
        """Unbans someone. Please refer to the main help dialog."""

        target_banned = False
        async for ban in await ctx.guild.bans():
            if ban[0] == target:
                target_banned = True
        if target_banned:
            await ctx.guild.unban(target)
            sent = await ctx.send("<:suprKewl:508479728613851136> Unbanned!")

            try:
                await target.send(f":thumbs_up: You've been unbanned from {ctx.guild}! If you still have a valid"
                                  f" invite, you can use it to rejoin.")
            except discord.HTTPException:
                await sent.edit(
                    content=f"{ctx.author.mention} The unbanned user's priviacy settings prevent me from notofying them"
                            f" of their unbanning."
                )
        else:
            await ctx.send(
                f"{ctx.author.mention} :x: Oops! That user ain't banned! Perhaps you meant someone else?"
            )

    @commands.command(
        description="Gives the list of banned users for this server."
    )
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def banlist(self, ctx):
        """Gives a list of banned users."""

        emb = ctx.default_embed()

        banlist = await ctx.guild.bans()
        if not any(banlist):
            await ctx.send(":white_check_mark: The server has no bans!")
        bans = map(str, banlist)

        msg = ", ".join(bans)
        emb.add_field(name=f"Banned users for {ctx.guild}", value=msg)

        await ctx.send(embed=emb)

    @commands.command(description="You call, I leave. That's all.")
    @commands.has_permissions(manage_guild=True)
    async def leave(self, ctx):
        """Use this command in place of kicking me."""

        await ctx.guild.leave()


def setup(bot):
    bot.add_cog(Moderation())
