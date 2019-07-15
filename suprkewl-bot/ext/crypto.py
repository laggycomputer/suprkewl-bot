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


import base64
import binascii
import hashlib
import io

import aiohttp
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
            await ctx.send(":x: Please provide a valid subcommand!")

    @caesar.command(name="encode", aliases=["e", "encipher", "encrypt"])
    async def caesar_encode(self, ctx, shift: int, *, message):
        """Encodes a message with the caesar cipher. See https://en.wikipedia.org/wiki/Caesar_cipher."""

        encoded = caesar_translate(message, shift)
        to_send = f"```\n{encoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(encoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(encoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @caesar.command(name="decode", aliases=["d", "decrypt", "decipher"])
    async def caesar_decode(self, ctx, shift: int, *, message):
        """Decodes a message that was encoded with the given shift. See https://en.wikipedia.org/wiki/Caesar_cipher."""

        decoded = caesar_translate(message, -shift)
        to_send = f"```\n{decoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(decoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(decoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @caesar.command(name="crack", aliases=["c"])
    async def caesar_crack(self, ctx, *, message):
        """Cracks a message encoded with the Caesar cipher."""

        shift = crack_caesar(message)
        decoded = caesar_translate(message, -shift)

        msg = f"I think this message was encoded with a shift of {shift}, which decodes to:```\n{decoded}```"

        if len(msg) > 2000:
            fp = io.BytesIO(decoded.encode("utf-8"))

            await ctx.send(
                f":white_check_mark: I think the shift is {shift}. Attached is a decryption of your message using that"
                f" shift.",
                file=discord.File(fp, "cracked.txt")
            )
        else:
            await ctx.send(msg)

    @commands.command(
        aliases=["r13"],
        description="Encodes/decodes a message with ROT13, a Caesar cipher of shift 13."
    )
    async def rot13(self, ctx, *, message):
        """Encodes/decodes messages with ROT13."""

        output = caesar_translate(message, 13)

        to_send = f"Your output is: ```\n{output}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(output)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(output.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @commands.group(
        aliases=["sub"],
        description="Performs operations with a substitution cipher "
                    "(https://en.wikipedia.org/wiki/Substitution_cipher#Simple_substitution)."
                    " If a key is provided that has a length of less than 26, it will be interpreted as a keyword."
    )
    async def substitution(self, ctx):
        """Perform operations with a substitution cipher."""

        if ctx.invoked_subcommand is None:
            await ctx.send(":x: Please provide a valid subcommand!")

    @substitution.command(name="keyword", aliases=["k", "key", "keywords", "kw"])
    async def substitution_keyword(self, ctx, *, kw):
        """Transforms a keyword into a full key."""

        full_key = keyword_expand(kw)

        await ctx.send(f":white_check_mark: Your keyword was expanded to `{full_key}`.")

    @substitution.command(name="decode", aliases=["d", "decrypt", "decipher"])
    async def substitution_decode(self, ctx, key, *, message):
        """Decodes a message with the given key using the substitution cipher."""

        decoded = decode_sub(message, key)
        to_send = f":white_check_mark: Your message decodes to: ```\n{decoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(decoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(decoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @substitution.command(name="encode", aliases=["e", "encipher", "encrypt"])
    async def substitution_encode(self, ctx, key, *, message):
        """Encodes a message with the given key using the substitution cipher."""

        encoded = encode_sub(message, key)
        to_send = f":white_check_mark: Your message encodes to: ```\n{encoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(encoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(encoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @commands.group(
        aliases=["@bash", "@b"],
        description="Performs operations with the Atbash cipher. See https://en.wikipedia.org/wiki/Atbash."
    )
    async def atbash(self, ctx):
        """Operates with the Atbash cipher."""

        if ctx.invoked_subcommand is None:
            await ctx.send(":x: Please provide a valid subcommand!")

    @atbash.command(name="encode", aliases=["e", "encipher", "encrypt"])
    async def atbash_encode(self, ctx, *, message):
        """Encodes a message with Atbash."""

        encoded = encode_sub(message, str(abc_list_backward))
        to_send = f":white_check_mark: Your message encodes to: ```\n{encoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(encoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(encoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @atbash.command(name="decode", aliases=["d", "decrypt", "decipher"])
    async def atbash_decode(self, ctx, *, message):
        """Decodes a message with Atbash."""

        decoded = decode_sub(message, str(abc_list_backward))
        to_send = f":white_check_mark: Your message decodes to: ```\n{decoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(decoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(decoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @commands.command(
        aliases=["cs"],
        description="Generate a checksum using <alg> for your <message>. Files are currently unsupported. Use the"
                    " algorithm `list` with no message to list available algorithms."
    )
    async def checksum(self, ctx, algorithm, *, message=None):
        """Generate cryptographic checksums."""

        allowed_alg = hashlib.algorithms_guaranteed

        if algorithm == "list" and message is None:
            algorithms = ", ".join(f"`{alg}`" for alg in allowed_alg)
            return await ctx.send(":white_check_mark: The allowed algorithms are as follows: \n" + algorithms)

        if algorithm in allowed_alg:
            message = message.encode("utf-8")
            m = getattr(hashlib, algorithm)()
            m.update(message)
            hash = m.hexdigest()

            await ctx.send(f":white_check_mark: The hash of your message is `{hash}`.")
        else:
            await ctx.send(
                f":x: Invalid algorithm. Remember that algorithm names are case-sensitive. See"
                f" `{ctx.prefix}{ctx.invoked_with} list` for the list of available algorithms."
            )

    @commands.group(aliases=["b64"])
    async def base64(self, ctx):
        """Perform operations with the base64 encoding."""

        if ctx.invoked_subcommand is None:
            await ctx.send("You must specify a valid subcommand.")

    @base64.command(name="encode", aliases=["e"])
    async def base64_encode(self, ctx, *, data):
        """Encode with base64."""

        encoded = base64.standard_b64encode(data.encode("utf-8")).decode("utf-8")
        to_send = f"```\n{encoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(encoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(encoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @base64.command(name="decode", aliases=["d"])
    async def base64_decode(self, ctx, *, data):
        """Decode with base64."""

        try:
            decoded = base64.standard_b64decode(data.encode("utf-8")).decode("utf-8")
        except binascii.Error:
            return await ctx.send("Your input code is invalid.")

        to_send = f"```\n{decoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(decoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(decoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @commands.group(aliases=["b32"])
    async def base32(self, ctx):
        """Perform operations with the base32 encoding."""

        if ctx.invoked_subcommand is None:
            await ctx.send("You must specify a valid subcommand.")

    @base32.command(name="encode", aliases=["e"])
    async def base32_encode(self, ctx, *, data):
        """Encode with base32."""

        encoded = base64.b32encode(data.encode("utf-8")).decode("utf-8")
        to_send = f"```\n{encoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(encoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(encoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @base32.command(name="decode", aliases=["d"])
    async def base32_decode(self, ctx, *, data):
        """Decode with base32."""

        try:
            decoded = base64.b32decode(data.encode("utf-8")).decode("utf-8")
        except binascii.Error:
            return await ctx.send("Your input code was invalid.")

        to_send = f"```\n{decoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(decoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(decoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @commands.group(aliases=["b16"])
    async def base16(self, ctx):
        """Perform operations with the base16 encoding."""

        if ctx.invoked_subcommand is None:
            await ctx.send("You must specify a valid subcommand.")

    @base16.command(name="encode", aliases=["e"])
    async def base16_encode(self, ctx, *, data):
        """Encode with base16."""

        encoded = base64.b16encode(data.encode("utf-8")).decode("utf-8")
        to_send = f"```\n{encoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(encoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(encoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @base16.command(name="decode", aliases=["d"])
    async def base16_decode(self, ctx, *, data):
        """Decode with base16."""

        try:
            decoded = base64.b16decode(data.encode("utf-8")).decode("utf-8")
        except binascii.Error:
            return await ctx.send("Your input code is invalid.")

        to_send = f"```\n{decoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(decoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(decoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @commands.group(aliases=["b85"])
    async def base85(self, ctx):
        """Perform operations with the base85 encoding."""

        if ctx.invoked_subcommand is None:
            await ctx.send("You must specify a valid subcommand.")

    @base85.command(name="encode", aliases=["e"])
    async def base85_encode(self, ctx, *, data):
        """Encode with base85."""

        encoded = base64.b85encode(data.encode("utf-8")).decode("utf-8")
        to_send = f"```\n{encoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(encoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(encoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @base85.command(name="decode", aliases=["d"])
    async def base85_decode(self, ctx, *, data):
        """Decode with Ascii85."""

        decoded = base64.b85decode(data.encode("utf-8")).decode("utf-8")
        to_send = f"```\n{decoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(decoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(decoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @commands.group(aliases=["a85"])
    async def ascii85(self, ctx):
        """Perform operations with the Ascii85 encoding."""

        if ctx.invoked_subcommand is None:
            await ctx.send("You must specify a valid subcommand.")

    @ascii85.command(name="encode", aliases=["e"])
    async def ascii85_encode(self, ctx, *, data):
        """Encode with Ascii85."""

        encoded = base64.a85encode(data.encode("utf-8")).decode("utf-8")
        to_send = f"```\n{encoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(encoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(encoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @ascii85.command(name="decode", aliases=["d"])
    async def ascii85_decode(self, ctx, *, data):
        """Decode with Ascii85."""

        decoded = base64.a85decode(data.encode("utf-8")).decode("utf-8")
        to_send = f"```\n{decoded}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(decoded)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(decoded.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)


def setup(bot):
    bot.add_cog(Cryptography())
