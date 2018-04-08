# run this file as
#
# scrapy runspider scrape.py

import datetime
import time

from scrapy import Request
from scrapy.spiders import Spider

from difflib import Differ
from pprint import pprint

import sys

class S1(Spider):
    name = 's1'
    custom_settings = {
            'DOWNLOAD_DELAY': 0.5
            }

    def __init__(self, category=None, *args, **kwargs):
        super(S1, self).__init__(*args, **kwargs)
        self.start_urls = ['%s' % self.link]

    def parse(self, response):
        text = response.xpath("//body//text()").extract()
        text = ''.join(text)
        text = clean_text(text,self.start,self.end)
        new_filename = self.name+datetime.date.today().strftime("%m_%d_%y")+".txt"
        f= open(new_filename,"w+")
        for line in text:
            f.write(str(line))
        f.close()

# takes away all text before start and after end
def clean_text(s,start,end):
    ans = s
    i = s.find(start)
    j = s.find(end)
    if i !=-1 and j!=-1:
        ans = s[i:j+len(end)]
    elif i!=-1 and j==-1:
        ans = s[i:]
    elif i==-1 and j!=-1:
        ans = s[:j+len(end)]
    else:
        ans = s
    return ans