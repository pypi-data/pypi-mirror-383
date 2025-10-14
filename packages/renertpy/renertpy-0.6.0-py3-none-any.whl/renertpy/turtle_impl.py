"""
RenertPy Python Package
Copyright (C) 2025 Assaf Gordon (assafgordon@gmail.com)
License: BSD (See LICENSE file)
"""

from uuid import uuid4
from turtle import getscreen,register_shape,Shape,stamp,penup,pendown,isdown,colormode,pos,goto,shape
from PIL import Image, ImageTk
from .colors import hexcolor_to_rgb
from .data import get_data_bw, get_data_rgb, load_picture_data
from .utils import is_numeric_iterable, is_str_iterable, is_rgb_iterable

def create_image_from_grayscale_data(pixel_data, width):
    height = len(pixel_data) // width
    if len(pixel_data) % width != 0:
        raise ValueError(f"The number of pixels ({len(pixel_data)}) is not divisible by width {width}")

	# "L" is 8-bit grayscale
    image = Image.frombytes('L', (width, height), bytes(pixel_data))
    return image

def create_image_from_rgb_triplets(rgb_data, width):
    """
    Creates a Pillow Image object from a list of RGB triplets.

    Args:
        rgb_triplets (list): A list of tuples, where each tuple is an (R, G, B) value.
                             Example: [(255, 0, 0), (0, 255, 0), ...]
        width (int): The desired width of the image.

    Returns:
        A Pillow Image object.
    """
    if len(rgb_data) % width != 0:
        raise ValueError(f"The number of pixels ({len(rgb_data)}) is not divisible by width {width}")

    height = len(rgb_data) // width

    # Flatten the list of (R,G,B) triplets into a single list [R,G,B,R,G,B,...]
    flat_pixel_data = [channel for triplet in rgb_data for channel in triplet]

    image = Image.frombytes('RGB', (width, height), bytes(flat_pixel_data))
    return image


def create_image_from_colornames(color_names, width):
    """
    Creates a Pillow Image object from a list of strings(=color names or HEX values).

    Returns:
        A Pillow Image object.
    """
    if colormode() != 255:
        raise RuntimeError("Please set colormode(255)")

    height = len(color_names) // width
    if len(color_names) % width != 0:
        raise ValueError(f"The number of pixels ({len(color_names)}) is not divisible by width {width}")

 
    # Convert the list of colors into a single list [R,G,B,R,G,B,...]
    flat_pixel_data = []
    for c in color_names:
        if c.startswith("#"):
            # assume it's a hexcolor (e.g. "#FFF" or "#FFFFFF")
            r,g,b = hexcolor_to_rgb(c)
        else:
            # Assume it's a color name, convert it to RGB with TK's standard function.
            rgb_16bit = getscreen().cv.winfo_rgb(c)
            # Convert TK's 16-bit values to standard 8-bit values
            rgb_8bit = tuple(value >> 8 for value in rgb_16bit)
            r,g,b = rgb_8bit
            
        flat_pixel_data.append(r)
        flat_pixel_data.append(g)
        flat_pixel_data.append(b)
        
    image = Image.frombytes('RGB', (width, height), bytes(flat_pixel_data))
    return image


def resize_image(image, new_width, new_height=None):
    width = image.width
    height = image.height
    
    if new_height is None:
        new_height  = round((new_width / width) * height)
    
    new_dimension = (new_width, new_height)

    # NOTE about resampling:
    # normally we would want fancy resampling to reduce pixelation of enlarged images.
    # But this is a teaching module for newbies:
    # IF they provide a 3 pixel image (e.g. data = ["red","pink","blue"] ) - when enlarging the image
    # (e.g. to 150 pixels on the screen, for visualization)
    # they expect to still see three distinct (big) squares - not a gradient.
    # "NEAREST" effectively disables resampling.
    resized_image = image.resize(new_dimension, resample=Image.Resampling.NEAREST)
    return resized_image

def create_photoimage_from_image(image):
    # This dummy call ensure there's an initialized screen.
    # otherwise, TK.PhotoImage() fails with "no root window"
    dummy = getscreen()
    photo_image = ImageTk.PhotoImage(image=image)
    return photo_image


def draw_photoimage_at_turtle(photo_image):
    current_shape = shape()
    shape_id = str(uuid4())
    shape_obj = Shape("image", photo_image)
    register_shape(shape_id, shape_obj)
    shape(shape_id)
    stamp()
    shape(current_shape)

def draw_data_bw(grayscale_image_data, width, resize_width=None):
    im = create_image_from_grayscale_data(grayscale_image_data, width)
    if resize_width:
        im = resize_image(im, resize_width)
    pi = create_photoimage_from_image(im)
    draw_photoimage_at_turtle(pi)

def draw_data_rgb(rgb_image_data, width, resize_width=None):
    im = create_image_from_rgb_triplets(rgb_image_data, width)
    if resize_width:
        im = resize_image(im, resize_width)
    pi = create_photoimage_from_image(im)
    draw_photoimage_at_turtle(pi)

def draw_data_colornames(colornames_image_data, width, resize_width=None):
    im = create_image_from_colornames(colornames_image_data, width)
    if resize_width:
        im = resize_image(im, resize_width)
    pi = create_photoimage_from_image(im)
    draw_photoimage_at_turtle(pi)


def draw_image(image_data, width, resize_width=None, center=False):
    if is_numeric_iterable(image_data):
        im = create_image_from_grayscale_data(image_data, width)
    elif is_str_iterable(image_data):
        im = create_image_from_colornames(image_data, width)
    elif is_rgb_iterable(image_data):
        im = create_image_from_rgb_triplets(image_data, width)
    else:
        raise ValueError("Unknown type of image_data (expecting: list of integers, RGB, or color-names)")
        
    if resize_width:
        im = resize_image(im, resize_width)
        
    pi = create_photoimage_from_image(im)
    
    if not center:
        old_x, old_y = pos()
        w = im.width
        h = im.height
        is_pen_down = isdown()
        penup()
        # TODO: fix the +/- depending on the logomode
        goto(old_x + w //2 , old_y - h // 2)
        pendown()
        
    draw_photoimage_at_turtle(pi)

    if not center:
        penup()
        goto(old_x, old_y)
        if is_pen_down:
            pendown()


