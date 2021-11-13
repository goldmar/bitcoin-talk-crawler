# /bin/bash

categories=`ls ./data/raw`

for category in $categories
do
   nohup python parse.py -c $category > parse_all.log &
done