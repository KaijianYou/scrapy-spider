# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import os
import re
from datetime import datetime
from typing import Tuple

import scrapy
from scrapy.loader.processors import MapCompose, Join, TakeFirst
from w3lib.html import remove_tags

from .settings import DATE_FORMAT, DATETIME_FORMAT


def date_from_string(value: str) -> datetime:
    try:
        time = datetime.strptime(value, DATE_FORMAT).date()
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

    def get_insert_sql(self):
        table = os.environ['JOBBOLE_TABLE']
        insert_sql = \
            f'INSERT INTO `{table}`(page_url, page_url_object_id, cover_url, title, create_time, tags, content, comment_num, upvote_num, collection_num)' \
            f'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        params = (
            self['page_url'],
            self['page_url_object_id'],
            self['cover_url'],
            self['title'],
            self['create_time'],
            self['tags'],
            self['content'],
            self['comment_num'],
            self['upvote_num'],
            self['collection_num']
        )
        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    page_url = scrapy.Field()
    question_id = scrapy.Field()
    topic = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comment_num = scrapy.Field()
    view_num = scrapy.Field()
    follower_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self) -> Tuple[str, Tuple]:
        table = os.environ['ZHIHU_QUESTION_TABLE']
        insert_sql = \
            f'INSERT INTO `{table}`(page_url, question_id, topic, title, content, answer_num, comment_num, view_num, follower_num, crawl_time)' \
            f'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ' \
            f'ON DUPLICATE KEY UPDATE content = VALUES(content), answer_num = VALUES(answer_num), view_num = VALUES(view_num), follower_num = VALUES(follower_num), comment_num = VALUES(comment_num), crawl_time = VALUES(crawl_time)'
        re_comment_match = re.match(r'(\d+) 条评论', self['comment_num'][0])
        if re_comment_match:
            comment_num = int(re_comment_match.group(1))
        else:
            comment_num = 0
        params = (
            self['page_url'][0],
            self['question_id'][0],
            self['topic'][0],
            self['title'][0],
            self.get('content', [''])[0],
            self['answer_num'][0].replace(',', ''),
            comment_num,
            int(self['view_num'][1]),
            self['follower_num'][0],
            self['crawl_time'][0].strftime(DATETIME_FORMAT)
        )
        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    page_url = scrapy.Field()
    question_id = scrapy.Field()
    answer_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    comment_num = scrapy.Field()
    upvote_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self) -> Tuple[str, Tuple]:
        table = os.environ['ZHIHU_ANSWER_TABLE']
        insert_sql = \
            f'INSERT INTO `{table}`(page_url, question_id, answer_id, author_id, content, comment_num, upvote_num, create_time, update_time, crawl_time)' \
            f'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ' \
            f'ON DUPLICATE KEY UPDATE content = VALUES(content), comment_num = VALUES(comment_num), upvote_num = VALUES(upvote_num), update_time = VALUES(update_time), crawl_time = VALUES(crawl_time)'
        params = (
            self['page_url'],
            int(self['question_id']),
            int(self['answer_id']),
            self['author_id'],
            self['content'],
            self['comment_num'],
            self['upvote_num'],
            datetime.fromtimestamp(self['create_time']).strftime(DATETIME_FORMAT),
            datetime.fromtimestamp(self['update_time']).strftime(DATETIME_FORMAT),
            self['crawl_time'].strftime(DATETIME_FORMAT)
        )
        return insert_sql, params


def remove_slash(s: str) -> str:
    return s.replace('/', '')


def trim_space(s: str) -> str:
    return s.strip()


def structured_work_address(addr: str) -> str:
    addrs = addr.split('\n')
    addrs = [addr.strip() for addr in addrs if addr.strip() != '查看地图']
    return ''.join(addrs)


class LagouJobItem(scrapy.Item):
    page_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    page_url_object_id = scrapy.Field(
        output_processor=TakeFirst()
    )
    title = scrapy.Field(
        output_processor=TakeFirst()
    )
    salary = scrapy.Field(
        output_processor=TakeFirst()
    )
    city = scrapy.Field(
        input_processor=MapCompose(remove_slash, trim_space),
        output_processor=TakeFirst()
    )
    years_of_working = scrapy.Field(
        input_processor=MapCompose(remove_slash, trim_space),
        output_processor=TakeFirst()
    )
    edu_requirement = scrapy.Field(
        input_processor=MapCompose(remove_slash, trim_space),
        output_processor=TakeFirst()
    )
    type = scrapy.Field(
        output_processor=TakeFirst()
    )
    publish_time = scrapy.Field(
        output_processor=TakeFirst()
    )
    tags = scrapy.Field(
        output_processor=Join(',')
    )
    advantage = scrapy.Field(
        output_processor=TakeFirst()
    )
    desc = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=TakeFirst()
    )
    work_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, structured_work_address, lambda s: s.replace(' ', '')),
        output_processor=TakeFirst()
    )
    company_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    company_name = scrapy.Field(
        output_processor=TakeFirst()
    )
    crawl_time = scrapy.Field(
        output_processor=TakeFirst()
    )

    def get_insert_sql(self) -> Tuple[str, Tuple]:
        table = os.environ['LAGOU_JOB_TABLE']
        insert_sql = \
            f'INSERT INTO `{table}`(page_url, page_url_object_id, title, salary, city, years_of_working, edu_requirement, `type`, publish_time, tags, advantage, `desc`, work_addr, company_url, company_name, crawl_time)' \
            f'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ' \
            f'ON DUPLICATE KEY UPDATE salary=VALUES(salary), publish_time=VALUES(publish_time), tags=VALUES(tags), advantage=VALUES(advantage), `desc`=VALUES(`desc`), crawl_time=VALUES(crawl_time)'
        params = (
            self['page_url'],
            self['page_url_object_id'],
            self['title'],
            self['salary'].strip(),
            self['city'],
            self['years_of_working'],
            self['edu_requirement'],
            self['type'],
            self['publish_time'],
            self['tags'],
            self['advantage'],
            self['desc'],
            self['work_addr'],
            self['company_url'],
            self['company_name'],
            self['crawl_time'].strftime(DATETIME_FORMAT)
        )
        return insert_sql, params
