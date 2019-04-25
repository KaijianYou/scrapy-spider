# -*- coding: utf-8 -*-

from urllib import parse

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
        next_url = response.css('a.next.page-numbers::attr(href)').extract_first('')
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        """解析页面详细内容"""
        cover_url = response.meta.get('cover_url', '')

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
