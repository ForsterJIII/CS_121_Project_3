from bs4 import BeautifulSoup
from collections import defaultdict
from pymongo import MongoClient
import json
import pprint
import sys
import re

client = MongoClient('localhost', 27017)
db = client.cs121_db

def test_query(query):
    try:
        count = 0
        result = db.posts.find({"token": query})
        token_value = result.next()
        print(token_value)
        for ids in token_value["docIds"]:
            if(count == 10):
                break
            print(ids)
    except StopIteration:
        print("Not in inverted index")

test_query("Informatics")
test_query("Mondego")
test_query("Irvine")
