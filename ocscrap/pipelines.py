# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import datetime
import MySQLdb
import MySQLdb.cursors
from scrapy import log
import re
from ocscrap.settings import IMAGES_STORE, IMG_OCL_DIR, APP_DATA_DIR
import hashlib
import os
import shutil
import PIL
from PIL import Image, ImageDraw
from StringIO import StringIO


SQL_DB = {
    "host": "5.175.146.193",
    "db": "openclassifieds",
    "user": "root",
    "passw": "HvBs73UtwPn51",
}

db_master = MySQLdb.connect(host=SQL_DB['host'],user=SQL_DB['user'],
                            passwd=SQL_DB['passw'], db=SQL_DB['db'], 
                            charset='utf8', use_unicode=True)

# SQL update for oc2 db
# ALTER TABLE `oc2_ads` ADD `url` TEXT NOT NULL ;

################################################################

locations = {}

def load_locations():
    if len(locations)==0:
        c_master = db_master.cursor()
        c_master.execute("""SELECT id_location, name FROM oc2_locations""")
        while True:
            data = c_master.fetchone()
            if data is None:
                break
            locations[str(data[0])] = data[1]
        c_master.close()

load_locations()

def get_location(address):
    if address is None or address=="":
        return 0
    result = ""
    loc_id = 0
    for k in locations:
        if address.count(locations[k])>0 and len(result)< len(locations[k]):
            result = locations[k]
            loc_id = k
    return loc_id

################################################################
categories = {}

def load_categories():
    if len(categories)==0:
        c_master = db_master.cursor()
        c_master.execute("""SELECT id_category, id_category_parent, name FROM oc2_categories""")
        while True:
            data = c_master.fetchone()
            if data is None:
                break
            categories[data[0]] = [data[1]] + data[2].split()
        c_master.close()
        for k in categories:
            if categories[k][0] not in (0,1):
                categories[k] = categories[k] + categories[categories[k][0]][1:]

load_categories()

def get_category(cat):
    max_k = 1
    max_cnt = 0
    for k in categories:
        cnt = 0
        for tag in categories[k][1:]:
            tc = cat.lower().count(tag.lower())
            if tc > 0 and len(tag)>2:
                cnt = cnt + tc
        if cnt > max_cnt:
            max_cnt = cnt
            max_k = k
    return max_k

################################################################


def get_seo_title(data):
    try:
        id_ = ""
        result = ""
        if data['url'] is not None:
            hash_object = hashlib.sha1(data['url'])
            hex_dig = hash_object.hexdigest()
            id_ = hex_dig
        result = id_ + u"-" + re.sub('[^0-9a-zA-Z]+', '-', data['title'])
        return result[:120]
    except Exception as e:
        log.msg(str(e), level=log.ERROR)
        return None


def get_content(data):
    try:
        result = ""
        if data['content'] is not None and data['content'].strip(' \t\n\r')!="":
            result = result + data['content'] + u"\n"
        if data['whatsapp'] is not None and data['whatsapp'].strip(' \t\n\r')!="":
            result = result + u"<br> Whatsapp: " + data['whatsapp'] + u"\n"
        if data['cel'] is not None and data['cel'].strip(' \t\n\r')!="":
            result = result + u"<br> Celular: " + data['cel'] + u"\n"
        if data['phone'] is not None and data['phone'].strip(' \t\n\r')!="":
            result = result + u"<br> Phone: " + data['phone'] + u"\n"
        return result
    except Exception as e:
        log.msg(str(e)+" error in get_content pipeline", level=log.ERROR)
        return None


def has_images(data):
    if data['image_urls']:
        return 1
    else:
        return 0


def get_price(data):
    try:
        result = 0
        if data['price'] is None:
            return 0
        price = data['price']
        if price.count("RD") > 0:
            result = float(price[3:].replace(",",""))
        else:
            #USD x ~44
            result = float(price[4:].replace(",",""))
            result = result*44
        return result
    except Exception as e:
        log.msg(str(e), level=log.ERROR)
        return 0


def getmonth(datet):
    if datet.month < 10:
        return "0"+str(datet.month)
    else:
        return str(datet.month)


def getday(datet):
    if datet.day < 10:
        return "0"+str(datet.day)
    else:
        return str(datet.day)


def thumbnail_image(source, dest):
    try:
        im = Image.open(source)
        im.thumbnail((200,200), Image.ANTIALIAS)
        im.save(dest, "JPEG")
    except Exception as e:
        log.msg(str(e), level=log.ERROR)


logo = Image.open(APP_DATA_DIR+"compVaina.jpg")


