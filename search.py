from pymongo import MongoClient
import json

BOOKKEPING_LOC = "../Project_3/WEBPAGES_RAW/bookkeeping.json"

def get_tfidf( key_value_tuple ):
	return key_value_tuple[1]["tf-idf"]

class Search:
	def _setup_db(self, db_name, db_collection):
		"""
		Connects to the MongoClient and initializes the collection
		"""
		self._db_host = MongoClient('localhost', 27017)
		self._db = self._db_host[db_name] # Name of the db being used
		self._collection = self._db[db_collection] #Name of the collection in the db


	def __init__(self, db_name, db_collection):
		self._setup_db(db_name, db_collection)

	def query(self, query_str: str)->list:
		"""
		Returns a list of URLs that contain the given query (sorted) by tf-idf
		values.
		"""
		urls_list = []
		json_data = json.load(open(BOOKKEPING_LOC))
		result = self._collection.find({"_id": query_str})
		token_value = result.next()
		docs_dict = token_value["Doc_info"]

		results_count = 0
		for doc_id, attributes in sorted(docs_dict.items(), key=get_tfidf, reverse=True):
			urls_list.append((json_data[doc_id], docs_dict[doc_id]["tf-idf"]))

			results_count += 1
			if (results_count == 10):
				break

		return urls_list


	def print_query_result(self, urls_list: list):
		"""
		Prints a user-friendly list of URLs.
		"""
		print("Search result:")
		url_ranking = 1
		for url, tf_idf in urls_list:
			print("{}) {} ({:.2f})".format(url_ranking, url, tf_idf))
			url_ranking += 1


if __name__ == "__main__":
	print("Starting search program...")
	search_program = Search("CS121_Inverted_Index", "HTML_Corpus_Index")
	while True:
		user_input = input("Enter a query to search or 'quit' to exit: ")
		if (user_input == "quit"):
			break
		urls_list = search_program.query(user_input.lower())
		search_program.print_query_result(urls_list)

	print("Bye")
	