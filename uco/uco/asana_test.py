# run this file as
#
# scrapy runspider asana_test.py

from scrapy import Request
from scrapy.spiders import Spider

# Spider definition
class S1(Spider):
    name = 's1'
    custom_settings = {
            'DOWNLOAD_DELAY': 0.5
            }
    allowed_domains = ['asana.com']
    # this would have to be updated for each software
    start_urls = ["https://asana.com/terms"]

    # parse automatically gets called when the file is run
    def parse(self, response): 
        # use xpath to get a list of all the text in the page
        text = response.xpath("//body//text()").extract()
        text = ''.join(text)
        text = clean_text(text,"Asana User Terms of Service", "an integral link.")
        # write terms into a txt file
        f= open("asana.txt","w+")
        for line in text:
            f.write(str(line))
        f.close() 
        return text


# remove all text before start and after end
# start and end would have to be sent in by the user
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
