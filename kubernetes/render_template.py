#!/usr/bin/env python

"""
render_template.py

Splits image into subsections and creates a Job for each subsection.
Also creates a Job for the controller, which just creates the scene,
monitors the workers for when they are finished, and then combines
the completed image subsections back together.

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

# create a yaml with a Job for each worker and a Job for the controller
# will divide image into quarters in this example (num_workers=4)
`./render_template --yaml_tmpl_path='job.yaml.jinja2' \
--img_width=800 \
--img_height=800 \
--num_workers=4 \
--scene_location='/data/state.pickle' \
--out_yaml_path='jobs.yaml'`
                   

Example 2
---------

TODO
----
> Need to figure out storage solution.

"""

import sys
import argparse
import subprocess
import re
import random

from jinja2 import Template



def main(yaml_tmpl_path, worker_name, controller_name, img_width,
         img_height, num_workers, scene_location, out_yaml_path):
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

    # create params to send to controller and workers
    unique_key = random.choice(range(1000000))
    tmpl_params = {
        'params': [
            {'part': '{}-{}'.format(i, num_workers-1), 'width': img_width,
             'height': img_height, 'scene_location': scene_location,
             'worker_name': worker_name, 'unique_key': unique_key}
            for i in range(num_workers)
        ],
        'contr_name': [
            {'contr_name': controller_name}, 
        ]

    }

    # fill in template parameters and output to file
    with open(out_yaml_path, 'w') as f:
        f.write(tmpl.render(**tmpl_params))

    cmd = 'kubectl create -f {}'.format(out_yaml_path)
    ret = subprocess.run(cmd.split(), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, encoding='utf-8')


    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Render Job templates.')
    parser.add_argument('--yaml_tmpl_path', default='job.yaml.jinja2',
                        help='Path to yaml Job template.')
    parser.add_argument('--worker_name', default='w1',
                        help='Name.')
    parser.add_argument('--controller_name', default='c1',
                        help='Name.')
    parser.add_argument('--img_width', type=int, default=1200,
                        help='Desired image width in pixels.')
    parser.add_argument('--img_height', type=int, default=900,
                        help='Desired image height in pixels.')
    parser.add_argument('--num_workers', type=int, default=4,
                        help='Number of tracing workers to create in parallel.')
    parser.add_argument('-s', '--scene_location', default='/data/state.pickle')
    parser.add_argument('--out_yaml_path', default='jobs.yaml',
                        help='Path to filled in yaml template.')
                        
    args = parser.parse_args()

    main(args.yaml_tmpl_path, args.worker_name, args.controller_name, args.img_width, args.img_height,
         args.num_workers, args.scene_location, args.out_yaml_path)
