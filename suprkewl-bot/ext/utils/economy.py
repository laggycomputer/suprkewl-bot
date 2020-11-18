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


async def get_money_prefix(ctx, guild_id=None):
    if not guild_id:
        return "$"
    resp = (await (
        await ctx.bot.db.execute("SELECT custom_dollar_sign FROM guilds WHERE guild_id == ?;", (guild_id,))
    ).fetchone())
    if not resp:
        return "$"
    if not resp[0]:
        return "$"
    return resp[0]


async def get_balance_of(ctx, user_id):
    resp = (await (
        await ctx.bot.db.execute("SELECT money FROM economy WHERE user_id == ?;", (user_id,))
    ).fetchone())
    return resp[0] if resp else 0


async def do_economy_give(ctx, to, amount):
    current_money = await get_balance_of(ctx, to.id)
    await ctx.bot.db.execute(
        "INSERT INTO economy (user_id, money) VALUES (?, ?) ON CONFLICT (user_id) DO UPDATE SET money = money + ?;",
        (to.id, current_money + amount, amount))
    await ctx.bot.db.commit()
