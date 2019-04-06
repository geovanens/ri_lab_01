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

    def text_formater(self, text):
        """
        Formata o texto bruto, removendo o autor da noticia e os caracteres desnecessários
        """
        text[0] = ' - '.join(text[0].split(" - ")[1:])
        text = [i.strip() for i in text]
        return "\n".join(text)

    def complement_string(self, string, size):
        """
        Utilizado como auxiliar de date_formater acrescenta os '0's necessários para que
        data e hora fiquem no formato solicitado
        """
        return '0'*(size-len(string))+string

    def date_formater(self, date, hour):
        """
        Recebe dados brutos de data (dd.mm.aaaa) e hora (hh.mm)
        e formata para que a saída seja no formato dd/mm/aaaa hh:mm:ss
        """
        date = date.split(".")
        day = self.complement_string(date[0], 2)
        mounth = self.complement_string(date[1], 2)
        year = date[2]
        hour, minutes = hour.split(":")
        hour = self.complement_string(hour, 2)
        minutes = self.complement_string(minutes, 2)
        return "%s/%s/%s %s:%s:00" % (day, mounth, year, hour, minutes)


    def get_details(self, response):
        """
        Dada uma response de uma página de nóticias retorna um item 
        contendo todos os dados solicitados no lab
        """
        item = RiLab01Item()
        title = response.css('h1::text').get(default='').strip()
        paragraphs = response.css('p').xpath('string()').getall()
        sub_title = paragraphs[2]
        try:
            author = response.css('strong').xpath('string()').get().replace("-", "").strip()
        except AttributeError:
            author = paragraphs[5].split("-")[0].strip()
        date = paragraphs[0]
        hour = response.css('p.meta::text').get().strip().split()[-1]
        section = response.css('body::attr(id)').get().split("-")[-1]
        text = paragraphs[5:]
        text.pop()
        text = self.text_formater(text)
        item['title'] = title
        item['sub_title'] = sub_title
        item['author'] = author
        item['date'] = self.date_formater(date, hour)
        item['section'] = section
        item['text'] = text
        item['url'] = response.url
        #self.writer_data(item)
        #save = [item['title'], item['sub_title'], item['author'], item['date'], item['section'], item['text'], item['url']]
        #print(','.join(save))
        yield item

    def parse(self, response):
        '''
        Pega todos os links listados em uma página semente e os encaminha para
        o método que extrai os detalhes solicitados
        '''
        url = response.url.split(':')[-1]
        links = [i for i in response.css('article a::attr(href)').getall()]
        links = [i for i in links if i.startswith(url)]
        for link in links:
                yield response.follow(link, callback=self.get_details)  