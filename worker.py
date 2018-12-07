#!/usr/bin/env python

"""
worker.py

"""
import argparse
import pickle
import time
import os

import numpy as np
import matplotlib.pyplot as plt



def normalize(x):
    """
    """
    x /= np.linalg.norm(x)
    return x


def intersect_plane(O, D, P, N):
    """
    Return the distance from O to the intersection of the ray (O, D) with the
    plane (P, N), or +inf if there is no intersection.  O and P are 3D points,
    D and N (normal) are normalized vectors.
    """
    denom = np.dot(D, N)
    if np.abs(denom) < 1e-6:
        return np.inf
    d = np.dot(P - O, N) / denom
    if d < 0:
        return np.inf
    return d


def intersect_sphere(O, D, S, R):
    """
    Return the distance from O to the intersection of the ray (O, D) with the 
    sphere (S, R), or +inf if there is no intersection.
    O and S are 3D points, D (direction) is a normalized vector, R is a scalar.
    """
    a = np.dot(D, D)
    OS = O - S
    b = 2 * np.dot(D, OS)
    c = np.dot(OS, OS) - R * R
    disc = b * b - 4 * a * c
    if disc > 0:
        distSqrt = np.sqrt(disc)
        q = (-b - distSqrt) / 2.0 if b < 0 else (-b + distSqrt) / 2.0
        t0 = q / a
        t1 = c / q
        t0, t1 = min(t0, t1), max(t0, t1)
        if t1 >= 0:
            return t1 if t0 < 0 else t0
    return np.inf


def intersect(O, D, obj):
    """
    """
    if obj['type'] == 'plane':
        return intersect_plane(O, D, obj['position'], obj['normal'])
    elif obj['type'] == 'sphere':
        return intersect_sphere(O, D, obj['position'], obj['radius'])


def get_normal(obj, M):
    """
    Find normal.
    """
    if obj['type'] == 'sphere':
        N = normalize(M - obj['position'])
    elif obj['type'] == 'plane':
        N = obj['normal']
    return N
    

def get_color(obj, M):
    """
    """
    # sphere
    if 'color' in obj:
        return obj['color']

    # plane
    if int(M[0] * 2) % 2 == int(M[2] * 2) % 2:
        return obj['color_plane0']
    return obj['color_plane1']


def trace_ray(rayO, rayD, scene_objects, L, O, ambient, diffuse_c,
              specular_c, specular_k, color_light):
    """
    """
    # Find first point of intersection with the scene.
    t = np.inf
    for i, obj in enumerate(scene_objects):
        t_obj = intersect(rayO, rayD, obj)
        if t_obj < t:
            t, obj_idx = t_obj, i
    # Return None if the ray does not intersect any object.
    if t == np.inf:
        return
    # Find the object.
    obj = scene_objects[obj_idx]
    # Find the point of intersection on the object.
    M = rayO + rayD * t
    # Find properties of the object.
    N = get_normal(obj, M)
    color = get_color(obj, M)
    toL = normalize(L - M)
    toO = normalize(O - M)
    # Shadow: find if the point is shadowed or not.
    l = [intersect(M + N * .0001, toL, obj_sh) 
            for k, obj_sh in enumerate(scene_objects) if k != obj_idx]
    if l and min(l) < np.inf:
        return
    # Start computing the color.
    col_ray = ambient
    # Lambert shading (diffuse).
    col_ray += obj.get('diffuse_c', diffuse_c) * max(np.dot(N, toL), 0) * color
    # Blinn-Phong shading (specular).
    col_ray += obj.get('specular_c', specular_c) * max(np.dot(N, normalize(toL + toO)), 0) ** specular_k * color_light
    return obj, M, N, col_ray


def load_scene(scene_location):
    """
    Parameters
    ----------
    scene_location : str
    """
    while not os.path.exists(scene_location):
        time.sleep(1)

    with open(scene_location, 'rb') as f:
        state = pickle.load(f)

    return state


def main(part, unique_key, width, height, scene_location):
    """
    """
    scene_dict = load_scene(scene_location=scene_location)
    trace_ray_kwargs = {
        k: v for k, v in scene_dict.items()
        if k in {'scene_objects', 'L', 'O', 'ambient', 'diffuse_c',
                 'specular_c', 'specular_k', 'color_light'}
    }
    # set rest of scene_dict as local vars for readability
    depth_max = scene_dict.pop('depth_max') # max num of light reflections
    col = np.zeros(3)  # Current color.
    O = np.array([0., 0.35, -1.])  # Camera.
    Q = np.array([0., 0., 0.])  # Camera pointing to.

    # Screen coordinates: x0, y0, x1, y1.
    r = width / height
    S = (-1., -1. / r + .25, 1., 1. / r + .25)

    img_part = int(part.split('-')[0])
    num_workers = int(part.split('-')[1]) + 1
    w_add = 2. / num_workers

    # Loop through all pixels.
    # TODO: we actually don't need the full image here ... will be more
    # efficient if we don't have it
    img = np.zeros((height, width, 3))
    for i, x in enumerate(np.linspace(S[0]+img_part*w_add,
                                      S[0]+(img_part+1)*w_add,
                                      width // num_workers),
                          start=img_part*(width // num_workers)):
        if i % 10 == 0:
            print(f"{i/float(width)*100}%")
        for j, y in enumerate(np.linspace(S[1], S[3], height)):
            col[:] = 0
            Q[:2] = (x, y)
            D = normalize(Q - O)
            depth = 0
            rayO, rayD = O, D
            reflection = 1.
            # Loop through initial and secondary rays.
            while depth < depth_max:
                traced = trace_ray(rayO, rayD, **trace_ray_kwargs)
                if not traced:
                    break
                obj, M, N, col_ray = traced
                # Reflection: create a new ray.
                rayO, rayD = M + N * .0001, normalize(rayD - 2 * np.dot(rayD, N) * N)
                depth += 1
                col += reflection * col_ray
                reflection *= obj.get('reflection', 1.)
            img[height - j - 1, i, :] = np.clip(col, 0, 1)

    # TODO: going to end up saving this to server
    img_path = os.path.join(
        os.path.dirname(scene_location),
        f'{unique_key}_img_{img_part+1}_of_{num_workers}.png')
    plt.imsave(img_path, img)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Tracing worker.')
    parser.add_argument('part', type=str,
                        help="part of image: format='{n}-{total}'")
    parser.add_argument('unique_key', type=int)
    parser.add_argument('--width', type=int, default=1200)
    parser.add_argument('--height', type=int, default=900)
    parser.add_argument('-s', '--scene_location', default='/data/state.pickle')
    args = parser.parse_args()

    main(args.part, args.unique_key, args.width, args.height,
         args.scene_location)
