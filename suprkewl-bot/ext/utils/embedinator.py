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
import traceback


class Embedinator:
    def __init__(self, bot, destination, member=None, **kwargs):
        self.bot = bot
        self.destination = destination
        self.member = member
        self.max_fields = kwargs.get("max_fields", 25)
        self.base_embed = discord.Embed(**kwargs)
        self.embed_list = []
        self.current = 0
        self.buttons = ["⏪", "◀", "▶", "⏩", "⏹"]
        self.add_embed_page()

    @property
    def last_page(self):
        return self.embed_list[-1]

    def add_embed_page(self):
        self.embed_list.append(self.base_embed.copy())
        if len(self.embed_list) > 1:
            self.set_footer(text=self.base_embed.footer.text, icon_url=self.base_embed.footer.icon_url)

    def add_field(self, *, name, value, inline=True):
        if len(self.last_page.fields) >= self.max_fields:
            self.add_embed_page()
        self.last_page.add_field(name=name, value=value, inline=inline)

    async def send(self):
        self.message = await self.destination.send(
            embed=self.embed_list[self.current]
        )
        self.active = True
        return self.message

    async def edit(self):
        await self.message.edit(
            embed=self.embed_list[self.current]
        )

    async def handle(self):
        for button in self.buttons:
            await self.message.add_reaction(button)

        while self.active:
            done, pending = await asyncio.wait(
                [
                    self.bot.wait_for(
                        "reaction_add",
                        check=self.check_reaction
                    ),
                    self.bot.wait_for(
                        "reaction_remove",
                        check=self.check_reaction
                    )
                ],
                timeout=60.0,
                return_when=asyncio.FIRST_COMPLETED
            )

            try:
                if any(done):
                    reaction, user = done.pop().result()
                    for future in pending:
                        future.cancel()
                    await self.handle_reaction(reaction, user)
                else:
                    await self.cleanup()
            except discord.NotFound:
                traceback.print_exc()
                return

    def check_reaction(self, reaction, user):
        return (
            reaction.message.id == self.message.id and
            str(reaction.emoji) in self.buttons and
            (self.member is None or user.id == self.member.id)
        )

    async def handle_reaction(self, reaction, user):
        emoji = str(reaction.emoji)

        if emoji == "⏹":
            await self.cleanup()

        if emoji == "▶":
            self.current += 1
            if self.current == len(self.embed_list):
                self.current = 0
            await self.edit()
        if emoji == "◀":
            self.current -= 1
            if self.current == -1:
                self.current = len(self.embed_list) - 1
            await self.edit()

        if emoji == "⏪":
            self.current = 0
            await self.edit()
        if emoji == "⏩":
            self.current = len(self.embed_list) - 1
            await self.edit()

    async def cleanup(self):
        try:
            await self.message.edit(content=":white_check_mark:", embed=None)
        except discord.NotFound:
            traceback.print_exc()

        self.active = False

    def set_footer(self, text, icon_url):
        i = 1
        for embed in self.embed_list:
            embed.set_footer(text=f'{i}/{len(self.embed_list)} {text}', icon_url=icon_url)
            i += 1

    def set_author(self, **kwargs):
        self.base_embed.set_author(**kwargs)
        for embed in self.embed_list:
            embed.set_author(**kwargs)

    def set_thumbnail(self, **kwargs):
        self.base_embed.set_thumbnail(**kwargs)
        for embed in self.embed_list:
            embed.set_thumbnail(**kwargs)
