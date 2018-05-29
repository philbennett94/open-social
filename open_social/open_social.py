from .common.social_error import SocialError 
from .facebook_op.facebook_client import FacebookClient 
from .instagram_op.instagram_client import InstagramClient 
from .reddit_op.reddit_client import RedditClient
from .tumblr_op.tumblr_client import TumblrClient
from .twitter_op.twitter_client import TwitterClient 
from datetime import datetime
import concurrent.futures, json, logging, os, sys, time, traceback  

class OpenSocial(object):
	
	"""
	Summary:
		Primary driver class for the open-social library. This class facilitates subclient
		generation, containment, and command execution so that data can be gathered from each social
		media platform with ease. 
	"""
	
	def __init__(self, clients: str = ["facebook","twitter","reddit","tumblr","instagram"]):
		"""
		Summary:
			Initializes the OpenSocial class

		Args:
			clients: (optional) a list of strings where each element is the name of a social
			media platform. Valid element values: "facebook","twitter","reddit","tumblr","instagram"

		Returns:
			An instance of the OpenSocial class
		"""
		currpath = os.getcwd()
		abspath = os.path.abspath(__file__)
		dname = os.path.dirname(abspath)
		os.chdir(dname)
		self.slash = "\\" if "win" in sys.platform else "/"
		with open("credentials{slash}info.json".format(slash=self.slash), "r") as file:
			self.credentials = json.load(file)
		self.clients = [self.create_client(client) for client in clients]
		del self.credentials
		os.chdir(currpath)

	def create_client(self, clientFlag: str) -> object:
		"""
		Summary:
			Factory function for all client types. Given a valid clientFlag, this function will
			return an instance of the client class associated with the social media platform defined
			by clientFlag.

		Args:
			clientFlag: the name of a social media platform supported by open-social. Valid
			flags are: "facebook","twitter","reddit","tumblr","instagram"

		Returns:
			An instance of the client associated with the social media platform defined by clientFlag 
		"""
		try:
			if clientFlag == "facebook":
				return FacebookClient(
					access_token=self.credentials["facebook"]["access_token"])
			elif clientFlag == "instagram":
				return InstagramClient(
					username=self.credentials["instagram"]["username"],
					password=self.credentials["instagram"]["password"])
			elif clientFlag == "twitter":
				return TwitterClient(
					app_key=self.credentials["twitter"]["app_key"],
					app_secret=self.credentials["twitter"]["app_secret"],
					oauth_token=self.credentials["twitter"]["oauth_token"],
					oauth_token_secret=self.credentials["twitter"]["oauth_token_secret"])
			elif clientFlag == "reddit":
				return RedditClient(
					client_id=self.credentials["reddit"]["client_id"],
					client_secret=self.credentials["reddit"]["client_secret"],
					user_agent=self.credentials["reddit"]["user_agent"])
			elif clientFlag == "tumblr":
				return TumblrClient(
					consumer_key=self.credentials["tumblr"]["consumer_key"],
					consumer_secret=self.credentials["tumblr"]["consumer_secret"],
					oauth_token=self.credentials["tumblr"]["oauth_token"],
					oauth_secret=self.credentials["tumblr"]["oauth_secret"])
			else:
				print("The platform code: {clientFlag}, is not a valid platform code. \
					Please enter one of the following platform codes: facebook, twitter, \
					reddit, tumblr, instagram.".format(clientFlag=clientFlag))
		except Exception as e:
			raise e
			etype, value, tb = sys.exc_info()
			error = SocialError()
			error.add_error(etype, value, tb)
			logging.warn(
				"The {clientFlag} client was not created...\nDETAILS: {details}".format(
					clientFlag=clientFlag,
					details=str(error)))

	def get_data(self, client: object, searchTerm: str, limit: int, **kwargs) -> dict:
		"""
		Summary:
			Runs the search function related to a given social media client object.

		Args:
			client: an instance of FacebookClient, InstagramClient, RedditClient, TumblrClient, or
					TwitterClient.
			searchTerm: the search term to match data points against. If a datapoint's
						primary text description field (post body, caption text, post title)
						contains the search term, then the datapoint will be included in
						the results.
			limit: the upper limit for the number of search results returned
			kwargs:
				- pages: names of public facebook pages to include in your search
				- relevantUsers: names of instagram users to include in your search
				- subReddits: names of subreddits to include in your search
				- blogs: names of tumblr blogs to include in your search

		Returns:
			A dict of parsed search results from the social media platform related to the 
			client type given as client. None is returned if the client type is sunsupported.
			dict -> {source: [data]}
		"""
		kwargs = kwargs["kwargs"] if "kwargs" in kwargs.keys() else kwargs
		if isinstance(client, FacebookClient):
			print("@Starting Facebook Search...")
			print("START TIME: ", str(time.time()))
			payload = self.search_facebook(client, searchTerm, pages=kwargs["pages"], limit=limit)
			print("END TIME: ", str(time.time()))
			return payload
		elif isinstance(client, InstagramClient):
			print("@Starting Instagram Search...")
			print("START TIME: ", str(time.time()))
			payload = self.search_instagram(client, searchTerm, relevantUsers=kwargs["relevantUsers"], limit=limit)
			print("END TIME: ", str(time.time()))
			return payload
		elif isinstance(client, TwitterClient):
			print("@Starting Twitter Search...")
			print("START TIME: ", str(time.time()))
			payload = self.search_twitter(client, searchTerm, limit)
			print("END TIME: ", str(time.time()))
			return payload
		elif isinstance(client, RedditClient):
			print("@Starting Reddit Search...")
			print("START TIME: ", str(time.time()))
			payload = self.search_reddit(client, searchTerm, subReddits=kwargs["subReddits"], limit=limit)
			print("END TIME: ", str(time.time()))
			return payload
		elif isinstance(client, TumblrClient):
			print("@Starting Tumblr Search...")
			print("START TIME: ", str(time.time()))
			payload = self.search_tumblr(client, searchTerm, blogs=kwargs["blogs"], limit=limit)
			print("END TIME: ", str(time.time()))
			return payload
		else:
			print("Unsupported client type...")

	def evaluate_all_clients(self, searchTerm: str, limit: int, **kwargs) -> dict:
		"""
		Summary:
			*|* This is a temporary work around until serialization issues for *|*
			*|* the multiprocessing library are worked out.                    *|*

			Executes a search on all available clients contained in self.clients. You
			must define all possible key word arguments for all client types in **kwargs.

		Args:
			searchTerm: the term to filter data on
			limit: the upper limit for the number of datapoints returned by the search
			kwargs:
				- pages: names of public facebook pages to include in your search
				- relevantUsers: names of instagram users to include in your search
				- subReddits: names of subreddits to include in your search
				- blogs: names of tumblr blogs to include in your search

		Returns:
			A dictionary containing search results for all clients. The keys of this dictionary
			consist of 
		"""
		results = {}
		workerSize = len(self.clients)
		with concurrent.futures.ThreadPoolExecutor(max_workers=workerSize) as executor:
			future_set = {executor.submit(self.get_data, client, searchTerm, limit, kwargs=kwargs["kwargs"]): client for client in self.clients}
			for future in concurrent.futures.as_completed(future_set):
				try:
					data = future.result()
					results.update(data)
				except Exception as e:
					print("Error during search: {error!s}".format({"error": str(e)}))
		return results

	def search_facebook(self, client: object, searchTerm: str, pages: list, limit: int) -> dict:
		"""
		Summary:
			Executes a search on public facebook pages. Loops through results and extracts
			datapoints whose top level text field matches the search term.

		Args:
			client: and instance of FacebookClient
			searchTerm: the term to filter data on
			pages: a list of names of public pages on facebook
			limit: the upper limit for the number of datapoints returned by the search

		Returns:
			A dictionary of processed datapoints from public facebook pages.
			dict -> {source: [data]}
		"""
		try:
			return {"facebook": client.search(searchTerm, pages, limit)}
		except Exception as e:
			print("Could not complete facebook search...")
			print("ERROR: {error!s}".format({"error": str(e)}))

	def search_instagram(self, client: object, searchTerm: str, relevantUsers: list, limit: int) -> dict:
		"""
		Summary:
			Executes a search on public instagram profiles. Loops through results and extracts
			datapoints whose top level text field matches the search term.

		Args:
			client: and instance of InstagramClient
			searchTerm: the term to filter data on
			relevantUsers: a list of names of public profiles on Instagram
			limit: the upper limit for the number of datapoints returned by the search

		Returns:
			A dictionary of processed datapoints from public instagram profiles.
			dict -> {source: [data]}
		"""
		try:
			return {"instagram": client.search(searchTerm, relevantUsers, limit)}
		except Exception as e:
			print("Could not complete instagram search...")
			print("ERROR: {error!s}".format({"error": str(e)}))

	def search_twitter(self, client: object, searchTerm: str, limit: int) -> dict:
		"""
		Summary:
			Executes a search on "popular" tweets. Filters tweets based on the search term
			provided as an argument.

		Args:
			client: an instance of TwitterClient
			searchTerm: the term to filter data on
			limit: the upper limit for the number of datapoints returned by the search

		Returns:
			A dictionary of processed datapoints from twitter's "popular" tweet dataset.
			dict -> {source: [data]}
		"""
		try:
			return {"twitter": client.search(searchTerm, limit)}
		except Exception as e:
			print("Could not complete twitter search...")
			print("ERROR: {error!s}".format({"error": str(e)}))

	def search_reddit(self, client: object, searchTerm: str, subReddits: list, limit: int) -> dict:
		"""
		Summary:
			Executes a search on posts in subreddits defined in subReddits. Filters tweets based on 
			the search term provided as an argument. 

		Args:
			client: and instance of RedditClient
			searchTerm: the term to filter data on
			subReddits: a list of names of subreddits
			limit: the upper limit for the number of datapoints returned by the search

		Returns:
			A dictionary of processed datapoints from subreddits.
			dict -> {source: [data]}
		"""
		try:
			return {"reddit": client.search(searchTerm, subReddits, limit)}
		except Exception as e:
			print("Could not complete reddit search...")
			print("ERROR: {error!s}".format({"error": str(e)}))

	def search_tumblr(self, client: object, searchTerm: str, blogs: list, limit: int) -> dict:
		"""
		Summary:
			Executes a search on public tumblr blogs. Loops through results and extracts
			datapoints whose top level text field matches the search term.

		Args:
			client: and instance of TumblrClient
			searchTerm: the term to filter data on
			blogs: a list of names of public blogs
			limit: the upper limit for the number of datapoints returned by the search

		Returns:
			A dict of processed datapoints from blogs.
			dict -> {source: [data]}
		"""
		try:
			return {"tumblr": client.search(searchTerm, blogs, limit)}
		except Exception as e:
			print("Could not complete twitter search...")
			print("ERROR: {error!s}".format({"error": str(e)}))

	def to_file(self, source: str, searchTerm: str, data: list):
		"""
		Summary:
			Dumps a list of datapoints returned from search functions. This function will
			write out any python object compatible with json.dumps to a file. The arguments
			for this function can be anything, but it is best used if you follow the guidelines
			set in the Args section below.

		Args:
			source: the social media platform code related to the data to
					be dumped to the file.
			searchTerm: the search term that was used to filter the data
			data: a list of search results

		Returns:
			None
		"""
		currpath = os.getcwd()
		abspath = os.path.abspath(__file__)
		dname = os.path.dirname(abspath)
		os.chdir(dname)
		fileName = "data{slash}{source}_{searchTerm}_{time}.json".format(
			slash=self.slash, 
			source=source, 
			searchTerm=searchTerm, 
			time=datetime
				.now()
				.strftime("%Y-%m-%d_%H-%M-%S"))
		with open(fileName, "w") as file:
			json.dump({"data": data}, file)
		os.chdir(currpath)