#!/bin/bash

cd /home/ubuntu/ocscrap
PATH=$PATH:/usr/local/bin
export PATH
scrapy crawl oc
scp -r /home/ubuntu/images/* devel@5.175.146.193:/var/www/cla/images && rm -r /home/ubuntu/images/* && rm -r /home/ubuntu/scrap_data/full/*

