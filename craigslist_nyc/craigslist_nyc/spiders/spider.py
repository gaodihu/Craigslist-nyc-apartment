from scrapy.spiders import Spider
from scrapy.selector import Selector
from craigslist_nyc.items import CraigslistNycItem


class MySpider(Spider):
    name = "craig"
    allowed_domains = ["craigslist.org"]
    start_urls = ["https://newyork.craigslist.org/search/abo"]

    def parse(self, response):
        hxs = Selector(response)
        titles = hxs.xpath("//a[@class='result-title hdrlnk']")
        for titles in titles:
            title = titles.xpath("text()").extract()
            link = titles.xpath("@href").extract()
            print title, link
