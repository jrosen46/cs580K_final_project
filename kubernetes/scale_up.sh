#!/bin/bash


# first command line argument specifies number of images to render
# second command line argument specifies number of workers per image
# to run: ./scale_up 8 8

if [ -z "$1" ]
then
    END=4
else
    END=$1
fi


if [ -z "$2" ]
then
    NUM_WORKERS=8
else
    NUM_WORKERS=$2
fi

for i in $(seq 1 $END)
do
    python render_template.py --scene_location="/data/state.pickle" \
        --worker_name="w${i}" --controller_name="c${i}" --num_workers=$NUM_WORKERS
done
