# -*- coding: utf-8 -*-
"""
Created on Sun Jul 27 20:02:36 2014

@author: raul
"""

import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

from ocscrap.items import OcItem
import ocscrap.pipelines
from ocscrap.pipelines import cache_urls, is_in_cache
from scrapy.contrib.loader import ItemLoader
from ocscrap.settings import CATEGORY_DEEP, APP_DATA_DIR
from datetime import datetime, date, timedelta
from scrapy import log

BASE_DOMAIN = "http://www.lapulga.com.do/"


class OcSpider(CrawlSpider):
    name = "oc"
    allowed_domains = ["lapulga.com.do"]
    start_urls = ["http://www.lapulga.com.do"]    
    rules = (
        # Extract links matching ’.hml’ and parse them with the spider’s method parse_item
        Rule(LinkExtractor(allow=('\.html',) ,restrict_xpaths=("//table[contains(@class, 'listaslnk')]//tbody//tr//td//*[@href]",)), callback='parse_item'),
    )

    def start_requests(self):
        cat_file = file(APP_DATA_DIR+"Allcategorys.txt",'r')
        lines = [ln[:-1] for ln in cat_file.readlines()]
        cat_file.close()
        print "Categories to scrap: %s " % str(len(lines))
        for url in lines:
            if len(url) > 15:
                yield self.make_requests_from_url(url)
                for i in range(2,CATEGORY_DEEP+1):
                    yield self.make_requests_from_url(url+"/"+str(i))

    def parse_item(self, response):
        print "Item detected:"
        if is_in_cache(response.url):
            print "Item in cache"
            log.msg("Jumping a already processed URL: " + str(response.url))
            return
        print "Item new (not in cache)"
        item = OcItem(url=response.url)
        item['title'] = "".join(response.css('h1.titart.mod2::text').extract())
        item['price'] = "".join(response.css('.preciod::text').extract())
        # item['content'] = "<br>".join(response.css("#contenidodesc").extract()).replace("lapulga","")
        item['content'] = "<br>".join(response.css(".descl").extract()).replace("lapulga","")
        # item['content'] = item['content'] + "<br>".join(response.xpath("//div[contains(@id, 'descp')]").extract()).replace("lapulga","")
        try:
            item['pub_date'] = "".join(response.xpath("//ul[contains(@class, 'dap')]//li[contains(.,'Publicado')]/text()").extract()).replace("Publicado.:","")
            item['pub_date'] = item['pub_date'].replace("pm","PM").lstrip().rstrip()
            date_object = datetime.strptime(item['pub_date'] ,'%d-%b-%Y %I:%M %p')
            item['pub_date'] = date_object.strftime('%Y-%m-%d %H:%M:%S')
        except:
            item['pub_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log.msg("Can not get pub date on item: " + str(item), level=log.ERROR)
        item['whatsapp'] = "".join(response.xpath("//ul[contains(@class, 'dap')]//li[contains(.,'WhatsApp.:')]/text()").extract()).replace("WhatsApp.:","")
        item['address'] = "".join(response.xpath("//span[contains(@id, 'dir')]/text()").extract()).replace(u"Dirección.:","")
        item['cel'] = "".join(response.xpath("//ul[contains(@class, 'dap')]//li[contains(.,'Celular.:')]/text()").extract()).replace("Celular.:","").replace("::before.:","")
        item['phone'] = "".join(response.xpath("//ul[contains(@class, 'dap')]//li[contains(.,'Telefono.:')]/text()").extract()).replace("Telefono.:","")
        cat = response.request.headers.get('Referer')
        if cat.count("/subcategoria/")>0:
            cat = cat.split("/subcategoria/")[1]
        item['category'] = cat
        item['image_urls'] = [BASE_DOMAIN+it for it in response.xpath('//a[@data-fancybox-group="gallery"]//img/@src').extract()]        
        return item
