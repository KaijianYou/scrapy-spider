# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import re
from datetime import datetime

import scrapy
from scrapy.loader.processors import MapCompose, Join, TakeFirst


def date_from_string(value: str) -> datetime:
    try:
        time = datetime.strptime(value, '%Y-%m-%d').date()
    except Exception:
        time = datetime.utcnow()
    return time


def extract_nums(value: str) -> int:
    matcher = re.match(r'.?(\d+).*', value)
    return int(matcher.group(1)) if matcher else 0


class JobboleArticleItem(scrapy.Item):
    page_url = scrapy.Field()
    page_url_object_id = scrapy.Field()
    cover_url = scrapy.Field()
    cover_path = scrapy.Field()
    title = scrapy.Field(
        output_processor=TakeFirst()
    )
    create_time = scrapy.Field(
        input_processor=MapCompose(date_from_string),
        output_processor=TakeFirst()
    )
    upvote_num = scrapy.Field(
        input_processor=MapCompose(extract_nums),
        output_processor=TakeFirst()
    )
    collection_num = scrapy.Field(
        input_processor=MapCompose(extract_nums),
        output_processor=TakeFirst()
    )
    comment_num = scrapy.Field(
        input_processor=MapCompose(extract_nums),
        output_processor=TakeFirst()
    )
    content = scrapy.Field(
        output_processor=TakeFirst()
    )
    tags = scrapy.Field(
        input_processor=MapCompose(lambda value: '' if '评论' in value else value),
        output_processor=Join(',')
    )
