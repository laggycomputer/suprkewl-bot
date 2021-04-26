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

import base64
import binascii
import hashlib
import io

import aiohttp
import discord
# This import is used via globals, so ignore your IDE/linter here.
from Cryptodome.Hash import *  # noqa F403, F401
from argon2 import PasswordHasher
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


def decode_a1z26(message):
    for letter in abc_list_backward:
        message = message.replace(str(abc_list.index(letter) + 1), letter.lower())

    return message.replace("-", "")


def encode_a1z26(message):
    split_message = []
    for word in message.split(" "):
        split_message.append(word)
    for i in range(len(split_message)):
        split_message[i] = list(split_message[i])

    new_words = []

    for word in split_message:
        current_word = []
        to_append = ""
        for letter in word:
            if not letter.isalpha():
                current_word.append(letter)
            else:
                current_word.append(abc_list.index(letter.upper()) + 1)

        for i in range(len(current_word)):
            to_append += str(current_word[i])
            if i == len(current_word) - 1 or not (
                    isinstance(current_word[i], int) and isinstance(current_word[i + 1], int)
            ):
                continue
            else:
                to_append += "-"
        print(to_append)
        new_words.append(to_append)

    return " ".join(new_words)


def do_hash(alg, msg):
    if alg in hashlib.algorithms_guaranteed:
        hash_obj = getattr(hashlib, alg)()
        hash_obj.update(msg)
        return hash_obj.hexdigest()
    elif alg.startswith("sha"):
        num = alg.replace("sha", "")
        if "/" in num:
            attr = f"SHA{num.split('/')[0]}"
            return globals()[attr].new(data=msg, truncate=num.split("/")[1]).hexdigest()
        else:
            attr = f"SHA{num}"
            return globals()[attr].new(data=msg).hexdigest()
    elif alg == "argon2":
        return PasswordHasher().hash(msg)
    else:  # This is an MDx alg
        return globals()[alg.upper()].new(data=msg).hexdigest()


