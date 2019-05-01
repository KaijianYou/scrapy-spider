# -*- coding: utf-8 -*-

import re
from datetime import datetime
from urllib import parse

import scrapy
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader

from scrapy_spider.items import LagouJobItem
from utils.tool import get_md5
from utils.selenium_login import get_lagou_cookie


class LagouSpider(scrapy.Spider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=']

    cookies = '_ga=GA1.2.1098909345.1542555087; user_trace_token=20181118233127-03af75b1-eb47-11e8-8956-5254005c3644; LGUID=20181118233127-03af79c9-eb47-11e8-8956-5254005c3644; fromsite=www.v2ex.com; index_location_city=%E5%8C%97%E4%BA%AC; bad_id551129f0-7fc2-11e6-bcdb-855ca3cec030=6f395351-34df-11e9-882d-51147bba196d; WEBTJ-ID=04072019%2C001055-169f36ac764f28-0ddc0fa8c07bd-366e7e04-2073600-169f36ac765960; JSESSIONID=ABAAABAABEEAAJAEE80C34D891D3D9C01DD2AAF38226A22; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1554567055,1554657212,1554821519,1555584104; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=3; _gid=GA1.2.2053290491.1556112016; X_MIDDLE_TOKEN=6eb392562ca87a667d1ebf1eb0b954d9; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%227984018%22%2C%22%24device_id%22%3A%221672772bdffa5a-00e5d641fd5b45-35677407-2073600-1672772be0061c%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_utm_source%22%3A%22m_cf_cpt_baidu_pc%22%2C%22%24os%22%3A%22MacOS%22%2C%22%24browser%22%3A%22Chrome%22%2C%22%24browser_version%22%3A%2272.0.3626.119%22%2C%22easy_company_id%22%3A%2277928%22%2C%22lagou_company_id%22%3A%2287747%22%7D%2C%22first_id%22%3A%221672772bdffa5a-00e5d641fd5b45-35677407-2073600-1672772be0061c%22%7D; TG-TRACK-CODE=index_hotsearch; LGSID=20190426181700-6e1547b9-680c-11e9-9d19-5254005c3644; PRE_UTM=; PRE_HOST=; PRE_SITE=https%3A%2F%2Fwww.lagou.com%2Fgongsi%2F71380.html; PRE_LAND=https%3A%2F%2Fpassport.lagou.com%2Flogin%2Flogin.html%3Fsignature%3DAD43E181926C1B912A21D714747FBD78%26service%3Dhttps%25253A%25252F%25252Fwww.lagou.com%25252Fgongsi%25252Fj369432.html%25253FschoolJob%25253Dtrue%26action%3Dlogin%26serviceId%3Dlagou%26ts%3D1556273820465; LG_LOGIN_USER_ID=8791b910a118d663ce3b9c48064b67f7266b17a3dabbc727; _putrc=DC4CE687C81B38F1; login=true; unick=%E6%B8%B8%E5%BC%80%E5%BB%BA; gate_login_token=5113434b9193434cf698b436b3d986ba6c51217a3a63472d; SEARCH_ID=b0d939a08ada496eaeeacbc94cbaa8eb; _gat=1; X_HTTP_TOKEN=c61fa40515ed620b5764726551ec13fa577717bf7a; LGRID=20190426183115-6b991b89-680e-11e9-b851-525400f775ce; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1556274676'
    custom_settings = {
        'COOKIES_ENABLED': False,
        'DOWNLOAD_DELAY': 1,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': cookies,
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
        },
        'RANDOM_DELAY': 30,
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_spider.middlewares.RandomDelayMiddleware": 999,
        }
    }

    # rules = (
    #     Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    #     Rule(LinkExtractor(allow=r'zhaopin/.*'), follow=True),
    #     Rule(LinkExtractor(allow=r'gongsi/j\d+.html'), follow=True),
    # )

    def start_requests(self):
        cookie_dict = get_lagou_cookie()
        for url in self.start_urls:
            yield Request(url=url, dont_filter=True, cookies=cookie_dict)

    def parse(self, response):
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda u: u.startswith('https'), all_urls)
        for url in all_urls:
            re_match = re.match('(.*lagou.com/jobs/(\d+)).html', url)
            if re_match:
                request_url = re_match.group(1)
                yield Request(request_url, callback=self.parse_job)
            else:
                yield Request(url, callback=self.parse)

    def parse_job(self, response):
        re_match = re.match('(.*lagou.com/jobs/(\d+)).html', response.url)
        if not re_match:
            yield None
        item_loader = ItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_value('page_url', response.url)
        item_loader.add_value('page_url_object_id', get_md5(response.url.encode('utf-8')))
        item_loader.add_css('title', '.job-name::attr(title)')
        item_loader.add_css('salary', '.job_request .salary::text')
        item_loader.add_xpath('city', '//*[@class="job_request"]/p/span[2]/text()')
        item_loader.add_xpath('years_of_working', '//*[@class="job_request"]/p/span[3]/text()')
        item_loader.add_xpath('edu_requirement', '//*[@class="job_request"]/p/span[4]/text()')
        item_loader.add_xpath('type', '//*[@class="job_request"]/p/span[5]/text()')
        item_loader.add_css('publish_time', '.publish_time::text')
        item_loader.add_css('tags', '.position-label li::text')
        item_loader.add_css('advantage', '.job-advantage p::text')
        item_loader.add_css('desc', '.job_bt div')
        item_loader.add_css('work_addr', '.work_addr')
        item_loader.add_css('company_url', '#job_company dt a::attr(href)')
        item_loader.add_css('company_name', '#job_company dt a img::attr(alt)')
        item_loader.add_value('crawl_time', datetime.utcnow())
        item = item_loader.load_item()
        yield item

