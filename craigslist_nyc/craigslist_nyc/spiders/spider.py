from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy import Request, signals
from scrapy.xlib.pydispatch import dispatcher

from craigslist_nyc.items import CraigslistNycItem

import json
import hashlib

domain_name = "https://newyork.craigslist.org"
start_url = domain_name + "/search/hhh"

# Params explanation:
# Posted today, available beyond 30 days
get_params = "sort=date&excats=2-17-21-1-17-7-24-10-22-22-1&postedToday=1&max_price=1500&availabilityMode=1&bundleDuplicates=1"

write_logs = True
log_file_name = "logs.txt"
pic_hash_file_name = "pic-hashes.txt"
body_hash_file_name = "body-hashes.txt"
result_file_name = "results.txt"
queried_urls_path = "urls.txt"
starred_path = "starred.txt"
actions_path = "actions.txt"

enable_directions_query = True
google_directions_query_key = "AIzaSyDfbd9R06aZ304FMrqYD34sMrVKMrepv6E"
directions_query_prefix = "https://maps.googleapis.com/maps/api/directions/json?destination=40.761879,-73.968401&mode=transit&key=" + google_directions_query_key + "&origin="

queried_urls = []
queried_pics = []
queried_bodies = []
found_results = dict()

send_email = True
duration_threshold = 1680
price_threshold = 1500
email_web_service = "http://localhost:5000/send"

strict_availability = True

