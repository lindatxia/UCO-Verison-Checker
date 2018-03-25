# run this file as
#
# scrapy runspider asana.py

from scrapy import Request
from scrapy.spiders import Spider

from difflib import Differ
from pprint import pprint

class S1(Spider):
    name = 's1'
    custom_settings = {
            'DOWNLOAD_DELAY': 0.5
            }
    allowed_domains = ['asana.com']
    start_urls = ["https://asana.com/terms"]

    def parse(self, response):
        text = response.xpath("//body//text()").extract()
        text = ''.join(text)
        text = clean_text(text,"Asana User Terms of Service", "an integral link.")
        f= open("asana.txt","w+")
        for line in text:
            f.write(str(line))
        f.close()
        compare("asana_old.txt","asana.txt","templates/changes_table.html")

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

def compare(a,b,filename):
    out = get_differences(a,b)
    make_html_table(out,filename)

# using the Differ module of the difflib library to compare 
# outputs a generator object that is converted into a list of 
# the changes of the form [[added/removed, line]]
# - -> line was removed
# + -> line was added
def get_differences(a,b):
    a_list = split_txt(a)
    b_list = split_txt(b)
    d = Differ()
    result = list(d.compare(a_list,b_list))
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