def fix_image_logo(src_img):
    global logo
    try:
        fl_img = file(src_img,'r')
        str_img = fl_img.read()
        fl_img.close()
        im = StringIO(str_img)
        im = Image.open(im)
        ancho, alto = im.size
        im.paste(logo,(ancho-110,alto-40))
        if im is not None:
            im.save(src_img, "JPEG")
    except Exception as e:
        log.msg(str(e), level=log.ERROR)
        return None


def move_images(item, db_id):
    """ Move images from final location."""
    try:
        pub_date =  datetime.datetime.strptime(item['pub_date'], '%Y-%m-%d %H:%M:%S')
        log.msg("Moving Images pub_date: " + str(pub_date), level=log.DEBUG) 
        if not os.path.isdir(IMG_OCL_DIR+str(pub_date.year)):
            os.mkdir(IMG_OCL_DIR+str(pub_date.year))
        if not os.path.isdir(IMG_OCL_DIR+str(pub_date.year)+"/"+getmonth(pub_date)):
            os.mkdir(IMG_OCL_DIR+str(pub_date.year)+"/"+getmonth(pub_date))
        if not os.path.isdir(IMG_OCL_DIR+str(pub_date.year)+"/"+getmonth(pub_date)+"/"+getday(pub_date)):
            os.mkdir(IMG_OCL_DIR+str(pub_date.year)+"/"+getmonth(pub_date)+"/"+getday(pub_date))
        if not os.path.isdir(IMG_OCL_DIR+str(pub_date.year)+"/"+getmonth(pub_date)+"/"+getday(pub_date)+"/"+str(db_id)):
            os.mkdir(IMG_OCL_DIR+str(pub_date.year)+"/"+getmonth(pub_date)+"/"+getday(pub_date)+"/"+str(db_id))
        dest_dir = IMG_OCL_DIR + str(pub_date.year) + "/" + getmonth(pub_date) + "/" + getday(pub_date) + "/"+str(db_id) + "/"

        onlyfiles = []
        for ur  in item['image_urls']:
            hash_object = hashlib.sha1(ur)
            hex_dig = hash_object.hexdigest()
            onlyfiles.append(hex_dig+".jpg")

        cnt = 1
        for fl in onlyfiles:
            log.msg("ORIGEN: " + IMAGES_STORE+"/full/"+fl, level=log.DEBUG)
            shutil.copyfile(IMAGES_STORE+"/full/"+fl, dest_dir+"img_"+str(cnt)+".jpg")
            fix_image_logo(dest_dir+"img_"+str(cnt)+".jpg")
            thumbnail_image(dest_dir+"img_"+str(cnt)+".jpg", dest_dir+"thumb_img_"+str(cnt)+".jpg")
            cnt = cnt + 1
    except Exception as e:
        log.msg(str(e), level=log.ERROR)

###################################
cache_urls = []


def init_url_cache():
    """ Load info about urls already loaded in array cache_urls """
    if not cache_urls:
        c_master = db_master.cursor()
        c_master.execute("""SELECT distinct url as url FROM oc2_ads""")
        while True:
            data = c_master.fetchone()
            if data is None:
                break
            cache_urls.append(data[0])
        c_master.close()

init_url_cache()

def is_in_cache(url):
    """ Determine if the url is in cache"""
    init_url_cache()
    if url in cache_urls:
        return True
    return False

###################################

class OcscrapPipeline(object):
    def process_item(self, item, spider):
        print "Item Pipeline call" + str(item)
        return item


class SQLStorePipeline(object):
    """ MySQL pipeline."""

    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb', host=SQL_DB['host'], db=SQL_DB['db'],
                user=SQL_DB['user'], passwd=SQL_DB['passw'], cursorclass=MySQLdb.cursors.DictCursor,
                charset='utf8', use_unicode=True)

    def process_item(self, item, spider):
        # run db query in thread pool
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self.handle_error)
        return item

    def _conditional_insert(self, tx, item):
        # create record if doesn't exist.
        # all this block run on it's own thread
        # tx.execute("select * from oc2_ads where url = %s", (item['url'], ))
        # result = tx.fetchone()
        if is_in_cache(item['url']):
            log.msg("Item already stored in db: %s" % item, level=log.DEBUG)
        else:
            cache_urls.append(item['url'])
            tx.execute("""INSERT IGNORE INTO oc2_ads (id_user, id_category, id_location, description, title, seotitle,
                address, price, phone, created, published, status, has_images, url, whatsapp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                ( 1, get_category(item['category']), get_location(item['address']), get_content(item), item['title'],
                 get_seo_title(item),item['address'],get_price(item),item['phone'],
                 item['pub_date'], item['pub_date'], 50, has_images(item), item['url'], item['whatsapp'] )
            )
            #tx.commit()
            newID = tx.lastrowid
            if has_images(item):
                move_images(item, newID)
            log.msg("Item stored in db: %s" % item, level=log.DEBUG)

    def handle_error(self, e):
        log.msg(str(e), level=log.ERROR)
