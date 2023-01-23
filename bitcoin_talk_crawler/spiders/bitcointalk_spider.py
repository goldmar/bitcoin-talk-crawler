import scrapy
import re 
import os 
from pdb import set_trace

class BitcointalkSpider(scrapy.Spider):
    name = "bitcointalk"
    
    cid2cname = {}
    cid2cname['1'] = "Bitcoin_Discussion"
    cid2cname['6'] = "Development_TechinalDiscussion"
    cid2cname['14'] = "Mining"
    cid2cname['4'] = "BitcoinTechnicalSupport"
    cid2cname['12'] = "Project_Development"
    cid2cname['7'] = "Economics"
    cid2cname['5'] = "Market_Place"
    cid2cname['8'] = "Trading_Discussion"
    cid2cname['24'] = "Meta"
    cid2cname['34'] = "Politics_Society"
    cid2cname['39'] = "Beginner_Help"
    cid2cname['9'] = "Off-topic"
    cid2cname['250'] = "Serious_Discussion"
    cid2cname['67'] = "Altcoin_Discussion"
    cid2cname['159'] = "Announcements (Altcoins)"
    cid2cname['160'] = "Mining (Altcoins)"
    cid2cname['199'] = "Pools (Altcoins)"
    cid2cname['161'] = "Marketplace (Altcoins)"
    cid2cname['197'] = "Service_Announcements(Altcoins)"
    cid2cname['198'] = "Service Discussion(Altcoins)"
    cid2cname['238'] = "Bounties (Altcoins)"
    cid2cname['224'] = "Speculation (Altcoins)"

    start_urls = [
        'https://bitcointalk.org/index.php?board=1.0', # Bitcoin Discussion
        'https://bitcointalk.org/index.php?board=6.0', # Development & Techincal Discussion
        'https://bitcointalk.org/index.php?board=14.0', # Mining
        'https://bitcointalk.org/index.php?board=4.0', # Bitcoin Technical Support
        'https://bitcointalk.org/index.php?board=12.0', # Project Development
        'https://bitcointalk.org/index.php?board=7.0', # Economics 
        'https://bitcointalk.org/index.php?board=5.0', # Market Place
        'https://bitcointalk.org/index.php?board=8.0', # Trading Discussion
        'https://bitcointalk.org/index.php?board=24.0', # Meta
        'https://bitcointalk.org/index.php?board=34.0', # Politics & Society
        'https://bitcointalk.org/index.php?board=39.0', # Beginners & Help
        'https://bitcointalk.org/index.php?board=9.0', # Off-topic
        'https://bitcointalk.org/index.php?board=250.0', # Serious Discussion
        'https://bitcointalk.org/index.php?board=67.0', # Altcoin Discussion
        'https://bitcointalk.org/index.php?board=159.0', # Announcements (Altcoins)
        'https://bitcointalk.org/index.php?board=160.0', # Mining (Altcoins)
        'https://bitcointalk.org/index.php?board=199.0', # Pools (Altcoins)
        'https://bitcointalk.org/index.php?board=161.0', # Marketplace (Altcoins)
        'https://bitcointalk.org/index.php?board=197.0', # Service Announcements (Altcoins)
        'https://bitcointalk.org/index.php?board=198.0', # Service Discussion (Altcoins)
        'https://bitcointalk.org/index.php?board=238.0', # Bounties (Altcoins)
        'https://bitcointalk.org/index.php?board=224.0', # Speculation (Altcoins)
    ]
    moved_regex = re.compile(r"^MOVED: ")

    def parse(self, response):
        page = response.url.split("/")[-1].split("?")[-1]
        category_id = response.url.split('=')[1].split('.')[0]
        last_page = int(response.xpath('//td[@id="toppages"]/a[@class="navPages"]')[-1].xpath('text()')[0].extract())
        for i in range(last_page):
            yield scrapy.Request('https://bitcointalk.org/index.php?board=' + category_id + '.' + str(i*40),
                                 callback=self.parse_topic_list)

    def parse_topic_list(self, response):
        data_path = './data/raw/'
        x = '//div[@class="tborder"]//td/span/a[contains(@href, "index.php?topic")]'

        for a in response.xpath(x):
            topic_title = a.xpath('text()')[0].extract()
            if not self.moved_regex.match(topic_title):
                topic_url = response.urljoin(a.xpath('@href')[0].extract())
                topic_id = topic_url.split('=')[1].split('.')[0]
                category_id = response.url.split('=')[1].split('.')[0]
                # https://bitcointalk.org/index.php?topic=20333.0
                print_url = 'https://bitcointalk.org/index.php?topic={0}.0'.format(topic_id)

                filename = f'bitcointalk_{category_id}_{topic_id}_1.html'
                file_path = os.path.join(data_path, category_id, filename)
                if os.path.exists(file_path):
                    continue

                yield scrapy.Request(print_url,
                                     callback=self.parse_topic_page,
                                     meta={'category_id': category_id,
                                           'topic_id': topic_id,
                                           'topic_title': topic_title})


    def parse_topic_page(self, response):
        category_id = response.meta['category_id']
        topic_id = response.meta['topic_id']
        topic_title = response.meta['topic_title'] 
        
        # extract sub-page urls 
        x = '//div[@id="bodyarea"]/table//td[@class="middletext"]/a/@href'
        url_list = response.xpath(x).extract()

        # first page is not included in the first page
        url_list.insert(0, 'https://bitcointalk.org/index.php?topic={0}.0'.format(topic_id))

        # remove 'all' page
        if len(url_list[-1].split(';')) > 1:
            url_list.pop()
        
        for idx, subpage_url in zip(range(len(url_list)), url_list):
            # page id             
            page_id = idx + 1
    
            yield scrapy.Request(subpage_url,
                                dont_filter=True,
                                callback=self.save_topic_page,
                                meta={'category_id': category_id,
                                    'topic_id': topic_id,
                                    'topic_title': topic_title,
                                    'page_id': page_id})

    def save_topic_page(self, response):
        category_id = response.meta['category_id']
        topic_id = response.meta['topic_id']
        topic_title = response.meta['topic_title']
        page_id = response.meta['page_id']

        filename = f'bitcointalk_{category_id}_{topic_id}_{page_id}.html'
        data_path = './data/raw/'
        category_dir_path = os.path.join(data_path, category_id)
        if not os.path.exists(category_dir_path):
            os.mkdir(category_dir_path)
 
        new_fname = os.path.join(category_dir_path, filename)
        if os.path.exists(new_fname):
            self.log(f'File exists: {new_fname}')
            return
        
        with open(new_fname, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')
