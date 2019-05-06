# -*- coding: utf-8 -*-

"""
The MIT License (MIT)
Copyright (c) 2018-2019 laggycomputer
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import asyncio

import discord
from discord.ext import commands


class Moderation(commands.Cog):

    @commands.group(
        aliases=["purge"], invoke_without_command=True,
        description="Clear <count> messages from the bottom of the current channel, excluding the message used to run"
                    " the command."
    )
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, count: int):
        """Delete messages. See full command help for more."""

        await ctx.message.delete()

        messages = await ctx.history(limit=count).flatten()

        await ctx.send(delete_after=5, content="Clearing...")
        deleted = 0
        errorcnt = 0

        for message in messages:
            try:
                await message.delete()
                deleted += 1
            except:
                errorcnt += 1

        sent = (await ctx.send(
            content=f"<:suprKewl:508479728613851136> Done! Deleted {deleted} messages, failed to delete {errorcnt}"
            f" messages. See `{ctx.prefix}clear info for more.`"
        ))
        await ctx.bot.register_response(sent, ctx.message)

    @clear.command(name="info")
    async def clear_info(self, ctx):
        """Shows info on clearing limitations."""

        sent = (await ctx.send(
            "If messages do not disappear when deleted, refresh Discord (Ctrl R) and they should disappear. Remember"
            " that bots cannot delete messages older than 2 weeks, and cannot delete messages faster than 5 per five"
            " seconds."
        ))
        await ctx.bot.register_response(sent, ctx.message)

    @clear.command(
        name="user",
        description="Delete messages within the past <count> messages, but only if they are from <user>."
                    " See the info subcommand of clear for more info."
    )
    async def clear_user(self, ctx, user: discord.Member, count: int):
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
                except:
                    errorcnt += 1
                total += 1

        sent = (await ctx.send(
            content=f"<:suprKewl:508479728613851136> Done! Tried to delete {total} messages, failed to delete"
            f" {errorcnt} messages. See `{ctx.prefix}clear info` for info on Discord client bugs and limitations."
        ))
        await ctx.bot.register_response(sent, ctx.message)

    @clear.command(
        name="role",
        description="Delete all messages within the given limit that were sent by members with the given role. See the"
                    " info subcommand of clear for more info."
    )
    async def clear_role(self, ctx, role: discord.Role, count: int):
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
                except:
                    errorcnt += 1
                total += 1

        sent = (await ctx.send(
            content=f"<:suprKewl:508479728613851136> Done! Tried to delete {total} messages, failed to delete"
            f" {errorcnt} messages. See `{ctx.prefix}clear info` for info on Discord client bugs and limitations."
        ))
        await ctx.bot.register_response(sent, ctx.message)

    @commands.command(
        description="Kicks the given <target>. Also notifies <target> of kick."
    )
    @commands.guild_only()
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, target: discord.Member):
        """Kick someone. See full help command."""

        if target == ctx.guild.owner:
            sent = (await ctx.send(":x: I can't kick the server owner!"))
            await ctx.bot.register_response(sent, ctx.message)
        else:
            if target == ctx.guild.me:
                sent = (await ctx.send(":x: I can't kick myself!"))
                await ctx.bot.register_response(sent, ctx.message)
            else:
                if ctx.author == target:
                    sent = (await ctx.send(":x: I'm not kicking you! If you hate this place that much, just leave!"))
                    await ctx.bot.register_response(sent, ctx.message)
                else:
                    if ctx.guild.me.top_role < ctx.author.top_role:
                        try:
                            await target.send(f"You've been kicked from `{ctx.guild}`. :slight_frown:")
                            sent = None
                        except discord.Forbidden:
                            sent = (await ctx.send(
                                ":x: ?! The kicked user's priviacy settings deny me from telling them they have"
                                " been kicked."
                            ))

                        await target.kick()

                        if sent is None:
                            sent = (await ctx.send(f":boom: RIP {target.mention}."))
                        else:
                            await sent.edit(content=f":boom: RIP {target.mention}.")
                        await ctx.bot.register_response(sent, ctx.message)

                    else:
                        sent = (await ctx.send(
                            ":x: The passed member has a higher/equal top role than/to me, meaning I can't kick 'em."
                        ))
                        await ctx.bot.register_response(sent, ctx.message)

    @commands.command(
        description="Bans the given <target> with reason <reason>, deleteing all messages sent from that user over the"
                    " last <deletedays> days."
    )
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, target: discord.Member, deletedays: int, reason: str):
        """Ban someone. See main help dialog."""

        if isinstance(ctx.channel, discord.abc.GuildChannel):
            if target == ctx.guild.owner:
                sent = (await ctx.send(":x: The server owner can't be banned!"))
                await ctx.bot.register_response(sent, ctx.message)
            else:
                if target == ctx.guild.me:
                    sent = (await ctx.send(":x: Oopsie! Can't ban myself..."))
                    await ctx.bot.register_response(sent, ctx.message)
                else:
                    if target == ctx.author:
                        sent = (await ctx.send(":x: I'm not banning you! Just leave if you hate this place so much!"))
                        await ctx.bot.register_response(sent, ctx.message)
                    else:
                        if ctx.guild.me.top_role > target.top_role:
                            if 7 >= deletedays >= 0:
                                try:
                                    await target.send(
                                        f"Looks like you were banned from `{ctx.guild}`, {target.mention}."
                                        f" :slight_frown:")
                                    sent = None
                                except discord.Forbidden:
                                    sent = (await ctx.send(
                                        ":x: Oh noes! The banned member's priviacy settings forbid me from notifying"
                                        " them of the ban."
                                    ))
                                await ctx.guild.ban(
                                    target, delete_message_days=deletedays, reason=reason
                                )
                                if sent is None:
                                    sent = (await ctx.send(f":boom: Swung the ban hammer on {target.mention}."))
                                else:
                                    await sent.edit(content=f":boom: Swung the ban hammer on {target.mention}.")
                                await ctx.bot.register_response(sent, ctx.message)

                            else:
                                sent = (await ctx.send(
                                    f"Oops! You specified an out-of-range integer for <deletedays>! See"
                                    f" `{ctx.prefix}help ban` for info on limits."
                                ))
                                await ctx.bot.register_response(sent, ctx.message)
                        else:
                            sent = (await ctx.send(
                                ":x: Oops! That member has a higher or equal top role to me, meaning I can't ban"
                                " him/her!"
                            ))
                            await ctx.bot.register_response(sent, ctx.message)

    @commands.command(
        description="Unbans the given <target>. The target must be banned from the current server. <target> will be"
                    " DM'd once they are unbanned."
    )
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, target: discord.User):
        """Unbans someone. Please refer to the main help dialog."""

        target_banned = False
        async for ban in await ctx.guild.bans():
            if ban[0] == target:
                target_banned = True
        if target_banned:
            await ctx.guild.unban(target)
            sent = (await ctx.send("<:suprKewl:508479728613851136> Unbanned!"))
            await ctx.bot.register_response(sent, ctx.message)

            try:
                await target.send(f":thumbs_up: You've been unbanned from {ctx.guild}! If you still have a valid"
                                  f" invite, you can use it to rejoin.")
            except:
                await sent.edit(
                    content=f"{ctx.author.mention} The unbanned user's priviacy settings prevent me from notofying them"
                    f" of their unbanning."
                )
        else:
            sent = (await ctx.send(
                f"{ctx.author.mention} :x: Oops! That user ain't banned! Perhaps you meant someone else?"
            ))
            await ctx.bot.register_response(sent, ctx.message)

    @commands.command(
        description="Gives the list of banned users for this server."
    )
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def banlist(self, ctx):
        """Gives a list of banned users."""

        emb = discord.Embed(color=0xf92f2f)
        bans = []
        banlist = await ctx.guild.bans()
        if not any(banlist):
            sent = (await ctx.send(":white_check_mark: The server has no bans!"))
            await ctx.bot.register_response(sent, ctx.message)
        for ban in banlist:
            bans.append(ban[0].name + "#" + ban[0].discriminator)

        msg = ", ".join(bans)
        emb.add_field(name=f"Banned users for {ctx.guild}", value=msg)

        emb.set_thumbnail(url=ctx.bot.user.avatar_url)
        emb.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
        emb.set_footer(
            text=f"{ctx.bot.description} Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url
        )

        sent = (await ctx.send(embed=emb))
        await ctx.bot.register_response(sent, ctx.message)


def setup(bot):
    bot.add_cog(Moderation())
