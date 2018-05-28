from pymongo import MongoClient
import json

BOOKKEPING_LOC = "WEBPAGES_RAW/bookkeeping.json"

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
                url_dict = {} #stores data of end urls                
                urls_tf_idf_total = {}#used to keep track of tf.idf for the queries
                result_list = [] #used to store the results
                json_data = json.load(open(BOOKKEPING_LOC))
                split_query = query_str.split()
                counter = 0
                for query in split_query: #iterate through query by splitting with space
                    result = self._collection.find({"_id": query})
                    try:
                        token_value = result.next()
                        docs_dict = token_value["Doc_info"]
                        results_count = 0 #potentially have to take out if want all queries for selecting
                        for doc_id, attributes in sorted(docs_dict.items(), key=get_tfidf, reverse=True):
                                #keeping track of updates. those with more updates = matched more queries = higher priority
                                #even if lower tf.idf
                                if(json_data[doc_id] in urls_tf_idf_total):
                                    urls_tf_idf_total[json_data[doc_id]][0] += 1
                                    urls_tf_idf_total[json_data[doc_id]][1] += docs_dict[doc_id]["tf-idf"]
                                else:
                                    urls_tf_idf_total[json_data[doc_id]] = [1,docs_dict[doc_id]["tf-idf"]]
                                results_count += 1
                                if (results_count == 10):
                                        break
                    except StopIteration:#could not find query
                        pass
                #search for urls that match the most words and continues until 10 queries are reached
                #or if there are no more urls to retrieve
                counter = len(split_query)
                while(1):
                        if(len(url_dict) >= 10 or counter == 0): 
                                break
                        for url,tf_idf in list(urls_tf_idf_total.items()):#list part necessary in python3
                            if( tf_idf[0] == counter): #iterates through ALL the words matching. Stopping prematurely
                                    #will result in queries being missed before moving to the next best match.
                                url_dict[url] = tf_idf
                        counter -= 1 #used to keep track of how many queries are matching.
                        #higher priority towards queries with more words matching
                #return urls sorted by tf_idf
                sorted_values = sorted(url_dict.items(),  key=lambda x: (x[1][0],x[1][1]), reverse = True)
                #return 10 top urls from sorted_values
                for url,tf_idf in sorted_values:
                        if(len(result_list) < 10):
                                result_list.append((url,tf_idf))
                        else:
                                break
                return result_list
       

	def print_query_result(self, urls_list: list):
		"""
		Prints a user-friendly list of URLs.
		"""
		print("Search result:")
		url_ranking = 1
		for url, tf_idf in urls_list:
			print("{}) {} {} {}".format(url_ranking, url, tf_idf[0],tf_idf[1]))
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
	
