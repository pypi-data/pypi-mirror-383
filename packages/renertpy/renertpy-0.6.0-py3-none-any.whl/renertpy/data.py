"""
RenertPy Python Package
Copyright (C) 2022 Assaf Gordon (assafgordon@gmail.com)
License: BSD (See LICENSE file)
"""

from .utils import load_image_as_2d_rgb_list,rgb_list_to_gray_scale
import os
import copy

files = {
        "balls" : "balls.jpg",
        "butterfly" : "butterfly.jpg",
        "kitten" : "kitten.jpg",
        "llama" : "llama.jpg",
        "panda" : "panda.jpg",
        "parrot" : "parrot.jpg",
        "puppy" : "puppy.jpg",
        "rose" : "rose.jpg",
        "sloth" : "sloth.jpg",
        "tulips" : "tulips.jpg"
    }            

images = { }

def load_picture_data():
    global images

    rootdir = os.path.abspath(os.path.dirname(__file__))
    datadir = os.path.join(rootdir,"data")

    for k,filename in files.items():
            rgb_data = load_image_as_2d_rgb_list( os.path.join(datadir,filename) )
            bw_data = rgb_list_to_gray_scale(rgb_data)

            images[k + "_rgb"] = rgb_data
            images[k + "_bw"] = bw_data

def get_data(image,suffix):
    if (suffix not in ["rgb","bw"]):
        raise ValueError("Invalid suffix '%s': use rgb or bw" % (str(suffix)))

    key = image + "_" + suffix
    if not (key in images):
        raise ValueError("Invalid image name '%s': use one of: %s" \
                % ( str(image), ",".join(files.keys())))
    return copy.deepcopy( images[key] )

def get_data_rgb(image):
    return get_data(image,"rgb")

def get_data_bw(image):
    return get_data(image,"bw")

def get_data_parrot_rgb():
    return get_data_rgb("parrot")

def get_data_parrot_bw():
    return get_data_bw("parrot")
    
def get_data_butterfly_rgb():
    return get_data_rgb("butterfly")

def get_data_butterfly_bw():
    return get_data_bw("butterfly")
