# -*- coding: utf-8 -*-
import re
import calendar
import time
import scrapy

from ..items import BitcoinTalkMessageItem


class BitcointalkSpider(scrapy.Spider):
    name = "bitcointalk"
    allowed_domains = ["bitcointalk.org"]
    start_urls = (
        'https://bitcointalk.org/index.php?board=7.0',
        'https://bitcointalk.org/index.php?board=57.0',
    )

    moved_regex = re.compile(r"^MOVED: ")

    post_regex = re.compile(r"""^					<br />
					<hr size="2" width="100%" />
					Title: <b>(?P<post_title>.*?)</b><br />
					Post by: <b>(?P<post_author>.*?)</b> on <b>(?P<post_date_time>.*?)</b>
					<hr />
					<div style="margin: 0 5ex;">(?P<post_message>.*?)</div>$""",
        re.MULTILINE)

    def parse(self, response):
        category_id = response.url.split('=')[1].split('.')[0]
        last_page = int(response.xpath('//td[@id="toppages"]/a[@class="navPages"]')[-1].xpath('text()')[0].extract())

        for i in range(last_page):
            yield scrapy.Request('https://bitcointalk.org/index.php?board=' + category_id + '.' + str(i*40),
                                 callback=self.parse_topic_list)

    def parse_topic_list(self, response):
        x = '//div[@class="tborder"]//td/span/a[contains(@href, "index.php?topic")]'
        for a in response.xpath(x):
            topic_title = a.xpath('text()')[0].extract()
            if not self.moved_regex.match(topic_title):
                topic_url = response.urljoin(a.xpath('@href')[0].extract())
                topic_id = topic_url.split('=')[1].split('.')[0]
                category_id = response.url.split('=')[1].split('.')[0]
                print_url = 'https://bitcointalk.org/index.php?action=printpage;topic={0}.0'.format(topic_id)
                yield scrapy.Request(print_url,
                                     callback=self.parse_topic_page,
                                     meta={'category_id': category_id,
                                           'topic_id': topic_id,
                                           'topic_title': topic_title})

    def parse_topic_page(self, response):
        category_id = response.meta['category_id']
        topic_id = response.meta['topic_id']
        topic_title = response.meta['topic_title']

        for (post_number, post) in enumerate(self.post_regex.finditer(response.body), start=1):
            post_date_time = post.group('post_date_time')
            struct_time = time.strptime(post_date_time, "%B %d, %Y, %I:%M:%S %p")
            timestamp = calendar.timegm(struct_time)

            item = BitcoinTalkMessageItem()
            item['timestamp'] = timestamp
            item['category_id'] = category_id
            item['topic_id'] = topic_id
            item['topic_title'] = topic_title
            item['message_number'] = post_number
            item['message_author'] = post.group('post_author')
            item['message_text'] = post.group('post_message')
            yield item
