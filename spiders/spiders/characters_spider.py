from pathlib import Path

import scrapy
from scrapy.selector import Selector



class QuotesSpider(scrapy.Spider):
    name = "characters"

    def start_requests(self):
        urls = ["https://wiki.biligame.com/ys/角色筛选"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        hxs = Selector(response)
        divs = hxs.xpath("//*[@id='CardSelectTr']")
        for div in divs:
            item = TestBotItem()
            item['var1'] = div.select('./td[2]/p/span[2]/text()').extract()
            item['var2'] = div.select('./td[3]/p/span[2]/text()').extract()
            item['var3'] = div.select('./td[4]/p/text()').extract()

            yield item