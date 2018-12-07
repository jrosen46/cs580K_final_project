#!/bin/bash


for i in 1 2 3 4;
do
    python render_template.py --scene_name="/data/state${i}.pickle" \
        --worker_name="w${i}" --controller_name="c${i}" --num_workers=8
done
