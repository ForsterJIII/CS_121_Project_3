from bs4 import BeautifulSoup
from collections import defaultdict
from pymongo import MongoClient
import json
import pprint
import sys
import re

FOLDER = "WEBPAGES_RAW"

class IndexBuilder():

	json_file = ""
	total_documents = 0

	# Maps tokens to number of documents with that token
	tokens_map = defaultdict(int)

	def __init__(self, json_file):
		self.json_file = json_file

	def get_total_tokens(self, tokens_dict: dict):
		"""
		Returns the total number of terms within a tokens dictionary.
		"""
		total = 0
		for (token, frequencies) in tokens_dict.items():
			total += frequencies
		return total

	def get_tokens_dict(self, text: str):
		"""
		Creates the tokens dictionary from the HTML text (re-used from my
		Assignment 1 code.) Keys are tokens and values are the tokens'
		frequencies.
		"""
		tokens_dict = defaultdict(int)
		for token in re.findall(re.compile(r"[A-Za-z0-9]+"), text):
			tokens_dict[token.lower()] += 1
		return tokens_dict


	def parse_json(self):
		"""
		Parses bookkeeping.json and creates a tokens dict.
		"""
		client = MongoClient('localhost', 27017)
		db = client.cs121_db

		# Index is the name of the collection in the db
		index = db.index

		json_data = json.load(open(self.json_file))


		for doc_id, url in json_data.items():
			html_file_loc = doc_id.split("/")
			html_file = open(FOLDER + "/" + html_file_loc[0] + "/"
						+ html_file_loc[1],'r','utf-8')
			soup = BeautifulSoup(html_file, 'html.parser')

			# Create the tokens dict of given doc and iterate through
			# each token, updating the db.
			tokens_dict = self.get_tokens_dict(soup.get_text())

			self.total_documents += 1

			for (token, frequencies) in tokens_dict.items():
				# cursor = index.find({"token" : token})
				# if (cursor.count() == 0):
				# 	index.insert({"token" : token, "docIds" : {doc_id : 0}, "docIdCounts" : {doc_id : frequencies}})
				# else:
				index.find_one_and_update(
					{"_id" : token}, 
					{"$set" : {("docIds." + doc_id) : 0, 
					("docIdCounts." + doc_id) : frequencies}}, 
					upsert=True)

			print("Parsed {} documents so far".format(self.total_documents))

			

	def build_index(self):
		client = MongoClient('localhost', 27017)
		db = client.cs121_db
		index = db.index

		# for (token_str, frequencies) in tokens_dict:
			# 	cursor = index.find("{{token : {}}}".format(token_str))
			# 	if (cursor.count == 0):
			# 		index.insertOne("{{token : {}, docIds : []}}")

			# cursor = index.find({"token" : "test_token"})
			# print(cursor.count())

			# db.posts.update({"_id" : 10}, {"token" : []})
			# db.posts.update({"_id" : 10}, {"$push" : {"token" : {"doc_id1" : "df-tf1"}}})

if __name__ == "__main__":
	try:
		index_builder = IndexBuilder(sys.argv[1])
		index_builder.parse_json()
		print("Completed index construction. " +
			"Total documents parsed: {}".format(index_builder.total_documents))

	except Exception as e:
		print(e)
