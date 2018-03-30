# run this file as
#
# scrapy runspider asana.py

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
        # for now hardcoded to asana_old.txt, but once file input works this will change
        self.old_terms = "asana_old.txt"

    def parse(self, response):
        text = response.xpath("//body//text()").extract()
        text = ''.join(text)
        text = clean_text(text,self.start,self.end)
        new_filename = self.name+".txt"
        f= open(new_filename,"w+")
        for line in text:
            f.write(str(line))
        f.close()
        compare(self.old_terms,new_filename,"templates/changes_table.html")

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

# compares a and b and outputs a HTML table of the changes. 

def compare(old,new,filename):
    out = get_differences(old,new)
    make_html_table(out,filename)

# using the Differ module of the difflib library to compare 
# outputs a generator object that is converted into a list of 
# the changes of the form [[added/removed, line]]
# - -> line was removed
# + -> line was added
def get_differences(old,new):
    # old_list = old.split("\n")
    old_list = split_txt(old)
    new_list = split_txt(new)
    d = Differ()
    result = list(d.compare(old_list,new_list))
    for i in range(0,len(result)):
        result[i]=result[i].split()
    return result

def split_txt(txt):
    f = open(txt,"r+")
    ans = f.read().splitlines()
    f.close()
    return ans

# created an html table that assigns a class to the rows
# that have been added and removed
def make_html_table(l,name):
    ans = ['<table>\n']
    for line in l:
        front = '\t<tr>\n\t\t<td>'
        if len(line) == 0 :
            continue
        elif line[0] == "?":
            continue
        elif line[0] == "-":
            front = '\t<tr>\n\t\t<td class ='+'"removed">'
        elif line[0] == "+":
            front = '\t<tr>\n\t\t<td class ='+'"added">'
        ans.append(str(add_line(line,front)))
    ans.append('</table>')
    write_file(ans,name)

def add_line(line,front):
    end = '</td>\n\t</tr>\n'
    if (line[0] == "+" or line[0] == "-"):
        line = line[1:]
    return front+" ".join(line)+end

def write_file(l,name):
    f = open(name,"w+")
    for line in l:
        f.write(str(line))
    f.close()