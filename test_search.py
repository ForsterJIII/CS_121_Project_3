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
    count = 0
    for post in db.employees.find({"token": query}):
        if(count == 10):
            break
        print(post.keys())
        print(post['token'])
        #for value in post:
            #print(value)
test_query("Informatics")
test_query("Mondego")
test_query("Irvine")
