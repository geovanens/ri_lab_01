# -*- coding: utf-8 -*-
import scrapy
import json
from pdb import set_trace as st
import csv

from ri_lab_01.items import RiLab01Item
from ri_lab_01.items import RiLab01CommentItem


class Brasil247Spider(scrapy.Spider):
    name = 'brasil_247'
    allowed_domains = ['brasil247.com']
    start_urls = []

    def __init__(self, *a, **kw):
        super(Brasil247Spider, self).__init__(*a, **kw)
        with open('seeds/brasil_247.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    def writer_data(self, item):
        row = [
            item['title'].encode('utf-8'),
            item['sub_title'].encode('utf-8'),
            item['author'].encode('utf-8'),
            item['date'].encode('utf-8'),
            item['section'].encode('utf-8'),
            item['text'].encode('utf-8'),
            item['url'].encode('utf-8')
        ]
        with open(r'output/results.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def text_formater(self, text):
        text = [i.strip() for i in text if i.strip()]
        return "\n".join(text)

    def complement_string(self, string, size):
        return '0'*(size-len(string))+string

    def date_formater(self, date, hour):
        date = date.split(".")
        day = self.complement_string(date[0], 2)
        mounth = self.complement_string(date[1], 2)
        year = date[2]
        hour, minutes = hour.split(":")
        hour = self.complement_string(hour, 2)
        minutes = self.complement_string(minutes, 2)
        return "%s/%s/%s %s:%s:00" % (day, mounth, year, hour, minutes)


    def get_details(self, response):
        item = RiLab01Item()
        item['title'] = response.xpath('//*[@id="wrapper"]/div[5]/h1/text()').get().strip()
        item['sub_title'] = response.xpath('//*[@id="wrapper"]/div[5]/p[2]/text()').get().strip()
        item['author'] = response.xpath('//*[@id="wrapper"]/div[6]/section[1]/div[1]/p[2]/strong/text()').get().replace("-", "").strip()
        date = response.xpath('//*[@id="wrapper"]')[0].css('p::text')[0].get().strip().strip()
        hour = response.xpath('//*[@id="wrapper"]')[0].css('p::text')[2].get().strip().split()[-1]
        item['date'] = self.date_formater(date, hour)
        item['section'] = response.css('body::attr(id)').get().split("-")[-1]
        all_text = response.xpath('//*[@id="wrapper"]/div[6]')[0].css('p::text').getall()
        item['text'] = self.text_formater(all_text)
        item['url'] = response.url
        self.writer_data(item)

    def parse(self, response):
        links = [i for i in response.css('article a::attr(href)').getall()][:20]
        for link in links:
                yield response.follow(link, callback=self.get_details)  