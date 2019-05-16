# -*- coding: utf-8 -*-

"""
Copyright (C) 2019 laggycomputer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import hashlib
import io

import discord
from discord.ext import commands


abc_list = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
abc_list_backward = list(reversed(abc_list))


def caesar_translate(message, shift):
    translated = ""

    for symbol in message:
        if symbol.upper() in abc_list:
            num = ord(symbol)
            num += shift % 26
            if symbol.isupper():
                if num > ord("Z"):
                    num -= 26
                elif num < ord("A"):
                    num += 26
            elif symbol.islower():
                if num > ord("z"):
                    num -= 26
                elif num < ord("a"):
                    num += 26

            translated += chr(num)
        else:
            translated += symbol
    return translated


def crack_caesar(string):

    maximum = 0

    weight = [
        6.51, 1.89, 3.06, 5.08, 17.4,
        1.66, 3.01, 4.76, 7.55, 0.27,
        1.21, 3.44, 2.53, 9.78, 2.51,
        0.29, 0.02, 7.00, 7.27, 6.15,
        4.35, 0.67, 1.89, 0.03, 0.04, 1.13
    ]

    c = [
        0, 0, 0, 0, 0,
        0, 0, 0, 0, 0,
        0, 0, 0, 0, 0,
        0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0
    ]

    s = c[:]

    for i in string:
        if i.upper() in abc_list:
            x = (ord(i) | 32) - 97
            if 0 <= x < 26:
                c[x] += 1

    for off in range(26):
        for i in range(26):
            s[off] += 0.01 * c[i] * weight[(i + off) % 26]
            if maximum < s[off]:
                maximum = s[off]
    return (26 - s.index(maximum)) % 26


def keyword_expand(keyword):

    kw_stripped = ""
    for letter in keyword.upper():
        if letter in abc_list:
            kw_stripped += letter

    keyword = kw_stripped

    last_letter_index = abc_list.index(keyword.upper()[-1])
    abc_sliced = list(abc_list[last_letter_index:])
    abc_sliced = abc_sliced + list(abc_list[:last_letter_index])

    kw = ""

    for letter in keyword.upper():
        if letter not in kw:
            kw = letter + kw

    keyword = kw

    for letter in keyword:
        del abc_sliced[abc_sliced.index(letter)]
        abc_sliced.insert(0, letter)

    full_key = ""

    for letter in abc_sliced:
        full_key += letter
    return full_key


def decode_sub(ciphertext, keyword):
    key = keyword_expand(keyword)
    decoded = ""

    for letter in ciphertext:
        if letter.upper() in abc_list:
            is_upper = letter.isupper()
            to_append = abc_list[key.index(letter.upper())]
            if is_upper:
                decoded += to_append
            else:
                decoded += to_append.lower()

    return decoded


def encode_sub(plaintext, keyword):
    key = keyword_expand(keyword)
    encoded = ""

    for letter in plaintext:
        if letter.upper() in abc_list:
            is_upper = letter.isupper()
            to_append = key[abc_list.index(letter.upper())]
            if is_upper:
                encoded += to_append
            else:
                encoded += to_append.lower()
        else:
            encoded += letter

    return encoded


class Cryptography(commands.Cog):

    @commands.group(
        aliases=["ceasar"],  # For you people that can't spell
        description="Operates with the Caesar cipher. Non-alphabetical characters are left untouched."
    )
    async def caesar(self, ctx):
        """Perform operations with the Caesar cipher."""

        if ctx.invoked_subcommand is None:
            sent = (await ctx.send(":x: Please provide a valid subcommand!"))
            await ctx.bot.register_response(sent, ctx.message)

    @caesar.command(name="encode", aliases=["e", "encipher", "encrypt"])
    async def caesar_encode(self, ctx, shift: int, *, message):
        """Encodes a message with the caesar cipher. See https://en.wikipedia.org/wiki/Caesar_cipher."""

        encoded = caesar_translate(message, shift)
        encoded = f"```\n{encoded}```"

        sent = (await ctx.send(encoded))
        await ctx.bot.register_response(sent, ctx.message)

    @caesar.command(name="decode", aliases=["d", "decrypt", "decipher"])
    async def caesar_decode(self, ctx, shift: int, *, message):
        """Decodes a message that was encoded with the given shift. See https://en.wikipedia.org/wiki/Caesar_cipher."""

        decoded = caesar_translate(message, -shift)
        decoded = f"```\n{decoded}```"

        sent = (await ctx.send(decoded))
        await ctx.bot.register_response(sent, ctx.message)

    @caesar.command(name="crack", aliases=["c"])
    async def caesar_crack(self, ctx, *, message):
        """Cracks a message encoded with the Caesar cipher."""

        shift = crack_caesar(message)
        decoded = caesar_translate(message, -shift)

        msg = f"I think this message was encoded with a shift of {shift}, which decodes to:```\n{decoded}```"

        if len(msg) > 2000:
            fp = io.BytesIO(decoded.encode("utf-8"))

            sent = (await ctx.send(
                content=f":white_check_mark: I think the shift is {shift}. Attached is a decryption of your message"
                f" using that shift.",
                file=discord.File(fp, "cracked.txt")
            ))
            await ctx.bot.register_response(sent, ctx.message)
        else:
            sent = (await ctx.send(msg))
            await ctx.bot.register_response(sent, ctx.message)

    @commands.command(
        aliases=["r13"],
        description="Encodes/decodes a message with ROT13, a Caesar cipher of shift 13."
    )
    async def rot13(self, ctx, *, message):
        """Encodes/decodes messages with ROT13."""

        output = caesar_translate(message, 13)

        msg = f"Your output is: ```\n{output}```"

        if len(msg) > 2000:
            fp = io.BytesIO(output.encode("utf-8"))

            sent = (await ctx.send(
                content=f":white_check_mark: Attached is your output.",
                file=discord.File(fp, "rot13.txt")
            ))
            await ctx.bot.register_response(sent, ctx.message)
        else:
            sent = (await ctx.send(msg))
            await ctx.bot.register_response(sent, ctx.message)

    @commands.group(
        aliases=["sub"],
        description="Performs operations with a substitution cipher "
                    "(https://en.wikipedia.org/wiki/Substitution_cipher#Simple_substitution)."
                    " If a key is provided that has a length of less than 26, it will be interpreted as a keyword."
    )
    async def substitution(self, ctx):
        """Perform operations with a substitution cipher."""

        if ctx.invoked_subcommand is None:
            sent = (await ctx.send(":x: Please provide a valid subcommand!"))
            await ctx.bot.register_response(sent, ctx.message)

    @substitution.command(name="keyword", aliases=["k", "key", "keywords", "kw"])
    async def substitution_keyword(self, ctx, *, kw):
        """Transforms a keyword into a full key."""

        full_key = keyword_expand(kw)

        sent = (await ctx.send(f":white_check_mark: Your keyword was expanded to `{full_key}`."))
        await ctx.bot.register_response(sent, ctx.message)

    @substitution.command(name="decode", aliases=["d", "decrypt", "decipher"])
    async def substitution_decode(self, ctx, key, *, message):
        """Decodes a message with the given key using the substitution cipher."""

        decoded = decode_sub(message, key)

        msg = f":white_check_mark: Your message decodes to: ```\n{decoded}```"
        if len(msg) > 2000:
            fp = io.BytesIO(decoded.encode("utf-8"))

            sent = (await ctx.send(
                "Your message was decoded. Because the resulting message is longer than 2000 characters, your output"
                " has been placed in the attached file.",
                file=discord.File(fp, "decoded.txt")
            ))
            await ctx.bot.register_response(sent, ctx.message)
        else:
            sent = (await ctx.send(msg))
            await ctx.bot.register_response(sent, ctx.message)

    @substitution.command(name="encode", aliases=["e", "encipher", "encrypt"])
    async def substitution_encode(self, ctx, key, *, message):
        """Encodes a message with the given key using the substitution cipher."""

        encoded = encode_sub(message, key)

        msg = f":white_check_mark: Your message encodes to: ```\n{encoded}```"
        if len(msg) > 2000:
            fp = io.BytesIO(encoded.encode("utf-8"))

            sent = (await ctx.send(
                "Your message was encoded. Because the resulting message is longer than 2000 characters, your output"
                " has been placed in the attached file.",
                file=discord.File(fp, "encoded.txt")
            ))
            await ctx.bot.register_response(sent, ctx.message)
        else:
            sent = (await ctx.send(msg))
            await ctx.bot.register_response(sent, ctx.message)

    @commands.group(
        aliases=["@bash", "@b"],
        description="Performs operations with the Atbash cipher. See https://en.wikipedia.org/wiki/Atbash."
    )
    async def atbash(self, ctx):
        """Operates with the Atbash cipher."""

        if ctx.invoked_subcommand is None:
            sent = (await ctx.send(":x: Please provide a valid subcommand!"))
            await ctx.bot.register_response(sent, ctx.message)

    @atbash.command(name="encode", aliases=["e", "encipher", "encrypt"])
    async def atbash_encode(self, ctx, *, message):
        """Encodes a message with Atbash."""

        encoded = encode_sub(message, str(abc_list_backward))

        msg = f":white_check_mark: Your message encodes to: ```\n{encoded}```"
        if len(msg) > 2000:
            fp = io.BytesIO(encoded.encode("utf-8"))

            sent = (await ctx.send(
                "Your message was encoded. Because the resulting message is longer than 2000 characters, your output"
                " has been placed in the attached file.",
                file=discord.File(fp, "encoded.txt")
            ))
            await ctx.bot.register_response(sent, ctx.message)
        else:
            sent = (await ctx.send(msg))
            await ctx.bot.register_response(sent, ctx.message)

    @atbash.command(name="decode", aliases=["d", "decrypt", "decipher"])
    async def atbash_decode(self, ctx, *, message):
        """Decodes a message with Atbash."""

        decoded = decode_sub(message, str(abc_list_backward))

        msg = f":white_check_mark: Your message decodes to: ```\n{decoded}```"
        if len(msg) > 2000:
            fp = io.BytesIO(decoded.encode("utf-8"))

            sent = (await ctx.send(
                "Your message was decoded. Because the resulting message is longer than 2000 characters, your output"
                " has been placed in the attached file.",
                file=discord.File(fp, "decoded.txt")
            ))
            await ctx.bot.register_response(sent, ctx.message)
        else:
            sent = (await ctx.send(msg))
            await ctx.bot.register_response(sent, ctx.message)

    @commands.group(
        aliases=["cs"], description="Generate a checksum for your message. Files are currently unsupported."
    )
    async def checksum(self, ctx):
        """Generate cryptographic checksums."""

        if ctx.invoked_subcommand is None:
            sent = (await ctx.send(":x: Please provide a valid subcommand!"))
            await ctx.bot.register_response(sent, ctx.message)

    @checksum.command(name="sha1", aliases=["s1"])
    async def checksum_sha1(self, ctx, *, message):
        """Generate a SHA1 hash."""

        message = message.encode("utf-8")
        m = hashlib.sha1()
        m.update(message)

        hash = m.hexdigest()

        sent = (await ctx.send(f":white_check_mark: The hash of your message is `{hash}`."))
        await ctx.bot.register_response(sent, ctx.message)

    @checksum.command(name="sha256", aliases=["s256"])
    async def checksum_sha256(self, ctx, *, message):
        """Generate a SHA256 hash."""

        message = message.encode("utf-8")
        m = hashlib.sha256()
        m.update(message)

        hash = m.hexdigest()

        sent = (await ctx.send(f":white_check_mark: The hash of your message is `{hash}`."))
        await ctx.bot.register_response(sent, ctx.message)

    @checksum.command(name="sha512", aliases=["s512"])
    async def checksum_sha512(self, ctx, *, message):
        """Generate a SHA512 hash."""

        message = message.encode("utf-8")
        m = hashlib.sha512()
        m.update(message)

        hash = m.hexdigest()

        sent = (await ctx.send(f":white_check_mark: The hash of your message is `{hash}`."))
        await ctx.bot.register_response(sent, ctx.message)

    @checksum.command(name="md5")
    async def checksum_md5(self, ctx, *, message):
        """Generate an MD5 hash."""

        message = message.encode("utf-8")
        m = hashlib.md5()
        m.update(message)

        hash = m.hexdigest()

        sent = (await ctx.send(f":white_check_mark: The hash of your message is `{hash}`."))
        await ctx.bot.register_response(sent, ctx.message)


def setup(bot):
    bot.add_cog(Cryptography())
