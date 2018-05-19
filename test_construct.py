from bs4 import BeautifulSoup
from collections import defaultdict
from pymongo import MongoClient
import json
import pprint
import sys
import re
client = MongoClient('localhost', 27017)
db = client.cs121_db

db.posts.insert_one({"token" : "tokenStr",  "docIds" : "hi"})
