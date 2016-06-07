# -*- coding: utf-8 -*-
import re
import scrapy
import urllib2
import json
from bs4 import BeautifulSoup
import csv


class PolyvorePphSpider(scrapy.Spider):
    name = "polyvore_pph"

    def __init__(self):
        self.allowed_domains = ["polyvore.com"]
        self.start_urls = self.get_url()
        self.fl = open("output.csv", "w")
        self.fl_hl = csv.writer(self.fl)

    def get_url(self):
        url = "http://www.polyvore.com/cgi/splash.trend?.in=json&.out=jsonx&request="
        page_num = 0
        offset = 21
        param = '{"trend":"Trending Now","page":' + str(page_num) + ',".passback":{"next_token":"{\\"offset\\":' + str(
            offset) + '}"}}'
        while True:
            full_url = url + urllib2.quote(param, safe='')
            yield full_url
            html = urllib2.urlopen(full_url).read()
            res = json.loads(html)
            next_token = res[".passback"]["next_token"]
            next_offset = int(re.findall('\d+', next_token)[0])
            offset = next_offset
            page_num += 1
            param = '{"trend":"Trending Now","page":' + str(
                page_num) + ',".passback":{"next_token":"{\\"offset\\":' + str(
                offset) + '}"}}'
            if next_token is None:
                break

    def parse(self, response):
        json_data = json.loads(response.body)
        parsed_data = BeautifulSoup(json_data["result"]["html"])

        for li in parsed_data.find_all("li"):
            data = BeautifulSoup(str(li))
            link = data.find_all("a")
            image = data.find_all("img")
            url = link[0].get("href").replace("..", "http://www.polyvore.com")
            title = link[0].get("title")
            image_url = image[0].get("src")
            self.fl_hl.writerow([title, url, image_url])
            self.fl.flush()
