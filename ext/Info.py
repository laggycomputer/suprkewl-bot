# -*- coding: utf-8 -*-
"""Copyright 2018 Dante Dam
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

import discord
from discord.ext import commands
import platform
import time

class Info():
    def __init__(self, bot):
        self.bot = bot
    @commands.command(description = "Gives info on role <permsRole> in server (ping the role). Append --perms to your message to also fetch permissions (in this case, the invoker must have a role called 'suprkewl-viewPerms'). If a permission is unlisted, it is likely that the permission in question cannot be requested from the bot's API. Also note the the permissions listed may or may not be overrideable on a per-channel, per-user/role basis.")    
    @commands.guild_only()
    @commands.has_any_role("suprkewl-viewPerms")
    @commands.bot_has_permissions(manage_roles = True)
    async def roleinfo(self, ctx, permsRole: discord.Role):
        """(GUILD ONLY) Gives server perms. See 's!help serverperms'..."""

        emb = discord.Embed(title = "Perms for {0.name}, a role in {1.name}".format(permsRole, ctx.guild), color = permsRole.color)
        emb.set_author(name = 'Me', icon_url = self.bot.user.avatar_url)
        emb.add_field(name = "Role Color (Hex)", value = str(permsRole.color))
        emb.add_field(name = "Members with Role", value = str(len(permsRole.members)))
        if "--perms" in ctx.message.content:
            perms = permsRole.permissions
            """
            emb.add_field(name="Create Instant Invite", value=str(perms.create_instant_invite))
            emb.add_field(name="Is Server Administrator", value=str(perms.administrator))
            emb.add_field(name="Kick Membbers", value=str(perms.kick_members))
            emb.add_field(name="Ban Members", value=str(perms.ban_members))
            emb.add_field(name="Manage Server", value=str(perms.guild))
            emb.add_field(name="Manage Channels", value=str(perms.manage_channels))
            emb.add_field(name="Manage Nicknames", value=str(perms.manage_nicknames))
            emb.add_field(name="Manage Roles", value=str(perms.manage_roles))
            emb.add_field(name="Manage Webhooks", value=str(perms.manage_webhooks))
            emb.add_field(name="Manage Emojis", value=str(perms.manage_emojis))
            emb.add_field(name="View the Audit Log", value=str(perms.view_audit_logs))
            emb.add_field(name="Add Reactions to Messages", value=str(perms.add_reactions))
            emb.add_field(name="Read Messages", value=str(perms.read_messages))
            emb.add_field(name="Read Message History", value=str(perms.read_message_history))
            emb.add_field(name="Send Messages", value=str(perms.send_messages))
            emb.add_field(name="Send TTS Messages", value=str(perms.send_tts_messages))
            emb.add_field(name="Embed Links in Messages", value=str(perms.embed_links))
            emb.add_field(name="Attach Files to Messages", value=str(perms.attach_files))
            emb.add_field(name="Mention @everyone", value=str(perms.mention_everyone))
            emb.add_field(name="Send and React with External Emojis", value=str(perms.external_emojis))
            emb.add_field(name="Connect to Voice Channels", value=str(perms.connect))
            emb.add_field(name="Speak in Voice Channels", value=str(perms.speak))
            emb.add_field(name="Mute Members", value=str(perms.mute_members))
            emb.add_field(name="Deafen Members", value=str(perms.deafen_members))
            emb.add_field(name="Must Use Push to Talk", value=str(perms.use_voice_activation))
            emb.add_field(name="Move Members", value=str(perms.move_members))
            emb.add_field(name="Change Own Nickname", value=str(perms.change_nickname))
            """
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
                readablename = apitohuman[perms[0]]
                permtuples.append((readablename, permTuple[1]))
            for number in order:
                fieldname = permtuples[number][0]
                fieldval = str(permtuples[number][1])
                emd.add_field(name = fieldname, value = fieldval)
        await ctx.send(embed = emb)

    @roleinfo.error
    async def roleinfoerr(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(":x: This command is marked for servers only, and will not work in a DM!")
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(":x: Without the permission `Manage Roles`, I can't fetch permssions!")

    @commands.command(description = "Gets some stats about the bot. Has a 5-second cooldown per channel..")
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def botstats(self, ctx):
        """Give some system info for the bot."""

        emb = discord.Embed(title = "Bot info", color = 0xffffff)
        year, month, dayofmonth, hour, minute, second, dayofweek, dayofyear, isdst = time.localtime()
        week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        dayofweek = week[dayofweek]
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "November", "December"]
        month = months[month]
        disptime = f"{dayofweek}, {month} {dayofmonth}, {year}; {hour}:{minute}:{second}, Pacific Standard Time"
        if isdst:
            disptime = disptime + " (DST)"

        emb.add_field(name = "System Time", value = disptime)
        emb.add_field(name = "Processor Type", value = platform.machine().lower())
        emb.add_field(name = "OS version (short)", value = platform.system()+" "+platform.release())
        emb.add_field(name = "OS version (long)", value = platform.platform(aliased = True))
        emb.add_field(name = "Python Version", value = "Python {0}, build date {1}".format(platform.python_branch(), platform.python_build()[1]))
        emb.add_field(name = "discord.py version", value = discord.__version__)
        emb.add_field(name = "Processor name", value = platform.processor())
        emb.add_field(name = "Current server count", value = str(len(self.bot.guilds)))
        emb.add_field(name = "Total Users", value = str(len(self.bot.users)))
        await ctx.send(embed = emb)
        
def setup(bot):
    bot.add_cog(Info(bot))
