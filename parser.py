import pickle
import os 
from lxml import etree
from bs4 import BeautifulSoup
from pdb import set_trace
from collections import defaultdict
import argparse
from tqdm import tqdm
import datetime

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--category", help="category id", default=8)
args = parser.parse_args()

data_path = 'data/raw'

# posts_dict: 
# key:  msg_id
# value: dict{msg_id:'', poster:'', thread_id:'', poster_id: '', reply_num:'', quote: '', msg:''}
posts_dict = {}

# threads_dict: 
# key:  thread_id
# value: [dict{msg_id:'', poster:'', thread_id:'', poster_id: '', reply_num:'', quote: '', msg:''}, ...]
threads_dict = defaultdict(list)

# parsing
cid = str(args.category)
threads_html_list = os.listdir(os.path.join(data_path, cid))

for thread_html in tqdm(threads_html_list):
    thread_id = thread_html.split('_')[-2]
    page_id = thread_html.split('_')[-1].split('.')[0]
    
    soup = BeautifulSoup(open('data/raw/{}/bitcointalk_{}_{}_{}.html'.format(cid, cid, thread_id, page_id), encoding="ISO-8859-1"), 'html.parser')
    # soup = BeautifulSoup(open('data/raw/67/bitcointalk_2500651_1.html', encoding="ISO-8859-1"), 'html.parser')
    dom = etree.HTML(str(soup))

    msg_body_list = dom.xpath('//div[@id="bodyarea"]/form/table//td[@class="windowbg" or @class="windowbg2"]')
    for msg_body in msg_body_list:
        msg_url = msg_body.xpath('table/tr/td/table/tr/td/a/@href')
        if len(msg_url) == 0:
            continue
        else:
            msg_url = msg_url[0]
        msg_id = msg_url.split('#')[-1]
        
        msg_time_path = msg_body.xpath('.//td[@class="td_headerandpost"]/table//div[@class="smalltext"]')[0]
        if msg_time_path.xpath('./text()'):
            msg_time = msg_time_path.xpath('./text()')[0]
        else:
            msg_time = msg_time_path.xpath('./span/text()')[0]
        try:
            msg_time = datetime.datetime.strptime(msg_time, "%B %d, %Y, %X %p")
        except:
            continue
            
        poster = msg_body.xpath('.//td[@class="poster_info"]/b/a/text()')
        if len(poster) == 0:
            continue
        else:
            poster = poster[0]
            
        poster_url = msg_body.xpath('.//td[@class="poster_info"]/b/a/@href')[0]
        uid = int(poster_url.split('=')[-1])

        msg = '\n'.join(msg_body.xpath('.//div[@class="post"]/text()'))
        
        quote_url = msg_body.xpath('.//div[@class="quoteheader"]/a/@href')
        if len(quote_url) == 0:
            posts_dict[msg_id] = {'msg_id': msg_id, 'poster': poster, 'thread_id': thread_id, 'msg': msg}
            threads_dict[thread_id] += [{'msg_id': msg_id, 'poster': poster, 'thread_id': thread_id, 'msg': msg}]
        else: 
            quote_id = quote_url[-1].split('#')[-1]
            posts_dict[msg_id] = {'msg_id': msg_id, 'poster': poster, 'poster_id': uid, 'thread_id': thread_id, 'quote': quote_id, 'msg': msg}
            threads_dict[thread_id] += [{'msg_id': msg_id, 'poster': poster, 'poster_id': uid, 'thread_id': thread_id, 'quote': quote_id, 'msg': msg}]


if not os.path.exists('data/parsed/'):
    os.mkdir('data/parsed')
pickle.dump([posts_dict, threads_dict], open("data/parsed/bitcointalk_{}_parsed".format(cid), "wb"))



