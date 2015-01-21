# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class OcItem(Item):
    content = Field()
    title = Field()
    price = Field()
    pub_date = Field()
    whatsapp = Field()
    address = Field()
    cel = Field()
    phone = Field()
    url = Field()
    lp_id = Field()
    category = Field()
    image_urls = Field()
    images = Field()

