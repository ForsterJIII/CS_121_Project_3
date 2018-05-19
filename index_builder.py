from bs4 import BeautifulSoup
from collections import defaultdict
from pymongo import MongoClient
import json
import pprint
import sys
import re

FOLDER = "WEBPAGES_RAW"

def get_total_tokens(tokens_dict):
	"""
	Returns the total number of terms within a tokens dictionary.
	"""
	total = 0
	for (token, frequencies) in tokens_dict.items():
		total += frequencies
	return total

def get_tokens_dict(text):
	"""
	Creates the tokens dictionary from the HTML text (re-used from my
	Assignment 1 code.) Keys are tokens and values are the tokens'
	frequencies.
	"""
	tokens_dict = defaultdict(int)
	for token in re.findall(re.compile(r"[A-Za-z0-9]+"), text):
		tokens_dict[token.lower()] += 1
	return tokens_dict

def parse_json(json_file):
	"""
	Parses bookkeeping.json to (eventually) add all tokens to an inverted
	index.
	"""
	client = MongoClient('localhost', 27017)
	db = client.cs121_db
	json_data = json.load(open(json_file))
	for doc_id, url in json_data.items():
		html_file_loc = doc_id.split("/")
		html_file = open(FOLDER + "/" + html_file_loc[0] + "/"
					+ html_file_loc[1])
		soup = BeautifulSoup(html_file, 'html.parser')
		tokens_dict = get_tokens_dict(soup.get_text())
		print("URL of page: " + url)
		print("Title of page: " + str(soup.title))
		print("Page text: " + str(soup.get_text()))
		print("Tokens: " + str(tokens_dict))
		print("Total tokens: " + str(get_total_tokens(tokens_dict)))
		# db.posts.update({"_id" : 10}, {"token" : []})
		db.posts.update({"_id" : 10}, {"$push" : {"token" : {"doc_id1" : "df-tf1"}}})
		break


if __name__ == "__main__":
	try:
		parse_json(sys.argv[1])
	except Exception as e:
		print(e)
