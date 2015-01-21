# -*- coding: utf-8 -*-

# Scrapy settings for ocscrap project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'ocscrap'

SPIDER_MODULES = ['ocscrap.spiders']
NEWSPIDER_MODULE = 'ocscrap.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Googlebot/2.1' #'ocscrap (+http://www.yourdomain.com)'

#EXPORT http_proxy = "127.0.0.1:8000"
DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 543,
}

CATEGORY_DEEP = 5

ITEM_PIPELINES = {'scrapy.contrib.pipeline.images.ImagesPipeline': 1,
                  'ocscrap.pipelines.SQLStorePipeline': 800,
                  'ocscrap.pipelines.OcscrapPipeline': 900
                  }

IMAGES_STORE = '/home/ubuntu/scrap_data'
# 90 days of delay for image expiration
IMAGES_EXPIRES = 90
#IMAGES_THUMBS = {
#    'med': (200, 200),
#}

# DOWNLOAD_DELAY = 0.25   # 250 ms of delay

#OpenClassifeds dir
IMG_OCL_DIR = "/home/ubuntu/images/"

# Dir that contains app data (image logo, category files)
APP_DATA_DIR = "/home/ubuntu/ocscrap/"

