#!/usr/bin/env python

"""
controller.py

"""
import os
import argparse
import pickle
import re

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


# TODO: FIGURE OUT HOW TO INTEGRATE THIS!
def save_scene(scene, scene_location):
    """
    Parameters
    ----------
    scene : dict
    scene_location : str, choices={'minikube_hostPath',
                                   'gke_persistent_volumne'}
    """
    with open('state.pickle', 'wb') as f:
        pickle.dump(scene, f, pickle.HIGHEST_PROTOCOL)

    #scp -i ~/.minikube/machines/minikube/id_rsa -r /folder2copy docker@$(minikube ip):/home/docker 

    #if scene_location == 'minikube_hostPath':
    #    with open(os.path.join(self.log_dir, 'state.pickle'), 'wb') as f:
    #        pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
    #elif scene_location == 'gke_persistent_volume':
    #    pass
    #else:
    #    raise ValueError(f"`scene_location` parameter: '{scene_location}' "
    #                     f"not understood.")


def combine_img_pieces(img_dir, width):
    """

    TODO
    ----
    This relies on the fact that the images are named img_\d_of_\d.png.
    Make it more robust.
    """
    img_paths = sorted(os.path.join(img_dir, p) for p in os.listdir(img_dir))
    m = re.search(r'img_\d_of_(\d).png', imgs_paths[0])
    if m is not None:
        num_workers = int(m.group(1))
        assert num_workers == len(img_paths)
    else:
        raise ValueError("Format of img paths must have been changed ...")

    interval = width // num_workers
    np_imgs = []
    for i, p in enumerate(img_paths):
        np_img = np.asarray(Image.open(p))
        np_img = np_img[:, i*interval:(i+1)*interval, :]
        np_imgs.append(np_img)

    final_np_image = np.concatenate(np_imgs, axis=1)
    final_png = Image.fromarray(final_np_image)
    final_png.save(os.path.join(img_dir, 'combined_image.png'))


def main(width, height, scene_location):
    """
    """
    scene = create_scene()
    save_scene(scene, scene_location)

    # TODO: we need to break this up in the correct way
    # workers will be started here ...
    # combine images back together here ...



if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='Tracing worker.')
    parser.add_argument('--width', type=int, default=1200)
    parser.add_argument('--height', type=int, default=900)
    parser.add_argument('-s', '--scene_location', default='state.pickle')


    args = parser.parse_args()

    
    main(args.width, args.height, args.scene_location)
