# -*- coding: utf-8 -*-
import scrapy
import re

import datetime
from urllib.parse import urljoin
from NBANews.utils.common import get_md5
from NBANews.items import NewsItem, NBAnewsItemLoader
from scrapy_splash import SplashRequest
from scrapy.loader import ItemLoader


class NanewsSpider(scrapy.Spider):
    name = 'nbaNews'
    allowed_domains = ['sports.qq.com']
    start_urls = ['http://sports.qq.com/l/basket/nba/list20181018164449.htm']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 0.5})

    def parse(self, response):
        '''
        1.解析新闻列表中的所有url  并交给scrapy 解析每个页面的数据
        2.将下一页的url交给scrapy
        :param response:
        :return:
        '''
        post_nodes = response.xpath('//*[@id="listInfo"]/li')

        for post_node in post_nodes:
            news_url = post_node.xpath('./a/@href').extract_first()
            image_url = urljoin("http://", post_node.xpath('./a/img/@src').extract_first())
            # 获取每页列表中的新闻
            yield SplashRequest(news_url, self.parse_detail, args={'wait': 0.5}, meta={"front-image-url": image_url})

        '''
        #获取下一页的的url
        next_url = response.xpath('//*[@class="next"]/@href').extract_first()
        print("next_url :"+str(next_url))
        if next_url:
            yield SplashRequest(next_url, self.parse, args={'wait': 0.5})
        '''

    def parse_detail(self, response):
        '''
        解析页面中的详细数据
        :param response:
        :return:
        '''

        #newsItem = NewsItem()
        # title = response.xpath('//div[@class="hd"]/h1/text()').extract()[0]
        # create_time = response.xpath('//span[@class="a_time"]/text()').extract()[0]
        # comment_nums = response.xpath('//*[@id="cmtNum"]/text()').extract()[0]
        # content = response.xpath('//div[@class="Cnt-Main-Article-QQ"]//p[@class="text"]/text()').extract_first()
        #image_path = [urljoin('http://', re.match(r'<img src="(.+?)"', p).group(1)) for p in
        #             response.xpath('//*[@align="center"]/img[@src]').extract()]


        '''
        newsItem['title'] = title
        newsItem['create_time'] = create_time
        newsItem['url'] = response.url
        newsItem['url_object_id'] = get_md5(response.url)
        newsItem['front_image_url'] = [front_image_url]
        newsItem['comment_nums'] = comment_nums
        newsItem['image_path'] = image_path
        newsItem['content'] = content
        '''

        # Itemloader 加载item

        item_loader = NBAnewsItemLoader(item=NewsItem(), response=response)
        front_image_url = response.meta.get("front-image-url", "")
        item_loader.add_xpath('title', '//div[@class="hd"]/h1/text()')
        item_loader.add_value('create_time', '/span[@class="a_time"]/text()')
        item_loader.add_xpath('comment_nums', '//*[@id="cmtNum"]/text()')
        item_loader.add_xpath('image_path', '//*[@align="center"]/img[@src]')
        item_loader.add_xpath('content', '//div[@class="Cnt-Main-Article-QQ"]//p[@class="text"]/text()')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_value('front_image_url', [front_image_url])
        newsItem = item_loader.load_item()

        yield newsItem
