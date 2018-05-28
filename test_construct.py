from bs4 import BeautifulSoup
from collections import defaultdict
from pymongo import MongoClient
import json
import pprint
import sys
import re
client = MongoClient('localhost', 27017)
db = client.cs121_db
#remove this if you drop collection manually
db.posts.drop()
#should only take 10 values order affects query processing. e.g. 11th value will not show
db.posts.insert_one({"token" : "Informatics",  "docIds" : ["0/0","0/1","0/10","0/100","0/101","0/102","0/103","0/104","0/105", "0/106","0/107"]})
db.posts.insert_one({"token" : "Irvine",  "docIds" : ["0/108","0/109","0/11","0/110","0/111","0/112","0/113","0/114","0/115","0/116","0/117"]})
db.posts.insert_one({"token" : "Mondego",  "docIds" : ["0/118","0/119","0/12","0/120","0/121","0/122","0/123","0/124","0/125", "0/126","0/127"]})


    
