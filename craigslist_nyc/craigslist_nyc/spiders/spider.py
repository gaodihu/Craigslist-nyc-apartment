from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy import Request
from craigslist_nyc.items import CraigslistNycItem

domain_name = "https://newyork.craigslist.org"
start_url = domain_name + "/search/abo"

class MySpider(Spider):
    name = "craig"
    allowed_domains = ["craigslist.org"]
    start_urls = [start_url]

    def parse(self, response):
        selector = Selector(response)
        titles = selector.xpath("//a[@class='result-title hdrlnk']")
        # for item in titles:
        #     link = item.xpath("@href").extract()[0]
        #     title = item.xpath("text()").extract()[0]     
        #     yield Request(domain_name + link, callback = self.parse_listing)

        # Single test:
        yield Request(domain_name + titles[0].xpath("@href").extract()[0], callback = self.parse_listing)

    def parse_listing(self, response):
        selector = Selector(response)

        title = response.xpath('//title/text()').extract()[0].lower()
        body = response.xpath('//section[@id="postingbody"]').extract()

        times = response.xpath('//time[@class="timeago"]/@datetime').extract()
        post_time = times[0]
        if len(times) == 2:
            update_time = post_time
        elif len(times) == 3:
            update_time = times[-1]
        else:
            print("unknown number of times occurred:" + str(times))

        price = response.xpath('//span[@class="price"]/text()').extract()[0]
        housing = response.xpath('//span[@class="housing"]/text()').extract()[0]

        maps = response.xpath('//div[@id="map"]')
        latitude = maps[0].xpath("@data-latitude").extract()[0]
        longitude = maps[0].xpath("@data-longitude").extract()[0]

        thumbnail_img_urls = response.xpath('//a[@class="thumb"]/@href').extract()

        print title, price, housing, post_time, update_time, latitude, longitude, thumbnail_img_urls
