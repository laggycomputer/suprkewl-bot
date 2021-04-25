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


async def get_money_prefix(ctx, guild_id=None):
    if guild_id is None and ctx.guild:
        guild_id = ctx.guild.id

    if not guild_id:
        return "$"
    set_money_prefix = await ctx.bot.db_pool.fetchval(
        "SELECT custom_dollar_sign FROM guilds WHERE guild_id = $1;", guild_id)
    return set_money_prefix if set_money_prefix is not None else "$"


async def get_balance_of(ctx, user_id):
    resp = await ctx.bot.db_pool.fetchval("SELECT money FROM economy WHERE user_id = $1;", user_id)
    return resp if resp is not None else 0


async def do_economy_give(ctx, to, amount):
    async with ctx.bot.db_pool.acquire() as conn:
        async with conn.transaction():
            current_money = await get_balance_of(ctx, to.id)
            await ctx.bot.db_pool.execute(
                "INSERT INTO economy (user_id, money) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET "
                "money = $2;", to.id, current_money + amount)
