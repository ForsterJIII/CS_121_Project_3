from bs4 import BeautifulSoup
from collections import defaultdict
from pymongo import MongoClient
import json
import pprint
import sys
import re
client = MongoClient('localhost', 27017)
db = client.cs121_db
db.posts.remove({"token":"Informatics"})
db.posts.insert_one({"token" : "Informatics",  "docIds" : ["docid1","docid2","docid3","docid4","docid5", "docid6","docid7","docid8","docid9","docid10", "docid11"]})
