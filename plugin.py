#!/usr/bin/python
# encoding: utf-8
import sys
import os
import urllib
from workflow import Workflow
from workflow import web

sys.path.append(os.path.join(os.path.dirname(__file__), 'bs4'))

log = None

from bs4 import BeautifulSoup


class TransitInformation(object):
    def __init__(self, time, duration, transfer, fare, url):
        self.time = time
        self.duration = duration
        self.transfer = transfer
        self.fare = fare
        self.url = url

    @property
    def title(self):
        return u'%s %s' % (self.time, self.duration)

    @property
    def description(self):
        return u'%s %s' % (self.transfer, self.fare)


class YahooTransitAlfredWorkflow(object):
    YAHOO_TRANSIT_SEARCH_URL = 'http://transit.yahoo.co.jp/search/result?flatlon=&from=%s&tlatlon=&to=%s'
    ICON_URL = 'icon.png'

    def __init__(self):
        self.wf = Workflow()
        self.log = self.wf.logger

    def run(self):
        sys.exit(self.wf.run(self.main))

    def main(self, wf):
        self.log.debug('start')
        args = wf.args

        queries = args[0].split()

        if len(queries) > 1:
            self.src, self.dst = queries[0:2]
            self.src = urllib.quote(self.src.encode('utf-8'))
            self.dst = urllib.quote(self.dst.encode('utf-8'))

            informations = self._fetch_transit_informations()
            for info in informations:
                wf.add_item(info.title, info.description, arg=info.url, valid=True, icon=self.ICON_URL)
        else:
            wf.add_item('transit <origin> <destination>')

        wf.send_feedback()

    def _get_url(self):
        return self.YAHOO_TRANSIT_SEARCH_URL % (self.src, self.dst)

    def _fetch_transit_informations(self):
        url = self._get_url()
        response = web.get(url)
        self.redirect_url = response.url
        soup = BeautifulSoup(response.content)
        routes = soup.select('[id^=route]')
        return [self._parse_information_from_node(route) for route in routes]

    def _parse_information_from_node(self, node):
        id = node['id']
        base_url = self._get_url()
        url = '%s#%s' % (base_url, id)

        summary = node.select('.routeSummary')[0]
        time = summary.select('li.time span')[0].getText()
        duration = summary.select('li.time')[0].getText()
        duration = duration.replace(time, '')
        transfer = summary.select('li.transfer')[0].getText()
        fare = summary.select('li.fare')[0].getText()
        humanized_fare = fare.replace('[priic]', '')

        info = TransitInformation(time, duration, transfer, humanized_fare, url)
        return info

if __name__ == '__main__':
    wf = YahooTransitAlfredWorkflow()
    wf.run()
