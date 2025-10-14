"""
RenertPy Python Package
Copyright (C) 2022 Assaf Gordon (assafgordon@gmail.com)
License: BSD (See LICENSE file)
"""
import warnings
import colorsys

def rgb_to_hsv(r,g,b):
    if not (r>=0 and r<=255):
        raise ValueError("Invalid r (red) value '%s': must be between 0 and 255" % str(r))
    if not (g>=0 and g<=255):
        raise ValueError("Invalid g (green) value '%s': must be between 0 and 255" % str(g))
    if not (b>=0 and b<=255):
        raise ValueError("Invalid b (blue) value '%s': must be between 0 and 255" % str(b))

    h,s,v = colorsys.rgb_to_hsv(r/255,g/255,b/255)

    h = int(h * 360) # convert to degrees

    return [h,s,v]

def hsv_to_rgb(h,s,v):
    if not (h>=0 and h<=360):
        raise ValueError("Invalid h (hue) value '%s': must be between 0 and 360" % str(h))
    if not (s>=0.0 and s<=1.0):
        raise ValueError("Invalid s (saturation) value '%s': must be between 0.0 and 1.0" % str(s))
    if not (v>=0 and v<=255):
        raise ValueError("Invalid v (value) value '%s': must be between 0 and 255" % str(v))

    r,g,b = colorsys.hsv_to_rgb(h/360,s,v)

    return [int(r*255), int(g*255), int(b*255)]


def hexcolor_to_rgb(cstr):
    # Python's Turtle has an undocumented function for this
    # ( TBuffer._color(str,cstr) ) which is nice an efficient,
    # but not user-friendly when given invalid input.
    # Since this module is meant for newbies, be less efficient and
    # more verbose with invalid input.
    if not cstr.startswith("#"):
        raise ValueError(f"invalid hex-color string '{cstr}' - must start with '#'")

    # Check if all the characeters (after '#') are hex-digits.
    # Here we don't yet care about the actual length - any length of valid hex-digits will work.
    # This code is less intuitive than standard check (e.g. regex or loop) but is more efficient
    # (as this is expected to be called once per pixel)
    try:
        dummy = int(cstr[1:], 16)
    except ValueError:
        raise ValueError(f"invalid hex-color string '{cstr}' - must start with '#' followed by 0-9,A-F characters")

    if len(cstr)==7:
        # Copied from turtle's _color()
        cl = [int(cstr[i:i+2], 16) for i in (1, 3, 5)]
    elif len(cstr)==4:
        # Copied from turtle's _color()
        cl = [16*int(h, 16) for h in cstr[1:]]
    else:
        raise ValueError(f"invalid hex-color string '{cstr}' - be '#' followed by 3 or 6 characters")

    return tuple(cl)

