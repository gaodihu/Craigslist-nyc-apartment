# Craigslist-nyc-apartment

This is a script that crawls recent Craigslist posting for apartments in New York City, filter them by some (hard coded) standards, and email the listing we are interested in.

The project was built and tested in the week of 04/27/17, and will not work if Craigslist updates their website (e.g. change element names, classes, layout, etc)!

### Current standards are:
 * Cheaper than $1500
 * Has a location in the listing, and from that location takes less than 25 minutes commute to 731 Lexington Avenue (by Google map queried from Google API)
 * Not explicitly mentioning "female only"
 * Not a repost (having the same title or body hash)
 * Not already inquired (having sent an email already)

### What it does afterwards:
 * In emailer folder there is a Flask app that sends email to recipients listed in the http GET parameter. If email option (hardcoded) is on, the crawler will tell the emailer app to send an email from a hardcoded account to a designated account. 

### How to run:
 * Replace YOUR.API.KEY in spider.py, replace email credentials and headers in emailer.py and settings.py
 * Meant to run as a cron (e.g. every 10 minutes), so that people gets your email rather soon after their listing appears, and the script don't need to worry about switching to next page since listings don't pop up that fast. Also sends email sooner boosts the response rate.
 * To run once, consult cron.sh

### Workflow:
 * Sends initial query, which may look like 
 https://newyork.craigslist.org/search/hhh?sort=date&excats=2-17-21-1-17-7-24-10-22-22-1&postedToday=1&max_price=1500&availabilityMode=1&bundleDuplicates=1
 * For each listing returned by the initial query, query its details if not already queried, the url may look like
 https://newyork.craigslist.org/mnh/sub/6162293366.html
 * Extract structured data from each url, including price, location, female only, etc. If all other criteria match (price, not female only, etc), send location to google API for Google maps query. (Only query Google API when necessary to minimize the amount of requests: in my experience this works well within the boundary of free tier service)
 * If Google maps query result also fits in criteria, send query to Craigslist for method of contact (We ask this only all criteria match, so that we don't do it too often hopefully, and get blocked by reCaptcha)
 * If method of contact is present, send a local request to emailer script to send inquiry.

### Logs and experience:
 * This ran for a week without being effectively blocked by captcha (which did happen in about a week, unfortunately)
 * This script keeps several logs:
   * actions.txt: the email addresses we are about to send inquiry to, if they have phone numbers on file, we keep a record of that, too
   * body-hashes.txt: sha256s of bodies and titles of listings we already queried (filter out user reposts)
   * logs.txt: warnings / errors in parsing each listing (for example housing type not present, expected tags not present, etc)
   * results.txt: well structured (json) data extracted from all listings we saw
   * starred.txt: well structured (json) data from listings that matches the filter criteria
   * urls.txt: listing urls we already checked (and won't check again)
 * The experiment was conducted between (04/27/17 and 05/04/17). The script ended up sending about 200 emails, fetching about 40 replies, scheduled about 30 FaceTime / Skype sessions scattered throughout two weeks. Among the 30 I'd be happy to go ahead with most of them (script does represent my criteria well :P), but ended up going to NYC in person and rented a different place.

### Inspired by:

http://mherman.org/blog/2012/11/05/scraping-web-pages-with-scrapy/#.WQE8plPysUs

### Dependency:

* Scrapy

### License:

MIT

### Contact:

Drop Zhehao <zhehao@cs.ucla.edu> an email if interested!


**Disclaimer: this script is hacked together in one night and a lot quick dirty workarounds are still around. Please don't run as is! If you are interested in extending the script, there are quite a few things on my mind, shoot me a message!**


**Big thanks to all the people that kindly responded and had the patience to set up a call with me!**



**Irrelevant but new problem: _I'm looking for a roommate_ :P! My ad: https://newyork.craigslist.org/que/roo/6161826057.html**