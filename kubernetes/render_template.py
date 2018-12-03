#!/usr/bin/env python

"""
render_template.py

Splits image into subsections and creates a Job for each subsection.

At this point, using Job Template Expansion to create one Job object for each
'tracer' seems to be the simplest/fastest way to get a proof of concept
working.  There are definitely more sophisticated ways to do this (i.e. worker
queues, etc.), but we are trading functionality for simplicity. Our method is
intended to be used with the creation of one rendered image ... it does not
really have the ability to dynamically scale our application based on a
real-time, continuous stream of tasks.

If we have the time to create something more functional, we should pursue that. This
is the minimum viable option in case we don't have time for anything better.

Usage
-----
Run `./render_template -h` to see command line options.

Example 1
---------

# create a yaml with a Job for each worker ... will divide image into quarters
`./render_template --yaml_tmpl_path='job.yaml.jinja2' \
--img_width=800 \
--img_height=800 \
--num_workers=4 \
--out_yaml_path='jobs.yaml'`
                   
# use this create yaml to launch jobs on cluster
`kubectl create -f jobs.yaml`

Example 2
---------

TODO
----
> Need to figure out storage solution.
> Need to figure out how to piece the final image back together when we have
  all the completed subsections. This is going to be reliant on our storage
  solution.

"""

import sys
import argparse
import subprocess

from jinja2 import Template

from controller import Controller


def main(yaml_tmpl_path, img_width, img_height, num_workers,
         scene_location, out_yaml_path):
    """Renders jinja `Job` template by filling in parameters.

    Parameters
    ----------
    yaml_tmpl_path : str
        Path to yaml Job template.
    img_width : int
        Desired image width in pixels.
    img_height : int
        Desired image height in pixels.
    num_workers : int
        Number of ray tracing workers to create in parallel.
    scene_location : str
        #TODO: add documentation here ...
    out_yaml_path : str
        Path to filled in yaml template.
    """

    # create the template
    with open(yaml_tmpl_path, 'r') as f:
        yaml_tmpl_text = f.read()
    tmpl = Template(yaml_tmpl_text)

    # just the test for the example template
    #tmpl_params = {
    #    'params' : [
    #        {'name': 'jared', 'url': 'jared.com', },
    #        {'name': 'dan', 'url': 'dan.com', },
    #        {'name': 'aaron', 'url': 'aaron.com', },
    #    ],
    #}    

    # create scene from controller
    ctr = Controller(img_width, img_height, scene_location)
    scene = ctr.create_scene()
    ctr.save_scene(scene, scene_location)

    tmpl_params = {
        'params': [
            {'part': f'{i}-{num_workers-1}', 'width': img_width,
             'height': img_height, 'scene_location': scene_location}
            for i in range(num_workers)
        ]
    }

    # fill in template parameters and output to file
    with open(out_yaml_path, 'w') as f:
        f.write(tmpl.render(**tmpl_params))

    # TODO: can we launch kubectl command from here?
    cmd = f'kubectl create -f {out_yaml_path}'
    ret = subprocess.run(cmd.split(), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, encoding='utf-8')
    print(ret)
    print('reached here ...')
    

    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Render Job templates.')
    parser.add_argument('--yaml_tmpl_path', default='job.yaml.jinja2',
                        help='Path to yaml Job template.')
    parser.add_argument('--img_width', type=int, default=1200,
                        help='Desired image width in pixels.')
    parser.add_argument('--img_height', type=int, default=900,
                        help='Desired image height in pixels.')
    parser.add_argument('--num_workers', type=int, default=1,
                        help='Number of tracing workers to create in parallel.')
    parser.add_argument('-s', '--scene_location', default='state.pickle')
    parser.add_argument('--out_yaml_path', default='jobs.yaml',
                        help='Path to filled in yaml template.')
                        
    args = parser.parse_args()

    main(args.yaml_tmpl_path, args.img_width, args.img_height,
         args.num_workers, args.scene_location, args.out_yaml_path)
