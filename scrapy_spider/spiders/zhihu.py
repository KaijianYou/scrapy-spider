# -*- coding: utf-8 -*-

import re
import json
from datetime import datetime
from urllib import parse

import scrapy
from scrapy.loader import ItemLoader
from scrapy.http import Request

from utils.selenium_login import get_zhihu_cookie
from scrapy_spider.items import ZhihuQuestionItem, ZhihuAnswerItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    start_answer_url = 'https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B*%5D.is' \
                       '_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_' \
                       'action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2' \
                       'Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%' \
                       '2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%' \
                       '2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelat' \
                       'ionship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis' \
                       '_labeled%2Cis_recognized%2Cpaid_info%3Bdata%5B*%5D.mark_infos%5B*%5D.url%' \
                       '3Bdata%5B*%5D.author.follower_count%2Cbadge%5B*%5D.topics&offset={1}&limi' \
                       't={2}&sort_by=default&platform=desktop'
    headers = {
        'HOST': 'www.zhihu.com',
        'Referer': 'https://www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML,'
                      ' like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    }

    def start_requests(self):
        cookie_dict = get_zhihu_cookie()
        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]

    def parse(self, response):
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda u: u.startswith('https'), all_urls)
        for url in all_urls:
            re_match = re.match('(.*zhihu.com/question/(\d+))(/|$).*', url)
            if re_match:
                request_url = re_match.group(1)
                yield Request(request_url, headers=self.headers, callback=self.parse_question)
            else:
                pass
                # yield Request(url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        re_match = re.match('.*zhihu.com/question/(\d+)(/|$).*', response.url)
        if not re_match:
            yield None

        question_id = int(re_match.group(1))
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_value('page_url', response.url)
        item_loader.add_value('question_id', question_id)
        item_loader.add_css('topic', '.QuestionHeader-topics .Popover>div::text')
        item_loader.add_css('title', 'h1.QuestionHeader-title::text')
        item_loader.add_css('content', '.QuestionHeader-detail span::text')
        item_loader.add_css('answer_num', '.List-headerText span::text')
        item_loader.add_css('comment_num', '.QuestionHeader-Comment>button::text')
        item_loader.add_css('view_num', '.NumberBoard-itemValue::attr(title)')
        item_loader.add_css('follower_num', '.NumberBoard-itemValue::attr(title)')
        item_loader.add_value('crawl_time', datetime.utcnow())

        question_item = item_loader.load_item()
        yield question_item
        yield Request(
            self.start_answer_url.format(question_id, 0, 20),
            headers=self.headers,
            callback=self.parse_answer
        )

    def parse_answer(self, response):
        answer_json = json.loads(response.text)
        is_end = answer_json['paging']['is_end']
        next_url = answer_json['paging']['next']

        for answer in answer_json['data']:
            item = ZhihuAnswerItem()
            item['page_url'] = answer['url']
            item['answer_id'] = answer['id']
            item['question_id'] = answer['question']['id']
            item['author_id'] = answer.get('author_id', None)
            item['content'] = answer.get('content', '')
            item['upvote_num'] = answer['voteup_count']
            item['comment_num'] = answer['comment_count']
            item['create_time'] = answer['created_time']
            item['update_time'] = answer['updated_time']
            item['crawl_time'] = datetime.utcnow()
            yield item

        if not is_end:
            yield Request(next_url, headers=self.headers, callback=self.parse_answer)
