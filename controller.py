#!/usr/bin/env python

"""
controller.py

"""
import os
import argparse
import pickle
import re
import time

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt



def add_sphere(position, radius, color):
    """Add sphere to scene."""

    return dict(type='sphere', position=np.array(position),
        radius=np.array(radius), color=np.array(color), reflection=.5)


def add_plane(position, normal, color_plane0, color_plane1):
    """Add plane to scene."""
    return dict(type='plane', position=np.array(position),
        normal=np.array(normal), color_plane0=color_plane0,
        color_plane1=color_plane1, diffuse_c=.75, specular_c=.5,
        reflection=.25)


def create_scene():
    """Creates and serializes scene description to persistent volume."""

    scene_params = {
        # list of scene objects
        'scene_objects': [
            add_sphere([.75, .1, 1.], .6, [0., 0., 1.]),
            add_sphere([-.75, .1, 2.25], .6, [.5, .223, .5]),
            add_sphere([-2.75, .1, 3.5], .6, [1., .572, .184]),
            add_plane([0., -.5, 0.], [0., 1., 0.],
                      1. * np.ones(3), 0. * np.ones(3)),
        ],

        # Light position and color.
        'L': np.array([5., 5., -10.]),
        'color_light': np.ones(3),

        # Default light and material parameters.
        'ambient': .05,
        'diffuse_c': 1.,
        'specular_c': 1.,
        'specular_k': 50,

        'depth_max': 5,  # Maximum number of light reflections.
        'col': np.zeros(3),  # Current color.

        'O': np.array([0., 0.35, -1.]),  # Camera.
        'Q': np.array([0., 0., 0.]),  # Camera pointing to.
    }

    return scene_params


def save_scene(scene, scene_location):
    """
    # TODO: Add documentation

    Parameters
    ----------
    scene : dict
    scene_location : str
    """
    with open(scene_location, 'wb') as f:
        pickle.dump(scene, f, pickle.HIGHEST_PROTOCOL)


def gather_image_paths(img_dir, match_str=r'img_(\d)_of_(\d).png'):
    """Gathers image paths into a list.
    
    # TODO: Add documentation

    Parameters
    ----------

    Returns
    -------
    """
    img_paths = sorted(
        os.path.join(img_dir, p) for p in os.listdir(img_dir)
        if re.search(match_str, p) is not None
    )
    return img_paths


def workers_finished(img_dir, match_str=r'img_(\d)_of_(\d).png'):
    """
    # TODO: Add documentation

    Parameters
    ----------

    Returns
    -------
    """
    img_paths = gather_image_paths(img_dir, match_str)

    if not img_paths:
        return False

    num_workers = int(re.search(match_str, img_paths[-1]).group(2))

    if len(img_paths) < (num_workers+1):
        return False

    return True


def combine_img_pieces(img_dir, width, match_str=r'img_(\d)_of_(\d).png',
                       outfile='final_image.png'):
    """
    # TODO: Add documentation

    TODO
    ----
    This relies on the fact that the images are named img_\d_of_\d.png.
    Make it more robust.
    """
    img_paths = gather_image_paths(img_dir, match_str)
    if not img_paths:
        raise ValueError("Format of img paths must have been changed ...")

    num_workers = int(re.search(match_str, img_paths[0]).group(2))
    assert (num_workers+1) == len(img_paths)

    interval = width // num_workers
    np_imgs = []
    for i, p in enumerate(img_paths):
        np_img = np.asarray(Image.open(p))
        np_img = np_img[:, i*interval:(i+1)*interval, :]
        np_imgs.append(np_img)

    final_np_image = np.concatenate(np_imgs, axis=1)
    final_png = Image.fromarray(final_np_image)
    final_png.save(os.path.join(img_dir, outfile))


def main(width, height, scene_location):
    """
    # TODO: Add documentation
    """
    scene = create_scene()
    save_scene(scene, scene_location)

    img_dir = os.path.dirname(scene_location)
    while not workers_finished(img_dir):
        time.sleep(2)

    combine_img_pieces(img_dir, width)



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Tracing controller.')
    parser.add_argument('--width', type=int, default=1200)
    parser.add_argument('--height', type=int, default=900)
    parser.add_argument('-s', '--scene_location', default='/data/state.pickle')
    args = parser.parse_args()

    main(args.width, args.height, args.scene_location)
