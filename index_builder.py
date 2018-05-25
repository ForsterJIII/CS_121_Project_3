from bs4 import BeautifulSoup
from collections import defaultdict
import json
import lxml
from pymongo import MongoClient
import re
import sys
import math

WEBPAGE_FOLDER = "/home/skayani-ubuntu/Desktop/cs121_projects/project3/WEBPAGES_RAW"

class IndexBuilder():

	def _setup_db(self, db_name, db_collection, keep_old_index):
		"""
		Connects to the MongoClient and initializes the collection
		"""
		self._db_host = MongoClient('localhost', 27017)
		self._db = self._db_host[db_name] # Name of the db being used
		self._collection = self._db[db_collection]; #Name of the collection in the db
		if( not keep_old_index ):
			self._collection.drop()
	
	def __init__(self, html_loc_json, db_name, db_collection, keep_old_index):
		self._corpus_json = html_loc_json # Name of the json file containing the corpus information
		self._total_documents = 0 # Total # of documents parsed
		self._tokens_map = defaultdict(int) # Maps tokens to number of documents with that token
		self._setup_db( db_name, db_collection, keep_old_index);

		# TODO: Feel free to rename
		self._index_dict = {}

	def _parse_html(self, text: str): #DOUBLE CHECK LATER TO SEE IF WE SHOULD BE RETURNING A DICT INSTEAD OF PASSING BY REFRENCE
		"""
		Creates the tokens dictionary from the HTML text (re-used from my
		Assignment 1 code.) Keys are tokens and values are the tokens'
		frequencies.
		"""
		tokens_dict = defaultdict(int)
		for token in re.findall(re.compile(r"[A-Za-z0-9]+"), text):
			tokens_dict[token.lower()] += 1
		return tokens_dict

	def insert_tfidf_values(self):
		for token_data in self._index_dict.values():
			for doc_id, term_freq in token_data["docIds"].items():
				token_data["docIds"][doc_id] = term_freq * math.log10(self._total_documents/len(token_data["docIds"]))

	def create_json_file(self):
		"""
		Creates the JSON file that will be used to load the index data in bulk.
		"""
		print("Creating json file...")
		json_list = []
		for token_data in self._index_dict.values():
			json_list.append(token_data)
		with open('index_data.json', 'w') as json_file:
			json.dump(json_list, json_file)
		print("Successfully created json file.")

	def create_index(self):
		"""
		Parses given corpus_json and creates an inverted index from its data
		"""
		corpus_data = json.load(open(self._corpus_json))

		for doc_id, url in corpus_data.items():
			html_id_info = doc_id.split("/")
			file_name = "{}/{}/{}".format(WEBPAGE_FOLDER, html_id_info[0], html_id_info[1])
			html_file = open(file_name, 'r', encoding = 'utf-8')
			soup = BeautifulSoup(html_file, 'lxml')

			# Create the tokens dict of given doc and iterate through
			# each token, updating the db.
			tokens_dict = self._parse_html(soup.get_text())

			self._total_documents += 1

			for (token, frequencies) in tokens_dict.items():
				token_exists = False
				if token in self._index_dict:
					token_exists = True
					self._index_dict[token]["docIds"][doc_id] = 1 + math.log10(frequencies)
				if (not token_exists):
					self._index_dict[token] = {"_id" : token, 
					"docIds" : {doc_id : 1 + math.log10(frequencies)}}

			# for (token, frequencies) in tokens_dict.items():
			# 	self._collection.find_one_and_update(
			# 		{"_id" : token}, 
			# 		{"$set" : {("docIds." + doc_id) : 0, 
			# 		("docIdCounts." + doc_id) : frequencies}}, 
			# 		upsert=True)

			print("Parsed {} documents so far".format(self._total_documents))

	def get_total_documents(self):
		"""
		Returns the total number of documents parsed
		"""
		return self._total_documents
		
	def get_total_tokens(self, tokens_dict: dict):
		"""
		Returns the total number of terms within a tokens dictionary.
		"""
		return self._collection.count()

if __name__ == "__main__":
	# try:
	index_builder = IndexBuilder("/home/skayani-ubuntu/Desktop/cs121_projects/project3/WEBPAGES_RAW/bookkeeping.json", "CS_121_db", "HTML_Corpus_Index", False)
	index_builder.create_index()
	index_builder.insert_tfidf_values()
	index_builder.create_json_file()
	# print("Completed index construction.\n Total documents parsed: {}".format( index_builder.get_total_documents() ))

	# except Exception as e:
	# 	print(e)
