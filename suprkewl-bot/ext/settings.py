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

from discord.ext import commands


class Settings(commands.Cog):
    """Change server-specific bot settings here."""

    @commands.command()
    @commands.guild_only()
    async def prefix(self, ctx, *, prefix=None):
        """Operate on the guild prefix for this bot."""

        if prefix is None:
            if ctx.invoked_subcommand is None:
                set_prefix = await ctx.bot.db_pool.fetchval(
                    "SELECT prefix FROM guilds WHERE guild_id = $1;", ctx.guild.id)
                if not set_prefix:
                    await ctx.send("This server has no custom prefix set. You can set one with"
                                   f" `{ctx.prefix}prefix <prefix>`.")
                else:
                    await ctx.send(
                        f"The guild prefix is currently `{set_prefix}`. You can change it with"
                        f" `{ctx.prefix}prefix <prefix>`."
                    )
        else:
            if ctx.author.guild_permissions.manage_guild:
                if len(prefix) > 10:
                    return await ctx.send(":x: The prefix cannot be longer than 10 characters!")

                await ctx.bot.db_pool.execute(
                    "INSERT INTO GUILDS (guild_id, prefix) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET "
                    "prefix = $2;", ctx.guild.id, prefix)

                await ctx.send(f":ok_hand: The prefix is now `{prefix}`.")
            else:  # Emulate the error handling.
                emb = ctx.default_embed()
                emb.add_field(
                    name="User Missing Permissions",
                    value=f":x: Permission denied to run `{ctx.prefix}{ctx.command}`."
                          f" You need to be able to Manage Server."
                )

                return await ctx.send(embed=emb)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def clearprefix(self, ctx):
        """Reset the guild prefix."""

        await ctx.bot.db_pool.execute("DELETE FROM guilds WHERE guild_id = $1;", ctx.guild.id)
        await ctx.send(
            f":ok_hand: The guild prefix has been reset! You can set it again with `{ctx.prefix}prefix <prefix>`."
        )


def setup(bot):
    bot.add_cog(Settings())
