#!/usr/bin/bash

# =
# a Bash script to automatically detect files being Created.
# the simple initial idea is to iteratively checking the directories. compared with the previous one
# if the event being created, we proceed the following commands.
# = 

WATCH_DIR="/home/wt301/Desktop/manual"

fswatch -0 $WATCH_DIR | while read -d "" event   # read each event produced by events
do
    if [ $event=="created" ]
        # the event in fswatch being created, (I) transformed to
        filename=$(basename "$event")
        source activate SeismicTool
        python IManual_CSV.py --filename=$filename
        #

done

