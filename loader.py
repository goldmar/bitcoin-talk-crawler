import pickle
import argparse
from pdb import set_trace

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--category", help="category id", default=67)
args = parser.parse_args()

cid = str(args.category)
set_trace()
with open('data/parsed/bitcointalk_{}_parsed'.format(cid), 'rb') as f:
    pickle_data = pickle.load(f)
posts_dict, threads_dict = pickle_data

# print(len(posters_dict))
print(len(posts_dict))
print(len(threads_dict))