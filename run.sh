#!/bin/bash
if [ ! -d "data" ];
then
    mkdir data;
else
    echo "folder data exists";
fi
if [ ! -d "data/raw/" ]
then
    mkdir data/raw/;
else
    echo "folder data/raw/ exists";
fi
nohup scrapy crawl bitcointalk > out.txt &
# scrapy crawl bitcointalk