class MySpider(Spider):
    name = "craig"
    allowed_domains = ["craigslist.org", "maps.googleapis.com", "localhost"]
    start_urls = [start_url + "?" + get_params]

    def __init__(self):
        self.starred_cnt = 0
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def derive_full_link(self, link):
        if link.startswith("//"):
            query_link = "https:" + link
        else:
            query_link = domain_name + link
        return query_link

    def parse(self, response):
        try:
            with open(queried_urls_path, "r") as queried_urls_file:
                queried_urls = queried_urls_file.read().splitlines()
        except IOError:
            queried_urls = []

        try:
            with open(pic_hash_file_name, "r") as pics_file:
                queried_pics = pics_file.read().splitlines()
        except IOError:
            queried_pics = []

        try:
            with open(body_hash_file_name, "r") as body_file:
                queried_bodies = body_file.read().splitlines()
        except IOError:
            queried_bodies = []

        selector = Selector(response)
        titles = selector.xpath("//a[@class='result-title hdrlnk']")
        for item in titles:
            link = item.xpath("@href").extract()[0]
            title = item.xpath("text()").extract()[0]
            query_link = self.derive_full_link(link)

            if not query_link in queried_urls:
                yield Request(query_link, callback = self.parse_listing)
            else:
                print "Ignored (" + query_link + ") since it's already queried"

        # Single test:
        # yield Request(domain_name + titles[0].xpath("@href").extract()[0], callback = self.parse_listing)

    def log_error(self, msg):
        if write_logs:
            with open(log_file_name, "a") as log_file:
                log_file.write(msg)

    def log_result(self, msg):
        with open(result_file_name, "a") as result_file:
            result_file.write(msg)

    def log_queried_url(self, msg):
        with open(queried_urls_path, "a") as queried_urls_file:
            queried_urls_file.write(msg)

    def log_starred(self, msg):
        with open(starred_path, "a") as starred_file:
            starred_file.write(msg)

    def log_actions(self, msg):
        with open(actions_path, "a") as actions_file:
            actions_file.write(msg)

    def log_pic_hashes(self, msg):
        with open(pic_hash_file_name, "a") as pics_file:
            pics_file.write(msg)

    def log_body_hashes(self, msg):
        with open(body_hash_file_name, "a") as body_file:
            body_file.write(msg)

    def parse_listing(self, response):
        selector = Selector(response)
        queried_urls.append(response.url)
        self.log_queried_url(response.url + "\n")

        removed = response.xpath('//span[@id="has_been_removed"]').extract()
        if removed:
            self.log_result("Post " + response.url + " has been removed")
            return
        skip_entry = False

        try:
            title = response.xpath('//title/text()').extract()[0].lower()
            m = hashlib.sha256()
            m.update(title)
            digest = m.hexdigest()
            if digest in queried_bodies:
                skip_entry = True
            else:
                queried_bodies.append(digest)
                self.log_body_hashes(digest + "\n")
        except IndexError:
            title = ""
            self.log_error("===== Failed to get title (" + response.url + "): =====\n" + response.text + "\n\n")

        try:
            body = response.xpath('//section[@id="postingbody"]').extract()
            body_str = str(body).lower()
            if "older female" in title or "older female" in body_str or "aa female" in body_str or "female only" in body_str or "females only" in body_str or "only female" in body_str or "girl only" in body_str or "girls only" in body_str or "only girl" in body_str:
                skip_entry = True
            m = hashlib.sha256()
            m.update(body_str)
            digest = m.hexdigest()
            if digest in queried_bodies:
                skip_entry = True
            else:
                queried_bodies.append(digest)
                self.log_body_hashes(digest + "\n")
        except IndexError:
            body = ""
            self.log_error("===== Failed to get body (" + response.url + "): =====\n" + response.text + "\n\n")

        try:
            times = response.xpath('//time[@class="timeago"]/@datetime').extract()
            post_time = times[0]
            if len(times) == 2:
                update_time = post_time
            elif len(times) == 3:
                update_time = times[-1]
            else:
                print("unknown number of times occurred:" + str(times))
        except IndexError:
            post_time = ""
            update_time = ""
            self.log_error("===== Failed to get times (" + response.url + "): =====\n" + response.text + "\n\n")

        try:
            price = response.xpath('//span[@class="price"]/text()').extract()[0]
            if price.startswith("$"):
                price = price[1:]
        except IndexError:
            price = "0"
            self.log_error("===== Failed to get price (" + response.url + "): =====\n" + response.text + "\n\n")

        try:
            housing = response.xpath('//span[@class="housing"]/text()').extract()[0].lower()
        except IndexError:
            try:
                housing = response.xpath('//p[@class="attrgroup"]/span').extract()[0].lower()
                if not ("br" in housing or "ba" in housing):
                    housing = ""
                    self.log_error("===== House type not provided: (" + response.url + "): =====\n\n")
            except IndexError:
                housing = ""
                self.log_error("===== Failed to get house type (" + response.url + "): =====\n" + response.text + "\n\n")

        try:
            maps = response.xpath('//div[@id="map"]')
            latitude = maps[0].xpath("@data-latitude").extract()[0]
            longitude = maps[0].xpath("@data-longitude").extract()[0]
            map_accuracy = maps[0].xpath("@data-accuracy").extract()[0]
        except IndexError:
            latitude = ""
            longitude = ""
            map_accuracy = ""
            self.log_error("===== Failed to get location (" + response.url + "): =====\n" + response.text + "\n\n")

        try:
            thumbnail_img_urls = response.xpath('//a[@class="thumb"]/@href').extract()
        except IndexError:
            thumbnail_img_urls = []
            self.log_error("===== Failed to get thumbnail_img_urls (" + response.url + "): =====\n" + response.text + "\n\n")

        try:
            availability_start = response.xpath('//span[contains(@class,"property_date")]/text()').extract()[0]
            if strict_availability:
                if not "jun" in availability_start.lower():
                    skip_entry = True
        except IndexError:
            availability_start = ""
            self.log_error("===== Failed to get availability_start (" + response.url + "): =====\n" + response.text + "\n\n")
            if strict_availability:
                skip_entry = True
        try:
            reply_link = response.xpath('//a[@id="replylink"]/@href').extract()[0]
            reply_link = self.derive_full_link(reply_link)
        except IndexError:
            self.log_error("===== Failed to get reply_link (" + response.url + "): =====\n" + response.text + "\n\n")

        found_results[response.url] = {
            "title": title,
            "body": body,
            "price": price,
            "type": housing,
            "post_time": post_time,
            "update_time": update_time,
            "latitude": latitude,
            "longitude": longitude,
            "map_accuracy": map_accuracy,
            "availability_start": availability_start,
            "thumbnail_img_urls": thumbnail_img_urls,
            "url": response.url,
            "reply_link": reply_link,
            "skip_entry": skip_entry
        }

        if enable_directions_query:
            if latitude != "" and longitude != "":
                directions_query_url = directions_query_prefix + latitude + "," + longitude
                print "query url is " + directions_query_url
                yield Request(directions_query_url, callback = 
                    lambda x : self.parse_directions_query(x, response.url))
            else:
                print "Directions query aborted because map location not present"
        else:
            self.log_result(json.dumps(found_results[response.url], indent = 2, sort_keys = True) + "\n")

    def parse_directions_query(self, response, referrer_url):
        res = json.loads(response.text)
        try:
            # value is in seconds
            total_duration = res["routes"][0]["legs"][0]["duration"]["value"]
            if referrer_url in found_results:
                found_results[referrer_url]["duration"] = total_duration
                # print "before!"
                if int(found_results[referrer_url]["duration"]) < duration_threshold and int(found_results[referrer_url]["price"]) < price_threshold:
                    if send_email:
                        if found_results[referrer_url]["skip_entry"]:
                            print "Interested but skipped: (" + referrer_url + ")!"
                        else:
                            yield Request(found_results[referrer_url]["reply_link"], callback = 
                                lambda x : self.send_email_inquiry(x, referrer_url))
                else:
                    print "Not interested: (" + referrer_url + ")!"
                # print "after!"
                self.log_result(json.dumps(found_results[referrer_url], indent = 2, sort_keys = True) + "\n")
            else:
                print "referrer url (" + referrer_url + ") not found in dict"
        except ValueError as e:
            print str(e)
        except IndexError as e:
            print str(e)

    # this call won't work...
    # def analyze_url(self, url):
    #     print "analyzing!"

    def parse_email_response(self, response, url):
        print "email sent for (" + url + ")!"
        self.log_starred("email sent for (" + url + ")!")

    def send_email_inquiry(self, response, url):
        able_to_connect = False
        try:
            email_addr = response.xpath('//a[@class="mailapp"]/text()').extract()[0]
            found_results[url]["email_addr"] = email_addr
            print "About to send email to : " + email_addr + "(" + url + ")!"
            self.log_starred("About to send email to : " + email_addr + " (" + url + ")!" + "\n")
            self.log_actions("About to send email to : " + email_addr + " (" + url + ")!" + "\n")
            yield Request(email_web_service + "?email= " + email_addr + "&cl=" + url, callback = 
                    lambda x : self.parse_email_response(x, url))
            able_to_connect = True
        except IndexError as e:
            print str(e)

        try:
            phone_number = response.xpath('//a[@class="reply-tel-link"]/@href').extract()[0]
            found_results[url]["phone_number"] = phone_number.split(':')[1]
            print "About to text : " + found_results[url]["phone_number"] + "(" + url + ")!"
            self.log_starred("About to text : " + found_results[url]["phone_number"] + " (" + url + ")!" + "\n")
            self.log_actions("About to text : " + found_results[url]["phone_number"] + " (" + url + ")!" + "\n")
            able_to_connect = True
        except IndexError as e:
            print str(e)
            print "Cannot grab phone number from " + response.url + ", or phone number not in expected format"

        if able_to_connect:
            self.log_starred(json.dumps(found_results[url], indent = 2, sort_keys = True) + "\n")
            self.starred_cnt += 1

    def spider_closed(self, spider):
        print "Spider about to close, found " + str(self.starred_cnt) + " interested entries!"


