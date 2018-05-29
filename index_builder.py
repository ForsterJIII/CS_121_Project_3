from bs4 import BeautifulSoup
from collections import defaultdict
import json
import lxml
import nltk
from nltk.corpus import stopwords
from pymongo import MongoClient
import re
import sys
import math
import time

#Only run once; Comment Out after
#nltk.download() #MUST INSTALL this before running nl tk

stop_words = set(stopwords.words('english')) #Words to skip when tokenzing a document
WEBPAGE_FOLDER = "WEBPAGES_RAW" #Folder contain all the documents to parse and the bookkeeping.json

class IndexBuilder():
	def _setup_db(self, db_name : str, db_collection, keep_old_index : bool):
		"""
		Connects to the MongoClient and initializes the collection
		"""
		self._db_host = MongoClient('localhost', 27017)
		self._db = self._db_host[db_name] # Name of the db being used
		self._collection = self._db[db_collection] #Name of the collection in the db
		if( not keep_old_index ): #Checks whether the user wants the database to reset or keep old data
			self._collection.drop()
	
	def __init__(self, html_loc_json, db_name : str, db_collection : str, keep_old_index : bool):
		self._corpus_json = html_loc_json # Name of the json file containing the corpus information
		self._total_documents = 0 # Total # of documents parsed
		self._inverted_index = defaultdict(dict) # A three-tiered dictionary (term->document->attributes) 
		self._setup_db( db_name, db_collection, keep_old_index)

	def _parse_html(self, text: str, tokens_dict: dict):
		"""
		Stores a tokens dictionary from the HTML text into tokens_dict (modified from my Assignment 1 code.) Keys are tokens and values are the tokens' frequencies.
		"""
		for token in re.findall(re.compile(r"[A-Za-z0-9]+"), text):
			if (token in stop_words): #Skip stop words
					continue
			tokens_dict[token.lower()] += 1
		return tokens_dict

	def update_db_scores(self):
		"""
		Updates the idf, tf-idf into every document's attributes;
		Should only be run on a finished inverted index
		"""
		print("Inserting DB Scores...")
		tfidf_start = time.time()
		for token_info in self._inverted_index.values():
			for doc_info in token_info["Doc_info"].values():
				doc_info["idf"] = self._total_documents / len(token_info["Doc_info"])
				doc_info["tf-idf"] = (1+math.log10(doc_info["tf"])) * math.log10(doc_info["idf"])
		print("Finished Updating DB Scores")
		print( "Updating DB Scores took: {} seconds".format( time.time() - tfidf_start ) )

	def insert_into_db(self):
		"""
		Inserts Inverted Index into the db
		"""
		print("Updating DB ...")
		db_insert_start = time.time()
		self._collection.insert_many( self._inverted_index.values() )
		print("Successfully Updated DB")
		print( "Inserting into the DB took: {} seconds".format( time.time() - db_insert_start ) )

	def create_index(self):
		"""
		Parses given corpus_json and creates an inverted index from its data
		"""
		corpus_data = json.load(open(self._corpus_json))

		print("Starting to Parse Corpus")
		doc_parsing_start = time.time()
		for doc_id, url in corpus_data.items():
			if( self._total_documents > 5000 ): #FOR TESTING
				 break;
			html_id_info = doc_id.split("/") #stored in "folder/html_file" format
			file_name = "{}/{}/{}".format(WEBPAGE_FOLDER, html_id_info[0], html_id_info[1])
			html_file = open(file_name, 'r', encoding = 'utf-8')
			soup = BeautifulSoup(html_file, 'lxml')

			# Create the tokens dict of given doc and iterate through
			# each token, updating the db.
			tokens_dict = defaultdict(int)
			self._parse_html(soup.get_text(), tokens_dict)
			
			#Tags for changing posting's weight_multiplier
			doc_title_tag = soup.find("title") #Doc's title; Returns None when no title
			doc_h1_tag = soup.find("h1") # Doc's first h1 tag; Returns None when no h1 tags
			doc_h2_tag = soup.find("h2") # Doc's first h2 tag; Returns None when no h2 tags
			doc_h3_tag = soup.find("h3") # Doc's first h3 tag; Returns None when no h3 tags
			doc_h4_tag = soup.find("h4") # Doc's first h4 tag; Returns None when no h4 tags
			doc_h5_tag = soup.find("h5") # Doc's first h5 tag; Returns None when no h5 tags
			doc_h6_tag = soup.find("h6") # Doc's first h6 tag; Returns None when no h6 tags
								
			self._total_documents += 1
			for (token, frequencies) in tokens_dict.items():
				weight_multiplier = 1.0 #Default
				if( (doc_title_tag is not None) and (doc_title_tag.string is not None) and (token in doc_title_tag.string.lower()) ):
					weight_multiplier = weight_multiplier + 0.40
				if( token in url.lower() ):
					weight_multiplier = weight_multiplier + 0.35							
				if( (doc_h1_tag is not None) and (doc_h1_tag.string is not None) and (token in doc_h1_tag.string.lower()) ):
					weight_multiplier = weight_multiplier + 0.30
				if( (doc_h2_tag is not None) and (doc_h2_tag.string is not None) and (token in doc_h2_tag.string.lower()) ):
					weight_multiplier = weight_multiplier + 0.25
				if( (doc_h3_tag is not None) and (doc_h3_tag.string is not None) and (token in doc_h3_tag.string.lower()) ):
					weight_multiplier = weight_multiplier + 0.20
				if( (doc_h4_tag is not None) and (doc_h4_tag.string is not None) and (token in doc_h4_tag.string.lower()) ):
					weight_multiplier = weight_multiplier + 0.15
				if( (doc_h5_tag is not None) and (doc_h5_tag.string is not None) and (token in doc_h5_tag.string.lower()) ):
					weight_multiplier = weight_multiplier + 0.10
				if( (doc_h6_tag is not None) and (doc_h6_tag.string is not None) and (token in doc_h6_tag.string.lower()) ):
					weight_multiplier = weight_multiplier + 0.05

				if (token not in self._inverted_index):
					self._inverted_index[token] = {"_id" : token, "Doc_info" : defaultdict(dict) }
				self._inverted_index[token]["Doc_info"][doc_id]["tf"] = frequencies
				self._inverted_index[token]["Doc_info"][doc_id]["weight_multiplier"] = weight_multiplier

			print("Parsed {} documents so far".format(self._total_documents))
		print( "Corpus Parsing Took: {} minutes".format( (time.time() - doc_parsing_start)/60 ) )

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
	index_builder = IndexBuilder("WEBPAGES_RAW/bookkeeping.json", "CS121_Inverted_Index", "HTML_Corpus_Index", False)
	index_builder.create_index()
	index_builder.update_db_scores()
	index_builder.insert_into_db()
	# print("Completed index construction.\n Total documents parsed: {}".format( index_builder.get_total_documents() ))

	# except Exception as e:
	# 	print(e)
