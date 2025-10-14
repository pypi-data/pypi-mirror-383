"""
RenertPy Python Package
Copyright (C) 2022 Assaf Gordon (assafgordon@gmail.com)
License: BSD (See LICENSE file)
"""

import warnings

import numpy as np
from PIL import ImageColor, Image
from ipycanvas import Canvas

from .utils import (check_iterable,
                    check_numeric_iterable,
                    check_numeric_iterable_2d,
                    truncate_list,
                    check_color_name,
                    validate_color_name,
                    check_colorname_iterable,
                    calc_dest_image_size)

def base_canvas(width = 1000,height = 100):
    canvas = Canvas(width=width,height=height)
    return canvas

def bar_plot(data,color="black",width=1000,height=100):
    check_iterable(data)
    check_numeric_iterable(data)
    data = truncate_list(data, 100)

    canvas = base_canvas()
    canvas.stroke_style = "gray"
    canvas.stroke_line(0,height,width,height)
    barwidth = width / len(data)
    canvas.fill_style = color
    for i,val in enumerate(data):
        canvas.fill_rect(i*barwidth, height-val, barwidth, val)
    return canvas

def line_plot(data,color="black",width=1000,height=100):
    check_iterable(data)
    check_numeric_iterable(data)
    data = truncate_list(data, 100)

    canvas = base_canvas()
    barwidth = width / len(data)
    canvas.stroke_style = "gray"
    canvas.stroke_line(0,0,0,height)
    canvas.stroke_line(0,50,barwidth*(len(data)-1),50)

    canvas.stroke_style = color
    canvas.begin_path()
    for i,val in enumerate(data):
        if i == 0:
            canvas.move_to(i*barwidth, 50 - val/2)
        else:
            canvas.line_to(i*barwidth, 50 - val/2)
    canvas.stroke()

    return canvas


def plot_single_color_image(data,src_width,src_height,dest_width,dest_height,color=None):
    check_iterable(data)
    check_numeric_iterable(data)

    color = validate_color_name(color)

    if src_height != (len(data) / src_width):
        raise ValueError("data length %d elements does match match src_width(%d) * src_height(%d)" % (len(data), src_width, src_height) )

    # Get the RGB values of the color (from a color name, or html #RGB)
    rgb = ImageColor.getrgb(color)

    # Create a numpy array of 0.0 to 1.0 (from greyscale input elements of 0-255)
    np_data = np.asarray(data)
    np_data = np_data / 255

    # Calculate corresponding RGB values for each greyscale input element
    r = np_data * rgb[0]
    g = np_data * rgb[1]
    b = np_data * rgb[2]

    # Merge into one numpy array and reshape it into WxHx3 (3 = for RGB)
    foo = np.dstack( (r,g,b))
    foo = np.reshape(foo, (src_height,src_width,3))

    image = Image.fromarray(foo.astype('uint8'), mode="RGB")
    image = image.resize((dest_width,dest_height),resample=Image.NEAREST)
    return image

def greyscale_plot(data,color=None):
    return plot_single_color_image(data, len(data), 1, 1000, 100, color)

def greyscale_2d_plot(data,width,color=None):
    max_size = 150

    height = len(data)//width
    if width>max_size or height>max_size:
        raise ValueError("image too large (%d x %d), max allowed width/height is %d pixels" % ( width,height,max_size ) )

    h_aspect = max_size / width
    v_aspect = max_size / height
    aspect = min(h_aspect,v_aspect)
    dst_width = round(aspect * width)
    dst_height = round(aspect * height)

    return plot_single_color_image(data, width, height , dst_width, dst_height, color)

def colorname_plot(data):
    check_iterable(data)
    check_colorname_iterable(data)
    dest_width = 1000
    dest_height = 100

    rgbs = [ImageColor.getrgb(x) for x in data]
    np_data = np.asarray(rgbs)
    foo = np.reshape(np_data, (1, len(rgbs), 3))

    image = Image.fromarray(foo.astype('uint8'), mode="RGB")
    image = image.resize((dest_width,dest_height),resample=Image.NEAREST)
    return image


def rgb_plot(data):
    check_iterable(data)
    check_numeric_iterable_2d(data)

    dest_width = 1000
    dest_height = 100


    # Create a numpy array of 0.0 to 1.0 (from greyscale input elements of 0-255)
    np_data = np.asarray(data)

    # Merge into one numpy array and reshape it into WxHx3 (3 = for RGB)
    foo = np.reshape(np_data, (1, len(data), 3))

    image = Image.fromarray(foo.astype('uint8'), mode="RGB")
    image = image.resize((dest_width,dest_height),resample=Image.NEAREST)
    return image

def rgb_2d_plot(data,width):
    check_iterable(data)
    check_numeric_iterable_2d(data)

    height = len(data)//width
    (dw,dh) = calc_dest_image_size( width, height )

    # Create a numpy array of 0.0 to 1.0 (from greyscale input elements of 0-255)
    np_data = np.asarray(data)

    # Merge into one numpy array and reshape it into WxHx3 (3 = for RGB)
    foo = np.reshape(np_data, (height, width, 3))

    image = Image.fromarray(foo.astype('uint8'), mode="RGB")
    image = image.resize((dw,dh),resample=Image.NEAREST)
    return image
