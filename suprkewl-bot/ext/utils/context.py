# -*- coding: utf-8 -*-

"""
Copyright (C) 2019 laggycomputer

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


class Context(commands.Context):

    async def register_response(self, msg):
        await self.bot.register_response(msg, self.message)

    async def send(self, *args, **kwargs):
        try:
            register = kwargs.pop("register_response")
        except KeyError:
            register = True

        sent = await super().send(
            *args, **kwargs
        )

        if register:
            await self.register_response(sent)

        return sent

    async def paginate_with_embeds(self, content, *, without_annotation=False, prefix="```\n", suffix="```"):
        if not isinstance(prefix, str) or not isinstance(suffix, str) or not isinstance(content, str):
            raise TypeError

        if len(content) > (2048 - len(prefix) - len(suffix)):
            by_line = content.split("\n")
            current_length = 0
            current_index = 0
            while current_length <= 2048:
                current_length += len(by_line[current_index]) + len("\n")
                current_index += 1

            part1 = prefix + "\n".join(by_line[:current_index - 1]) + suffix
            part2 = prefix + "\n".join(by_line[current_index:]) + suffix

            emb1 = discord.Embed(description=part1, color=self.bot.embed_color)
            emb2 = discord.Embed(description=part2, color=self.bot.embed_color)

            if not without_annotation:
                emb1.set_author(name=self.me.name, icon_url=self.me.avatar_url)
                emb2.set_footer(
                    text=f"{self.bot.embed_footer} Requested by {self.author}", icon_url=self.author.avatar_url)

            await self.send(embed=emb1)
            await self.send(embed=emb2)
        else:
            emb = discord.Embed(description=prefix + content + suffix, color=self.bot.embed_color)

            if not without_annotation:
                emb.set_thumbnail(url=self.me.avatar_url)
                emb.set_author(name=self.me.name, icon_url=self.me.avatar_url)
                emb.set_footer(
                    text=f"{self.bot.embed_footer} Requested by {self.author}", icon_url=self.author.avatar_url)

            await self.send(embed=emb)
