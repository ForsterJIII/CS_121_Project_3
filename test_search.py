from bs4 import BeautifulSoup
from collections import defaultdict
from pymongo import MongoClient
import json
import pprint
import sys
import re

client = MongoClient('localhost', 27017)
db = client.cs121_db
index = db.index

BOOKKEPING_LOC = "../WEBPAGES_RAW/bookkeeping.json"
f = open("query_results.txt", "w+")

def test_query(query):
    try:
        query = query.lower()
        count = 0
        result = index.find({"_id": query})
        token_value = result.next()
        f.write("For query '{}'\n".format(query))
        for ids in token_value["docIds"]:
            if(count == 10):
                break
            
            json_data = json.load(open(BOOKKEPING_LOC))
            f.write(json_data[ids] + '\n')
            count += 1
            f.write('\n')

        f.write('\n')
        f.write('\n')
        f.write('\n')
        f.write('\n')
    except StopIteration:
        print("Not in inverted index")

test_query("Informatics")
test_query("Mondego")
test_query("Irvine")
f.close()