#!/usr/bin/python
# encoding: utf-8
import sys
import os
import urllib
from workflow import Workflow

sys.path.append(os.path.join(os.path.dirname(__file__), 'Scrapy'))
print sys.path

log = None


import scrapy

class TransitSpider(scrapy.Spider):
    YAHOO_TRANSIT_SEARCH_URL = 'http://transit.yahoo.co.jp/search/result?flatlon=&from=%s&tlatlon=&to=%s'

    def __init__(self, src, dst):
        url = self.YAHOO_TRANSIT_SEARCH_URL % (urllib.urlencode(src), urllib.urlencode(dst))
        self.url = url

    def start_requests(self):
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        for href in response.css('.question-summary h3 a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_question)

    def parse_question(self, response):
        yield {
            'title': response.css('h1 a::text').extract()[0],
            'votes': response.css('.question .vote-count-post::text').extract()[0],
            'body': response.css('.question .post-text').extract()[0],
            'tags': response.css('.question .post-tag::text').extract(),
            'link': response.url,
        }

class YahooTransitAlfredWorkflow(object):
    def __init__(self):
        self.wf = Workflow()

    def run(self):
        log = self.wf.logger
        sys.exit(self.wf.run(self.main))

    def main(self, wf):
        args = wf.args

        queries = args[0].split()

        if len(queries) > 1:
            src, dst = queries[0:2]
            wf.add_item(u'Item title', src)
            wf.add_item(u'Item title', dst)

        wf.send_feedback()

    def _fetch_transit_information(self, src, dst):
        spider = TransitSpider(src, dst)


if __name__ == '__main__':
    wf = YahooTransitAlfredWorkflow()
    wf.run()
