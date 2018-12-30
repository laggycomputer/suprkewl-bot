# -*- coding: utf-8 -*-
"""Copyright 2018 Dante Dam
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

import platform
import time

import discord
from discord.ext import commands

class Info():
    def __init__(self, bot):
        self.bot = bot
    @commands.command(description="Gives info on role <permsRole> in server (ping the role). Includes role color and member count, amongst other things.")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def roleinfo(self, ctx, role: discord.Role):
        """(GUILD ONLY) Gives info on a passed role."""

        emb = discord.Embed(title=f"Info for '{role}', a role in '{ctx.guild}'", color=role.color)
        emb.set_author(name='Me', icon_url=self.bot.user.avatar_url)
        emb.add_field(name="Role Color (Hex)", value=role.color)
        emb.add_field(name="Members with Role", value=len(role.members))
        emb.add_field(name="Role ID", value=role.id)
        dispHoist="No"
        if role.hoist:
            dispHoist="Yes"
        emb.add_field(name="'Display role member seperately from online members'", value=dispHoist)

        await ctx.send(embed=emb)

    @roleinfo.error
    async def roleinfoerr(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(":x: This command is marked for servers only, and will not work in a DM!")
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(":x: Without the permission `Manage Roles`, I can't fetch permssions!")

    @commands.command(description="Gives perms on the given <role> (ping it). Permissions are listed in the order they appear on Discord. The bot must have the 'Manage Roles' permission for this to work, and the user must have a role called 'suprkewl-viewPerms' to use the command. Remember that role perms may be overridden on a per-channel (sometimes also on a per-user) basis.")
    @commands.guild_only()
    @commands.has_any_role("suprkewl-viewPerms")
    @commands.bot_has_permissions(manage_roles=True)
    async def roleperms(self, ctx, role: discord.Role):
        """(GUILD ONLY) Get permissions for a role"""

        emb = discord.Embed(title=f"Perms for '{role}', a role in '{ctx.server}'")

        perms = role.permissions

        apitohuman = {"add_reactions":"Add Reactions", "administrator":"Administrator", "attach_files":"Attach Files",
        "ban_members":"Ban Members", "change_nickname":"Can Change Own Nickname", "connect":"Connect to Voice Channels",
        "create_instant_invite":"Create Server Invites", "deafen_members":"Deafen Members", "embed_links":"Embed Links",
        "external_emojis":"(Nitro Only) Use External Emotes", "kick_members":"Kick Members", "manage_channels":"Change, Create, and Delete Roles",
        "manage_emojis":"Create, Delete, and Rename Server Emotes", "manage_guild":"Manage Server", "manage_messages":"Manage Messages",
        "manage_messages":"Manage Messages", "manage_nicknames":"Manage Nicknames", "manage_roles":"Manage Roles", "manage_webhooks":"Manage Webhooks",
        "mention_everyone":"Ping \@everyone and \@here", "move_members":"Move Members Between Voice Channels", "mute_members":"Mute Members",
        "priority_speaker":"Use Priority PTT", "read_message_history":"Read Past Messages in Text Channels", "read_messages":"Read Messages and See Voice Channels",
        "send_messages":"Send Messages", "send_tts_messages":"Send TTS Messages", "speak":"Speak", "use_voice_activation":"No Voice Activity",
        "view_audit_log":"View the Server Audit Log"}

        order = [1, 28, 13, 16, 11, 10, 3, 6, 4, 15, 12, 17, 23, 24, 25, 14, 8, 2, 22, 18, 9, 0, 5, 26, 20, 7, 19, 27, 21]
        permtuples = []

        for permTuple in iter(perms):
            readablename = apitohuman[permTuple[0]]
            permtuples.append((readablename, permTuple[1]))

        for number in order:
            fieldname = permtuples[number][0]

            if permtuples[number][1]:
                fieldval = "Yes"
            else:
                fieldval = "No"
            emb.add_field(name=fieldname, value=fieldval)

        await ctx.send(embed=emb)

    @commands.command(description="Gets some stats about the bot. Has a 5-second cooldown per channel..")
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def botstats(self, ctx):
        """Give some system info for the bot."""

        emb = discord.Embed(title="Bot info", color=0xffffff)
        year, month, dayofmonth, hour, minute, second, dayofweek, dayofyear, isdst = time.localtime()
        week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        dayofweek = week[dayofweek]
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "November", "December"]
        month = months[month]
        disptime = f"{dayofweek}, {month} {dayofmonth}, {year}; {hour}:{minute}:{second}, Pacific Standard Time"
        if isdst:
            disptime = disptime + " (DST)"

        emb.add_field(name="System Time", value=disptime)
        emb.add_field(name="Processor Type", value=platform.machine().lower())
        emb.add_field(name="OS version (short)", value=platform.system() + " " + platform.release())
        emb.add_field(name="OS version (long)", value=platform.platform(aliased = True))
        emb.add_field(name="Python Version", value=f"Python {platform.python_branch()}, build date {platform.python_build()[1]}")
        emb.add_field(name="discord.py version", value=discord.__version__)
        emb.add_field(name="Processor name", value=platform.processor())
        emb.add_field(name="Current server count", value=str(len(self.bot.guilds)))
        emb.add_field(name="Total Users", value=str(len(self.bot.users)))
        await ctx.send(embed=emb)
        
def setup(bot):
    bot.add_cog(Info(bot))
