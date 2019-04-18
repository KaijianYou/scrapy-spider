# -*- coding: utf-8 -*-

import re
from urllib import parse
from datetime import datetime

import scrapy
from scrapy.http import Request

from scrapy_spider.items import JobboleArticleItem
from scrapy.loader import ItemLoader
from utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        # 获取文章列表页中的文章 URL，下载文章并解析
        article_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for article_node in article_nodes:
            cover_url = article_node.css('img::attr(src)').extract_first('')
            article_url = article_node.css('::attr(href)').extract_first('')
            yield Request(
                url=parse.urljoin(response.url, article_url),
                callback=self.parse_detail,
                meta={'cover_url': cover_url}
                # dont_filter=True
            )

        # 获取下一页的 URL 后再获取文章列表
        # next_url = response.css('a.next.page-numbers::attr(href)').extract_first('')
        # if next_url:
            # yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        """解析页面详细内容"""
        cover_url = response.meta.get('cover_url', '')
        title = response.css('.entry-header h1::text').extract_first('')
        create_time = response.css('p.entry-meta-hide-on-mobile::text') \
            .extract_first('').strip().replace(' ·', '')
        try:
            create_time = datetime.strptime(create_time, '%Y-%m-%d').date()
        except Exception:
            create_time = datetime.utcnow()
        upvote_num = response.css('span.vote-post-up h10::text').extract_first('')
        re_collection_num = re.match(
            r'.?(\d+).*',
            response.css('span.bookmark-btn::text').extract_first('')
        )
        collection_num = 0
        if re_collection_num:
            collection_num = re_collection_num.group(1)
        re_comment_num = re.match(
            r'.?(\d+).*',
            response.css('a[href="#article-comment"] span::text').extract_first('')
        )
        comment_num = 0
        if re_comment_num:
            comment_num = re_comment_num.group(1)
        content = response.css('div.entry').extract_first('')
        tag_list = response.css('p.entry-meta-hide-on-mobile a::text').extract()
        tag_list = [tag.strip() for tag in tag_list if not tag.strip().endswith('评论')]
        tags = ','.join(tag_list)

        article_item = JobboleArticleItem()
        article_item['page_url'] = response.url
        article_item['page_url_object_id'] = get_md5(response.url.encode('utf-8'))
        article_item['cover_url'] = [cover_url]
        article_item['title'] = title
        article_item['create_time'] = create_time
        article_item['upvote_num'] = upvote_num
        article_item['collection_num'] = collection_num
        article_item['comment_num'] = comment_num
        article_item['content'] = content
        article_item['tags'] = tags

        item_loader = ItemLoader(item=JobboleArticleItem(), response=response)
        item_loader.add_value('page_url', response.url)
        item_loader.add_value('page_url_object_id', get_md5(response.url.encode('utf-8')))
        item_loader.add_value('cover_url', [cover_url])
        item_loader.add_css('title', '.entry-header h1::text')
        item_loader.add_css('create_time', 'p.entry-meta-hide-on-mobile::text')
        item_loader.add_css('upvote_num', 'span.vote-post-up h10::text')
        item_loader.add_css('collection_num', 'span.bookmark-btn::text')
        item_loader.add_css('comment_num', 'a[href="#article-comment"] span::text')
        item_loader.add_css('content', 'div.entry')
        item_loader.add_css('tags', 'p.entry-meta-hide-on-mobile a::text')

        article_item = item_loader.load_item()
        yield article_item
