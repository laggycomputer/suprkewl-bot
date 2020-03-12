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

import copy
import io
import math
import os
import time
import typing

import aiohttp
import cv2
import discord
from discord.ext import commands
import numpy as np
from PIL import Image
import PIL.ImageFilter
import PIL.ImageOps

from .utils import async_executor


PWD = os.getcwd()


@async_executor()
def fry(img):
    coords = find_chars(img)
    img = add_b_emojis(img, coords)
    img = add_laughing_emojis(img, 5)

    # bulge at random coordinates
    [w, h] = [img.width - 1, img.height - 1]
    w *= np.random.random(1)
    h *= np.random.random(1)
    r = int(((img.width + img.height) / 10) * (np.random.random(1)[0] + 1))
    img = bulge(img, np.array([int(w), int(h)]), r, 3, 5, 1.8)

    img = add_noise(img, 0.2)
    img = change_contrast(img, 200)

    fp = io.BytesIO()
    img.save(fp, format="png")
    fp.seek(0)

    return fp


def find_chars(img):
    gray = np.array(img.convert("L"))
    ret, mask = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    image_final = cv2.bitwise_and(gray, gray, mask=mask)
    ret, new_img = cv2.threshold(image_final, 180, 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    dilated = cv2.dilate(new_img, kernel, iterations=1)
    contours, hierarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    coords = []
    for contour in contours:
        # get rectangle bounding contour
        [x, y, w, h] = cv2.boundingRect(contour)
        # ignore large chars (probably not chars)
        if w > 70 and h > 70:
            continue
        coords.append((x, y, w, h))
    return coords


def change_contrast(img, level):
    factor = (259 * (level + 255)) / (255 * (259 - level))

    def contrast(c):
        return 128 + factor * (c - 128)
    return img.point(contrast)


def add_noise(img, factor):
    def noise(c):
        return c*(1+np.random.random(1)[0]*factor-factor/2)
    return img.point(noise)


# add lens flares to coords in given image
def add_flares(img, coords):
    ret = img.copy()

    flare = Image.open("assets/frying/lens_flare.png")
    for coord in coords:
        ret.paste(flare, (int(coord[0] - flare.size[0] / 2), int(coord[1] - flare.size[1] / 2)), flare)

    return ret


def add_b_emojis(img, coords):
    tmp = img.copy()

    b = Image.open("assets/frying/B.png")
    for coord in coords:
        if np.random.random(1)[0] < 0.1:
            resized = b.copy()
            resized.thumbnail((coord[2], coord[3]), Image.ANTIALIAS)
            tmp.paste(resized, (int(coord[0]), int(coord[1])), resized)

    return tmp


def add_laughing_emojis(img, max_emojis):
    ret = img.copy()

    emoji = Image.open("assets/frying/smilelaugh.png")
    for i in range(int(np.random.random(1)[0] * max_emojis)):
        coord = np.random.random(2) * np.array([img.width, img.height])
        resized = emoji.copy()
        size = int((img.width / 10) * (np.random.random(1)[0] + 1))
        resized.thumbnail((size, size), Image.ANTIALIAS)
        ret.paste(resized, (int(coord[0]), int(coord[1])), resized)

    return ret


# creates a bulge like distortion to the image
# parameters:
#   img = PIL image
#   f   = np.array([x, y]) coordinates of the centre of the bulge
#   r   = radius of the bulge
#   a   = flatness of the bulge, 1 = spherical, > 1 increases flatness
#   h   = height of the bulge
#   ior = index of refraction of the bulge material
def bulge(img, f, r, a, h, ior):
    width = img.width
    height = img.height
    img_data = np.array(img)

    # ignore large images
    if width * height > 3000 * 3000:
        return img

    # determine range of pixels to be checked (square enclosing bulge), max exclusive
    x_min = int(f[0] - r)
    if x_min < 0:
        x_min = 0
    x_max = int(f[0] + r)
    if x_max > width:
        x_max = width
    y_min = int(f[1] - r)
    if y_min < 0:
        y_min = 0
    y_max = int(f[1] + r)
    if y_max > height:
        y_max = height

    # make sure that bounds are int and not np array
    if isinstance(x_min, np.ndarray):
        x_min = x_min[0]
    if isinstance(x_max, np.ndarray):
        x_max = x_max[0]
    if isinstance(y_min, np.ndarray):
        y_min = y_min[0]
    if isinstance(y_max, np.ndarray):
        y_max = y_max[0]

    # array for holding bulged image
    bulged = np.copy(img_data)
    for y in range(y_min, y_max):
        for x in range(x_min, x_max):
            ray = np.array([x, y])

            # find the magnitude of displacement in the xy plane between the ray and focus
            s = length(ray - f)

            # if the ray is in the centre of the bulge or beyond the radius it doesn't need to be modified
            if 0 < s < r:
                # slope of the bulge relative to xy plane at (x, y) of the ray
                m = -s / (a * math.sqrt(r ** 2 - s ** 2))

                # find the angle between the ray and the normal of the bulge
                theta = np.pi / 2 + np.arctan(1 / m)

                # find the magnitude of the angle between xy plane and refracted ray using snell's law
                phi = np.abs(np.arctan(1 / m) - np.arcsin(np.sin(theta) / ior))

                # find length the ray travels in xy plane before hitting z=0
                k = (h + (math.sqrt(r ** 2 - s ** 2) / a)) / np.sin(phi)

                # find intersection point
                intersect = ray + normalise(f - ray) * k

                # assign pixel with ray's coordinates the colour of pixel at intersection
                if 0 < intersect[0] < width - 1 and 0 < intersect[1] < height - 1:
                    bulged[y][x] = img_data[int(intersect[1])][int(intersect[0])]
                else:
                    bulged[y][x] = [0, 0, 0]
            else:
                bulged[y][x] = img_data[y][x]
    img = Image.fromarray(bulged)
    return img


async def download_image(cs, url, fmt="RGB"):
    try:
        async with cs.get(url) as resp:
            try:
                img = Image.open(io.BytesIO(await resp.content.read())).convert(fmt)
            except OSError:
                img = None
    except aiohttp.InvalidURL:
        img = None

    return img


# remove special characters from string
def remove_specials(string):
    return "".join(c for c in string if c.isalnum()).lower()


# return the length of vector v
def length(v):
    return np.sqrt(np.sum(np.square(v)))


# returns the unit vector in the direction of v
def normalise(v):
    return v / length(v)


@async_executor()
def _combine(one, two):
    a = Image.open(one).resize((256, 256)).convert("RGBA")
    b = Image.open(two).resize((256, 256)).convert("RGBA")
    lx, ly = a.size
    fin = Image.new("RGBA", a.size)
    for x in range(lx):
        for y in range(ly):
            if (x + y) % 2 == 0:
                px = a.getpixel((x, y))
            else:
                px = b.getpixel((x, y))
            fin.putpixel((x, y), px)
    n = io.BytesIO()
    fin.save(n, "png")
    n.seek(0)

    return n


@async_executor()
def _invert(img):
    inverted = PIL.ImageOps.invert(img)

    fp = io.BytesIO()
    inverted.save(fp, "png")
    fp.seek(0)

    return fp


@async_executor()
def _posterize(img):
    postered = PIL.ImageOps.posterize(img, 1)

    fp = io.BytesIO()
    postered.save(fp, "png")
    fp.seek(0)

    return fp


@async_executor()
def _solarize(img):
    solarized = PIL.ImageOps.solarize(img)

    fp = io.BytesIO()
    solarized.save(fp, "png")
    fp.seek(0)

    return fp


@async_executor()
def invert_along(img, axis):
    if axis == "x":
        ret = PIL.ImageOps.flip(img)
    elif axis == "y":
        ret = PIL.ImageOps.mirror(img)

    fp = io.BytesIO()
    ret.save(fp, "png")
    fp.seek(0)

    return fp


def link(arr, arr2):
    rgb1 = arr.reshape((arr.shape[0] * arr.shape[1], 3))
    rgb2 = list(map(tuple, arr2.reshape((arr2.shape[0] * arr2.shape[1], 3))))
    template1 = {x: [0, []] for x in rgb2}
    for x, y in zip(rgb2, rgb1):
        template1[x][1].append(y)
    return template1


def reset_template(template):
    for v in template.values():
        v[0] = 0


def process_sorting(img, img2):
    arr = np.array(img)
    arr2 = np.array(img2)

    shape = arr.shape
    npixs = shape[0] * shape[1]
    valid = []
    for i in range(1, npixs + 1):
        num = npixs / i
        if num.is_integer():
            valid.append((int(num), i))

    frames = []
    way_back = []
    for v in valid:
        arr = arr.reshape((v[0], v[1], shape[2]))
        arr.view("uint8,uint8,uint8").sort(order=["f2"], axis=1)
        arr2 = arr2.reshape((v[0], v[1], shape[2]))
        arr2.view("uint8,uint8,uint8").sort(order=["f2"], axis=1)
        new = Image.fromarray(arr.reshape(shape))
        frames.append(new)
        ar2 = copy.copy(arr2)
        way_back.append(ar2)

    template = link(arr, arr2)

    for way in reversed(way_back):
        for i, z in enumerate(way[:, :, ]):
            for x, rgb in enumerate(z):
                thing = template[tuple(rgb)]
                way[:, :, ][i][x] = thing[1][thing[0]]
                thing[0] += 1
        new = Image.fromarray(way.reshape(shape))
        frames.append(new)
        reset_template(template)

    for i in range(5):
        frames.insert(0, frames[0])
        frames.append(frames[-1])
    frames += list(reversed(frames))
    return frames


@async_executor()
def process_transform(img1, img2):
    img1 = img1.resize((256, 256), Image.NEAREST)
    if img1.mode != "RGB":
        img1 = img1.convert("RGB")
    img2 = img2.resize((256, 256), Image.NEAREST)
    if img2.mode != "RGB":
        img2 = img2.convert("RGB")
    frames = process_sorting(img1, img2)

    buff = io.BytesIO()
    frames[0].save(
            buff,
            "gif",
            save_all=True,
            append_images=frames[1:] + frames[-1:] * 5,
            duration=125,
            loop=0
        )
    buff.seek(0)
    return buff


@async_executor()
def _grayscale(img):
    fp = io.BytesIO()
    PIL.ImageOps.grayscale(img).save(fp, "png")
    fp.seek(0)

    return fp


@async_executor()
def _emboss(img):
    fp = io.BytesIO()
    img.filter(PIL.ImageFilter.EMBOSS).save(fp, "png")
    fp.seek(0)

    return fp


@async_executor()
def _blur(img):
    img = img.resize((256, 256))

    frames = []

    for i in range(0, 200, 20):
        frames.append(img.filter(PIL.ImageFilter.BoxBlur(i / 10)))

    fp = io.BytesIO()
    frames[0].save(fp, "gif", save_all=True, append_images=frames[1:] + list(reversed(frames)), loop=0,
                   duration=100)
    fp.seek(0)

    return fp


async def process_single_arg(ctx, argument):
    if argument is None:
        is_found = False
        for att in ctx.message.attachments:
            if att.height is not None and not is_found:
                url = att.proxy_url
                is_found = True
        if not is_found:
            url = str(ctx.author.avatar_url_as(format="png", size=1024))
    else:
        try:
            url = str(
                (await commands.MemberConverter().convert(ctx, argument)).avatar_url_as(format="png", size=1024)
            )
        except commands.BadArgument:
            try:
                url = str(
                    (await commands.UserConverter().convert(ctx, argument)).avatar_url_as(format="png", size=1024)
                )
            except commands.BadArgument:
                url = argument

    try:
        async with ctx.bot.http2.get(url) as resp:
            try:
                img = Image.open(io.BytesIO(await resp.content.read())).convert("RGB")
            except OSError:
                await ctx.send(":x: That URL is not an image.")
                return
    except aiohttp.InvalidURL:
        await ctx.send(":x: That URL is invalid.")
        return

    return img


# To avoid confusion with PIL.Image
class Image_(commands.Cog, name="Image",
             command_attrs=dict(cooldown=commands.Cooldown(1, 2, commands.BucketType.member))):
    """All commands in this cog that take one argument can use an URL or a member/user. These commands can also use
     a message attachment. If nothing is given, the message author's avatar is used."""

    @commands.command(
        aliases=["df"]
    )
    async def deepfry(self, ctx, *, url=None):
        """Deepfry an image."""

        async with ctx.typing():
            url = await process_single_arg(ctx, url)
            if url is None:  # An error message was sent
                return

            t = time.time()
            img = await fry(url)
            t = round(time.time() - t, 3)

            fp = discord.File(img, "deepfried.png")

        await ctx.send(f"That took about {t} seconds", file=fp)

    @commands.command(
        aliases=["cmb"],
        description="Combine your avatar and that of another user. Example: `s!transform \"Too Laggy#3878\" @SuprKewl"
                    " Bot`"
    )
    async def combine(
            self, ctx,
            user1: typing.Union[discord.Member, discord.User],
            *, user2: typing.Union[discord.Member, discord.User] = None
    ):
        """Combine two avatars."""

        async with ctx.typing():
            if not user2:
                user2 = user1
                user1 = ctx.author

            if user1 == user2:
                return await ctx.send(":question: You can't combine with yourself!")

            a1 = io.BytesIO(await user1.avatar_url_as(format="png").read())
            a2 = io.BytesIO(await user2.avatar_url_as(format="png").read())

            f = await _combine(a1, a2)
            f = discord.File(f, "combined.png")

        await ctx.send(":white_check_mark:", file=f)

    @commands.command(
        aliases=["inv"],
        description="Invert an image."
    )
    async def invert(self, ctx, *, url=None):
        """Invert the colors of an image."""

        url = await process_single_arg(ctx, url)
        if url is None:  # An error message was sent
            return

        inverted = await _invert(url)
        fp = discord.File(inverted, "image.png")
        await ctx.send(":white_check_mark:", file=fp)

    @commands.command(
        aliases=["gs"],
        description="Grayscale an image."
    )
    async def grayscale(self, ctx, *, url=None):
        """Convert an image to grayscale."""

        url = await process_single_arg(ctx, url)
        if url is None:  # An error message was sent
            return

        fp = await _grayscale(url)

        fp = discord.File(fp, "gray.png")
        await ctx.send(":white_check_mark:", file=fp)

    @commands.command(
        aliases=["dk"],
        description="Darken all pixels of an image."
    )
    async def darken(self, ctx, *, url=None):
        """Darken an image."""

        url = await process_single_arg(ctx, url)
        if url is None:  # An error message was sent
            return

        postered = await _posterize(url)
        fp = discord.File(postered, "poster.png")
        await ctx.send(":white_check_mark:", file=fp)

    @commands.command(
        aliases=["sz"],
        description="Solarize an image."
    )
    async def solarize(self, ctx, *, url=None):
        """Invert all pixels of an an image above a certain brightness."""

        url = await process_single_arg(ctx, url)
        if url is None:  # An error message was sent
            return

        solarized = await _solarize(url)
        fp = discord.File(solarized, "image.png")
        await ctx.send(":white_check_mark:", file=fp)

    @commands.group(description="Invert an image along an axis. Specify `x` or `y`.")
    async def flip(self, ctx):
        """Invert an image along a given axis."""

        if ctx.invoked_subcommand is None:
            await ctx.send(":x: Please specify an axis to invert along. Only `x` and `y` are valid.")

    @flip.command(name="x")
    async def flip_x(self, ctx, *, url=None):
        """Invert along the x axis, a.k.a. flip."""

        url = await process_single_arg(ctx, url)
        if url is None:  # An error message was sent
            return

        flipped = await invert_along(url, "x")
        fp = discord.File(flipped, "image.png")
        await ctx.send(":white_check_mark:", file=fp)

    @flip.command(name="y")
    async def flip_y(self, ctx, *, url=None):
        """Invert along the y axis, a.k.a. mirror."""

        url = await process_single_arg(ctx, url)
        if url is None:  # An error message was sent
            return

        flipped = await invert_along(url, "y")
        fp = discord.File(flipped, "image.png")
        await ctx.send(":white_check_mark:", file=fp)

    @commands.command(aliases=["emb"])
    async def emboss(self, ctx, *, url=None):
        """Generate an embossed version of an image."""

        url = await process_single_arg(ctx, url)
        if url is None:  # An error message was sent
            return

        fp = await _emboss(url)
        fp = discord.File(fp, "embossed.png")

        await ctx.send(":white_check_mark:", file=fp)

    @commands.command(aliases=["bl"])
    async def blur(self, ctx, *, url=None):
        """Generate a GIF that blurs and unblurs an image."""

        async with ctx.typing():
            t = time.time()

            url = await process_single_arg(ctx, url)
            if url is None:  # An error message was sent
                return

            fp = await _blur(url)
            fp = discord.File(fp, "blurred.gif", spoiler=True)  # This really messes with your eyes

            t = round(time.time() - t, 3)

        await ctx.send(f":white_check_mark: That took {t} seconds.\n Warning - staring at this for too long might make "
                       "your eyes hurt...", file=fp)

    @commands.command(
        aliases=["ts", "tf"],
        description="If you only specify one member, I will transform their avatar to yours."
                    " Example: `s!transform \"Too Laggy#3878\" @SuprKewl Bot`"
    )
    async def transform(
            self, ctx,
            user: typing.Union[discord.Member, discord.User],
            *, other: typing.Union[discord.Member, discord.User] = None
    ):
        """Transform the avatar of one user to that of another and back."""

        other = other or ctx.author

        # Save bandwidth
        im1 = Image.open(io.BytesIO(await user.avatar_url_as(format="png", size=256).read()))
        im2 = Image.open(io.BytesIO(await other.avatar_url_as(format="png", size=256).read()))
        async with ctx.typing():
            t = time.time()

            if other == ctx.author:
                buff = await process_transform(im2, im1)
            else:
                buff = await process_transform(im1, im2)

            t = round(time.time() - t, 3)

            await ctx.send(
                f":white_check_mark: That took about {t} seconds.", file=discord.File(buff, "transform.gif"))


def setup(bot):
    bot.add_cog(Image_())
