from pymongo import MongoClient
from tkinter import *
import webbrowser
import json

BOOKKEPING_LOC = "../WEBPAGES_RAW/bookkeeping.json"

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

	def _clear_window(self):
		for widget in self._master.winfo_children():
			widget.destroy()

	def _create_query_page(self):
		self._clear_window()

		label = Label(self._master, text="Query")
		label.grid(row=0)
		label.config(font=("Courier", 18))

		self._query_entry = Entry(self._master)
		self._query_entry.grid(row=0, column=1)

		Button(self._master, text='Search', command=self._create_results_page).grid(row=3, column=0, sticky=W, pady=4)
		Button(self._master, text='Quit', command=self._master.quit).grid(row=3, column=1, sticky=W, pady=4)

	def _open_link(self, event):
		webbrowser.open_new(event.widget.cget("text"))

	def _create_results_page(self):
		self._query_str = self._query_entry.get()

		for widget in self._master.winfo_children(): # Clear the window
			widget.destroy()

		title = Label(self._master, text="Search results:")
		title.grid(row=0, column=1, sticky="N")
		title.config(font=("Courier", 18))
		url_list = self._query(self._query_str.lower())

		currRow = 1
		for url, tfidf in url_list:
			number_label = Label(self._master, text=str(currRow) + ") ")
			number_label.grid(row=currRow, column=0, sticky="W")
			number_label.config(font=("Courier", 18))

			url_link = Label(self._master, text="http://" + url,
								fg="blue", cursor="hand2")
			url_link.grid(row=currRow, column = 1, sticky = "W")
			url_link.config(font=("Courier", 18))
			currRow += 1

			url_link.bind("<Button-1>", self._open_link)

		new_search_label = Button(self._master, text="Search again", command=self._create_query_page)
		new_search_label.grid(row=currRow, column=5, sticky="W")

	def __init__(self, db_name, db_collection):
		self._setup_db(db_name, db_collection)
		self._master = Tk()
		screen_height = self._master.winfo_screenheight()
		screen_width = self._master.winfo_screenwidth()
		self._master.geometry("{}x{}".format(str(self._master.winfo_screenwidth()-100), 
								str(self._master.winfo_screenheight()-100)))
		self._master.resizable(0, 0)
		self._query_entry = None
		self._query_str = None
		self._create_query_page()

	def _query(self, query_str: str)->list:
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


	mainloop( )


	# while True:
	# 	user_input = input("Enter a query to search or 'quit' to exit: ")
	# 	if (user_input == "quit"):
	# 		break
	# 	urls_list = search_program.query(user_input.lower())
	# 	search_program.print_query_result(urls_list)

	# print("Bye")