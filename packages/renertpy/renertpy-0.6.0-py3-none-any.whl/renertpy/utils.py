"""
RenertPy Python Package
Copyright (C) 2022 Assaf Gordon (assafgordon@gmail.com)
License: BSD (See LICENSE file)
"""
import warnings
from PIL import ImageColor
import numpy
import PIL

def check_iterable(data):
    # Will raise a "type error: data is not iterable"
    some_object_iterator = iter(data)

def check_color_name(data):
    if not isinstance(data,str):
        raise ValueError("value '%s' is not a valid color name" % (str(data)))
    try:
        x = ImageColor.getrgb(data)
    except ValueError:
        raise ValueError("value '%s' is not a valid color name" % (str(data)))

def validate_color_name(data):
    if data is None:
        return "white"
    check_color_name(data)
    return data

def check_numeric_iterable(data):
    # Will raise ValueError if one of the elements isn't numeric
    for i,val in enumerate(data):
        try:
            b = 0 + val
        except (ValueError,TypeError):
            raise ValueError("Element #" + str(i) + " is not numeric ('" + str(val) + "')")

def is_numeric_iterable(data):
    try:
        check_numeric_iterable(data)
        return True
    except ValueError:
        return False

def check_str_iterable(data):
    # Will raise ValueError if one of the elements isn't a string
    for i,val in enumerate(data):
        if not isinstance(val,str):
            raise ValueError("Element #" + str(i) + " is not a string ('" + str(val) + "')")

def is_str_iterable(data):
    try:
        check_str_iterable(data)
        return True
    except ValueError:
        return False

def check_colorname_iterable(data):
    # Will raise ValueError if one of the elements isn't numeric
    for i,val in enumerate(data):
        try:
            check_color_name(val)
        except ValueError:
            raise ValueError("Element #" + str(i) + " is not a valid color name ('" + str(val) + "')")


def check_numeric_iterable_2d(data):
    dim = None # dimension of 2nd array must be the same for all elements (i.e. a valid matrix)

    # Will raise ValueError if one of the elements isn't numeric
    for i,arr1 in enumerate(data):

        # Will raise a "type error: data is not iterable"
        try:
            some_object_iterator = iter(arr1)
            if isinstance(arr1, str):
                raise ValueError("Element [%d] (content = '%s') is not a list (expecting list-of-lists)" % (i, str(arr1)))

        except TypeError:
            raise ValueError("Element [%d] (content = '%s') is not a list (expecting list-of-lists)" % (i, str(arr1)))
        l = len(arr1)
        if not dim:
            dim = l
        else:
            if dim != l:
                raise ValueError("list-of-lists length error: previous sub-lists had %d elements, but list #%d has %d elements" % ( dim, i, l ))
        for j,val in enumerate(arr1):
            try:
                b = 0 + val
            except (TypeError,ValueError):
                raise ValueError("Element [%d][%d] is not numeric (content = '%s')" % (i,j,str(val)))


def is_rgb_iterable(data):
    try:
        # First, check it's a 2D numeric data
        check_numeric_iterable_2d(data)

        # then check if the 2nd dimension is 3 (for r,g,b)
        if len(data[0])==3:
            return True

        return False
    except ValueError:
        return False


def truncate_list(data, max_count):
    count = min(100, len(data))
    if count != len(data):
        warnings.warn("Got too many elements, drawing only first 100 elements")
        data = list(data)
        data = data[:count]
    return data

def calc_dest_image_size(width,height,max_size=150):
    if width>max_size or height>max_size:
        raise ValueError("image too large (%d x %d), max allowed width/height is %d pixels" % ( width,height,max_size ) )

    h_aspect = max_size / width
    v_aspect = max_size / height
    aspect = min(h_aspect,v_aspect)
    dst_width = round(aspect * width)
    dst_height = round(aspect * height)
    return (dst_width, dst_height)

def load_image_as_2d_rgb_list(filename):
    npdata = numpy.asarray(PIL.Image.open(filename))
    dims = npdata.shape
    b = npdata.reshape(1, dims[0] * dims[1], 3 )
    data = b.tolist()[0]
    return data

def rgb_list_to_gray_scale(data):
    bw_data = [ (x[0]+x[1]+x[2])//3 for x in data ]
    return bw_data
