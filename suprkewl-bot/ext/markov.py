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

import io
import random

import aiohttp
import discord
from discord.ext import commands


class MarkovChain:
    def __init__(self, t_length):
        self.token_len = t_length
        self.links = []
        self.cur_token = [""] * self.token_len
        self.prev_token = [""] * self.token_len
        self.punctuation = [",", ".", ":", "!", "?", ";", "-"]

    def add_word(self, word):
        if word == "&amp":
            word = "&"

        self.links.append([list(self.prev_token), word])

        del self.prev_token[0]
        self.prev_token.append(word)

    def add_sentence(self, sentence):
        sentence = sentence.replace("\"", "")
        sentence = sentence.replace("'", "")
        sentence = sentence.replace("(", "")
        sentence = sentence.replace(")", "")
        split = sentence.split(" ")
        for token in split:
            for mark in self.punctuation:
                if token.endswith(mark):
                    token = token.replace(mark, "")
                    self.add_word(token)
                    self.add_word(mark)
                    break
            else:
                self.add_word(token)

    def get_options(self, words):
        o = []
        for link in self.links:
            if words == link[0]:
                o.append(link[1])
        return o

    def reset_state(self):
        self.cur_token = [""] * self.token_len

    def next_token(self):
        options = self.get_options(self.cur_token)
        if len(options) == 0:
            return None
        del self.cur_token[0]
        self.cur_token.append(random.choice(options))
        return self.cur_token[-1]

    def next_sentence(self):
        words = [""]
        while words[-1] != "." and words[-1] != "!" and words[-1] != "?" and words[-1] != "\n":
            words.append(self.next_token())
        s = ""
        for token in words:
            s += token
            s += " "
        return s


class Markov(commands.Cog):
    """Make funny Markov chains."""

    def __init__(self):
        def load_file(filename):
            def load_chain(name, c_len):
                chain = MarkovChain(c_len)
                data = open("assets/markov/" + name, "r").read()
                for sentence in data.split("\n"):
                    chain.add_sentence(sentence)
                    chain.add_word("\n")
                return chain

            for chain_len in range(1, 4):
                name = filename + str(chain_len)
                self.markov[name] = load_chain(filename, chain_len)

        self.markov = dict()
        for file in ["obama.txt", "rickroll.txt", "trump.txt"]:
            load_file(file)

    @commands.command()
    async def listchains(self, ctx):
        """List the available sources for a Markov chain."""

        await ctx.send("""
`obama` - Various Obama quotes.
`rickroll` - The *Never Gonna Give You Up* lyrics.
`trump` - A pile of Trump tweets. :eyes:
        """)

    @commands.command()
    async def markov(self, ctx, name, num_tokens: int):
        """Generate Markov chains."""

        new_name = name + ".txt" + str(random.randint(1, 3))
        await ctx.send(new_name)
        if new_name not in self.markov:
            return await ctx.send(
                f"{name} is not a valid chain name.  The valid names are `obama`, `rickroll`, and `trump`. See "
                f"`{ctx.prefix}listchains` for more info.")

        chain = self.markov[new_name]
        ret = []
        for i in range(num_tokens):
            s = chain.next_sentence()
            ret.append(s)

        ret = "\n".join(ret)
        if len(ret) < 2000:
            await ctx.send(ret)
        else:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(ret)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(ret.encode("utf-8")), "out.txt")
                await ctx.send("Attached is your result:", file=fp)


def setup(bot):
    bot.add_cog(Markov())
