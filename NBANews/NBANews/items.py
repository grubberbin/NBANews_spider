# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
import re
from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst


class NbanewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class NBAnewsItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def add_tags(value):
    return value + "NBA"


def date_convert(value):
    try:
        create_time = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M")
    except Exception as e:
        create_time = datetime.datetime.now()
    return create_time


def return_value(value):
    return value


def get_image_url(value):
    if value :
        #for str_url in value:
            url = re.match(r'<img src="(.+?)"', value)
            if url:
                yield urljoin('http://',url.group(1))


class NewsItem(scrapy.Item):
    '''

    '''
    title = scrapy.Field(
        input_processor=MapCompose(add_tags)
    )
    create_time = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )

    url = scrapy.Field()
    comment_nums = scrapy.Field()
    content = scrapy.Field()
    image_path = scrapy.Field(
        output_processor=MapCompose(get_image_url)
    )
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    url_object_id = scrapy.Field()