class Cryptography(commands.Cog):

    @commands.group(
        invoke_without_command=True,
        aliases=["ceasar"],  # For you people that can't spell
        description="Operates with the Caesar cipher. Non-alphabetical characters are left untouched."
    )
    async def caesar(self, ctx):
        """Perform operations with the Caesar cipher."""

        await ctx.send(":x: Please provide a valid subcommand!")
        await ctx.send_help(ctx.command)

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

    @commands.group(
        aliases=["sub"],
        invoke_without_command=True,
        description="Performs operations with a substitution cipher "
                    "(https://en.wikipedia.org/wiki/Substitution_cipher#Simple_substitution)."
                    " If a key is provided that has a length of less than 26, it will be interpreted as a keyword."
    )
    async def substitution(self, ctx):
        """Perform operations with a substitution cipher."""

        await ctx.send(":x: Please provide a valid subcommand!")
        await ctx.send_help(ctx.command)

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

    @commands.command(
        aliases=["cs", "hash"],
        description="Generate a checksum using <alg> for your <message>. Files are currently unsupported. Use the"
                    " algorithm `list` with no message to list available algorithms."
    )
    async def checksum(self, ctx, algorithm, *, message=None):
        """Generate cryptographic checksums."""

        algorithm = algorithm.lower()

        allowed_algs = list(hashlib.algorithms_guaranteed)
        allowed_algs += ["sha" + n for n in ["224", "256", "384", "512", "512/224", "512/256"]]
        allowed_algs += ["md2", "md5", "argon2"]

        for alg in ["blake2s", "blake2b"]:
            del allowed_algs[allowed_algs.index(alg)]

        if message is None:
            if algorithm == "list":
                algorithms = ", ".join(f"`{alg}`" for alg in allowed_algs)
                return await ctx.send(":white_check_mark: The allowed algorithms are as follows: \n" + algorithms)
            else:
                return await ctx.send(":x: Where's your message?")

        if algorithm in allowed_algs:
            message = message.encode("utf-8")
            ret = do_hash(algorithm, message)

            await ctx.send(f"{ctx.author.mention}\n> `{ret}`")
        else:
            await ctx.send(
                f":x: Invalid algorithm. See `{ctx.prefix}{ctx.invoked_with} list` for the list of available "
                f"algorithms."
            )

    @commands.group(
        invoke_without_command=True,
        description="Perform operations with A1Z26, a substitution cipher. Replaces A with 1, B with 2, and so on. This"
                    " cipher uses dashes to seperate letters.",
        aliases=["a1"]  # Haha!
    )
    async def a1z26(self, ctx):
        """Operate with the A1Z26 cipher."""

        await ctx.send(":x: Please provide a valid subcommand!")
        await ctx.send_help(ctx.command)

    @a1z26.command(name="encode", aliases=["e"])
    async def a1z26_encode(self, ctx, *, message):
        """Encode in A1Z26."""

        encoded = encode_a1z26(message)
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

    @a1z26.command(name="decode", aliases=["d"])
    async def a1z26_decode(self, ctx, *, message):
        """Decode in A1Z26."""

        decoded = decode_a1z26(message)
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

    @commands.command(aliases=["e"])
    async def encode(self, ctx, alg, *, data=None):
        """Encode a message in a certain algorithm. Use the algorithm `list` to list possibilities."""

        alg = alg.lower()

        if alg in ("base64", "base32", "base16", "base85", "ascii85"):
            alg = alg.replace("base", "b").replace("ascii", "a")

        if alg in ("b64", "b32", "b16", "b85", "a85"):
            encode_func = getattr(base64, alg + "encode")
            out = encode_func(data.encode("utf-8")).decode("utf-8")
        elif alg in ("rot13", "r13"):
            out = caesar_translate(data, 13)
        elif alg in ("atbash", "@bash", "@b"):
            out = encode_sub(data, "".join(abc_list_backward))
        else:
            if alg != "list":
                msg = "Invalid algorithm!\n"
            else:
                msg = ""

            valid_algs = ("rot13", "r13", "atbash", "@bash", "@b", "base64", "b64", "base32", "b32", "base16", "b16",
                          "base85", "b85", "ascii85", "a85")

            msg += "The valid algorithms are:\n"
            msg += ", ".join(f"`{a}`" for a in valid_algs)

            return await ctx.send(msg)

        to_send = f":white_check_mark:```\n{out}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(out)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(out.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)

    @commands.command(aliases=["d"])
    async def decode(self, ctx, alg, *, data=None):
        """Decode a message in a certain algorithm. Use the algorithm `list` to list possibilities."""

        alg = alg.lower()

        if alg in ("base64", "base32", "base16", "base85", "ascii85"):
            alg = alg.replace("base", "b").replace("ascii", "a")

        if alg in ("b64", "b32", "b16", "b85", "a85"):
            decode_func = getattr(base64, alg + "decode")
            try:
                out = decode_func(data.encode("utf-8")).decode("utf-8")
            except (binascii.Error, UnicodeEncodeError, UnicodeDecodeError):
                return await ctx.send(":x: Your input is invalid for the specified algorithm.")
        elif alg in ("rot13", "r13"):
            out = caesar_translate(data, 13)
        elif alg in ("atbash", "@bash", "@b"):
            out = decode_sub(data, "".join(abc_list_backward))
        else:
            if alg != "list":
                msg = "Invalid algorithm!\n"
            else:
                msg = ""

            valid_algs = ("rot13", "r13", "atbash", "@bash", "@b", "base64", "b64", "base32", "b32", "base16", "b16",
                          "base85", "b85", "ascii85", "a85")

            msg += "The valid algorithms are:\n"
            msg += ", ".join(f"`{a}`" for a in valid_algs)

            return await ctx.send(msg)

        to_send = f":white_check_mark:```\n{out}```"

        if len(to_send) > 2000:
            try:
                hastebin_url = await ctx.bot.post_to_hastebin(out)
                await ctx.send(hastebin_url)
            except (aiohttp.ContentTypeError, AssertionError):
                fp = discord.File(io.BytesIO(out.encode("utf-8")), "out.txt")
                await ctx.send(":thinking: Your data was too long for Discord, and hastebin is not working.", file=fp)
        else:
            await ctx.send(to_send)


def setup(bot):
    bot.add_cog(Cryptography())
