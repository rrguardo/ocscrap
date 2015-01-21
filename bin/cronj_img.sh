#!/bin/bash
FILE=""
DIR="/home/ubuntu/images"
# init
# look for empty dir 
if [ "$(ls -A $DIR)" ]; then
     echo "Take action $DIR is not Empty"
     scp -r /home/ubuntu/images/* devel@5.175.146.193:/var/www/cla/images && rm -r /home/ubuntu/images/* && rm -r /home/ubuntu/scrap_data/full/*
else
    echo "$DIR is Empty"
fi

