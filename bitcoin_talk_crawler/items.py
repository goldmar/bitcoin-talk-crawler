# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BitcoinTalkMessageItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    timestamp = scrapy.Field()
    category_id = scrapy.Field()
    topic_id = scrapy.Field()
    topic_title = scrapy.Field()
    message_number = scrapy.Field()
    message_author = scrapy.Field()
    message_text = scrapy.Field()
