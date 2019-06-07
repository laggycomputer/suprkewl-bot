import io
import math
import os

import aiohttp
import cv2
import discord
from discord.ext import commands
import numpy as np
from PIL import Image


PWD = os.getcwd()


def _fry(img):
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

    return img


async def fry(ctx, img):
    return await ctx.bot.loop.run_in_executor(None, _fry, img)


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

    flare = Image.open(PWD + "/../assets/lens_flare.png")
    for coord in coords:
        ret.paste(flare, (int(coord[0] - flare.size[0] / 2), int(coord[1] - flare.size[1] / 2)), flare)

    return ret


def add_b_emojis(img, coords):
    tmp = img.copy()

    b = Image.open(PWD + "/../assets/B.png")
    for coord in coords:
        if np.random.random(1)[0] < 0.1:
            resized = b.copy()
            resized.thumbnail((coord[2], coord[3]), Image.ANTIALIAS)
            tmp.paste(resized, (int(coord[0]), int(coord[1])), resized)

    return tmp


def add_laughing_emojis(img, max_emojis):
    ret = img.copy()

    emoji = Image.open(PWD + "/../assets/smilelaugh.png")
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


async def download_image(ctx, url):
    try:
        async with ctx.bot.http2.get(url) as resp:
            try:
                img = Image.open(io.BytesIO(await resp.content.read())).convert("RGB")
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


class Image_(commands.Cog, name="Image"):  # To avoid confusion with PIL.Image

    @commands.command()
    @commands.guild_only()
    async def deepfry(self, ctx, *, url=None):
        """Deepfry an image. Specify a member to use their avatar, or no URL to use yours."""

        if url is None:
            url = str(ctx.author.avatar_url_as(format="png", size=1024))
        else:
            try:
                member = await commands.MemberConverter().convert(ctx, url)
                url = str(member.avatar_url_as(format="png", size=1024))
            except commands.BadArgument:
                pass

        async with ctx.typing():
            img = await download_image(ctx, url)
            if img is None:
                sent = await ctx.send(
                    "That argument does not seem to be an image, and does not seem to be a member of this server.")
                return await ctx.register_response(sent)

            img = await fry(ctx, await fry(ctx, img))  # One fry is very weak
            fname = str(ctx.message.id) + ".png"
            try:
                img.save(fname, format="png")
            except IOError:
                sent = await ctx.send(
                    "Your image was rendered but could not be saved, please try again later. :slight_frown:")
                return await ctx.register_response(sent)

            fp = discord.File(fname, "deepfried.png")

        sent = await ctx.send(file=fp)
        os.remove(fname)
        await ctx.register_response(sent)


def setup(bot):
    bot.add_cog(Image_())
