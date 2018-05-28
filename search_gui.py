from collections import defaultdict
import json
from pymongo import MongoClient
from tkinter import *
import urllib
from bs4 import BeautifulSoup
import webbrowser

WEBPAGE_FOLDER = "../WEBPAGES_RAW"
BOOKKEPING_LOC = "../WEBPAGES_RAW/bookkeeping.json"

def get_tfidf( token_docInfo_pair : (str, dict) ):
	return token_docInfo_pair[1]["tf-idf"]
	
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

		label = Label(self._master, text="Query:")
		label.config(font=("Courier", 64))
		label.place(x=self._middle_width,y=self._middle_height, anchor="center")

		self._query_entry = Entry(self._master)
		self._query_entry.config(font=("Courier", 64))
		self._query_entry.place(x=self._middle_width,y=self._middle_height+120, anchor="center")

		search_button = Button(self._master, text='Search', command=self._create_results_page)
		search_button.config(font=("Courier", 50))
		search_button.place(x=self._middle_width-380,y=self._middle_height+240, anchor="center")
		
		quit_button = Button(self._master, text='Quit', command=self._master.quit)
		quit_button.config(font=("Courier", 50))
		quit_button.place(x=self._middle_width+420,y=self._middle_height+240, anchor="center")

	def _open_link(self, event):
		webbrowser.open_new(str(event.widget.cget("textvariable")))

	def _create_results_page(self):
		self._query_str = self._query_entry.get()

		for widget in self._master.winfo_children(): # Clear the window
			widget.destroy()

		title = Label(self._master, text="Top 10 Search Results For '{}':".format(self._query_str))
		title.grid(row=0, column=1, sticky="N")
		title.config(font=("Courier", 32))
		url_list = self._query(self._query_str.lower())

		currRow = 1
		for doc_id, url in url_list:
			number_label = Label(self._master, text=str(currRow) + ") ")
			number_label.grid(row=currRow, column=0, sticky="W")
			number_label.config(font=("Courier", 24))
			

			title = url
			# BS to get web page title
			html_id_info = doc_id.split("/") #stored in "folder/html_file" format
			file_name = "{}/{}/{}".format(WEBPAGE_FOLDER, html_id_info[0], html_id_info[1])
			html_file = open(file_name, 'r', encoding = 'utf-8')
			soup = BeautifulSoup(html_file, 'lxml')
			html_title = soup.title
			if (html_title != None and html_title.string != None):
				title = html_title.string.strip()			
			

			url_link = Label(self._master, text=title,
								textvariable="http://"+url,
								fg="blue", cursor="hand2")
			url_link.grid(row=currRow, column = 1, sticky = "W", columnspan = int(self._master.winfo_screenwidth()/2))
			url_link.config(font=("Courier", 24))
			currRow += 1

			url_link.bind("<Button-1>", self._open_link)

		if (url_list == []):
			error_label = Label(self._master, text="No results found.")
			error_label.grid(row=1, column=1)
			error_label.config(font=("Courier", 24))
			currRow += 1

		new_search_label = Button(self._master, text="Search again", command=self._create_query_page)
		new_search_label.grid(row=currRow, column=1, sticky="W")
		new_search_label.config(font=("Courier", 24))

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
		self._middle_height = int(self._master.winfo_screenheight()/2-50)
		self._middle_width = int(self._master.winfo_screenwidth()/2-50)
		self._create_query_page()

	def _query(self, query_str: str)->list:
				"""
				Returns a list of URLs that contain the given query (sorted) by tf-idf
				values.
				"""
				count_and_tfidf_of_docid = {} # Used to keep track of how many query terms a doc contains and its tfidf		
				result_list = [] #Used to store the urls to be returned at the end
				url_json = json.load(open(BOOKKEPING_LOC)) #Contains the key for the doc-ids to their urls
				split_query = query_str.split() #Splits the query into individual terms by space
				counter = 0
				
				for query in split_query: #iterate through query by splitting with space
					result = self._collection.find({"_id": query})
					if( result.count() < 1 ):
						continue; #No apperance of query term in inverted index
					token_dict = result.next() #Contains _Id : token_name and Doc_info : dict which contains all docids with token
					docs_dict = token_dict["Doc_info"]
					for docID, attributes in sorted(docs_dict.items(), key=get_tfidf, reverse=True): #Sorted list by tf-idf
						if( docID not in count_and_tfidf_of_docid.keys() ):
							count_and_tfidf_of_docid[docID] = ( 1, docs_dict[docID]["tf-idf"] ) #Firsty apperance of docID
						else:
							count_and_tfidf_of_docid[docID] = ( count_and_tfidf_of_docid[docID][0]+1,
																count_and_tfidf_of_docid[docID][1]+docs_dict[docID]["tf-idf"] )
						
				#return 10 top urls based upon query word count and then total tf-idf
				for docID, count_and_tf_idf in sorted(count_and_tfidf_of_docid.items(), key=lambda tuple: (tuple[1][0], tuple[1][1]), reverse=True):
					if( len(result_list) < 10 ):
						docID_url = url_json[docID]
						result_list.append((docID, docID_url))
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