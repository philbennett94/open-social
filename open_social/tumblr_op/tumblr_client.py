from ..common.abstract_social_client import AbstractSocialClient
from ..common.utils import search
from pytumblr import TumblrRestClient

class TumblrClient(AbstractSocialClient):

	"""
	Summary:
		The TumblrClient class wraps an instance of the pytumblr.TumblrRestClient class. This class
		has built in support for common tasks like pagination and keyword matching to extract 
		relevant data points for the Tumblr platform.
	"""

	def __init__(self, consumer_key: str, consumer_secret: str, oauth_token: str, oauth_secret: str):
		"""
		Summary:
			Initializes and instance of TumblrClient

		Args:
			consumer_key: a valid tumblr rest api application's consumer key
			consumer_secret: a valid tumblr rest api application's consumer secret
			oauth_token: a valid tumblr rest api application's oauth token
			oauth_secret: a valid tumblr rest api application's oauth_secret

		Returns:
			An instance of the TumblrClient class
		"""
		self.tumblr = TumblrRestClient(
			consumer_key = consumer_key,
			consumer_secret = consumer_secret,
			oauth_token = oauth_token,
			oauth_secret = oauth_secret
		)

	def get_page(self, sourceName: str) -> (list, list):

		"""
		Summary:
			Gets the first page of results and a link to the next page of results 
			for a top level page attribute of facebook. 

		Args:
			sourceName: the name of the social media page to be searched for data

		Returns:
			dataPage: a list of individual data points taken from the api response
			nextPageLink: a list with info needed to link to the next page of data
		"""
		rawData = self.tumblr.posts(sourceName, limit=50, offset=0, notes_info=True)
		dataPage = rawData['posts']
		nextPageLink = [sourceName, 50]
		return dataPage, nextPageLink

	def update_page(self, nextPageLink: list) -> (list, list):

		"""
		Summary:
			Updates the current data page to provide new data in the executing loop 
			(search). Gets a list of data results and a link to the next page of data.

		Args:
			nextPageLink: a link to the next page of data results

		Returns:
			dataPage: a list of individual data points taken from the api response
			nextPageLink: a list with info needed to link to the next page of data
		"""
		rawData = self.tumblr.posts(nextPageLink[0], limit=50, offset=nextPageLink[1], notes_info=True)
		dataPage = rawData['posts']
		nextPageLink = [nextPageLink[0], nextPageLink[1] + 50]
		return dataPage, nextPageLink

	def match(self, searchTerm: str, datum: dict) -> bool:

		"""
		Summary:
			Gathers any secondary information that is relevant to the 
			social data point and updates the data point with that 
			information.

		Args:
			datum: the data point to be updated with secondary information

		Returns:
			datum: the data point updated with secondary information
		"""
		searchTerm = searchTerm.lower()
		validFilter = datum.keys()
		jsonAttributes = ["summary"]
		validAttributes = [attribute for attribute in jsonAttributes if attribute in validFilter]
		for attribute in validAttributes:
			if searchTerm in datum[attribute].lower():
				return True
		return False
		pass

	def parse(self, datum: dict) -> dict:

		"""
		Summary: 
			Used to parse api response and add any additional data that is
			relevant to the response.

		Args: 
			datum: the datapoint to be parsed and updated
		
		Returns:
			datum: the parsed data dictionary with secondary information added
		"""
		datum = {
			"type": datum["type"],
			"blog_name": datum["blog_name"],
			"id": datum["id"],
			"date": datum["date"],
			"post_url": datum["post_url"],
			"summary": datum["summary"],
			"note_count": datum["note_count"],
			"notes": datum["notes"]

		}
		return datum

	def get_secondary_information(self, datum: dict) -> dict:

		"""
		Summary:
			Gathers any secondary information that is relevant to the 
			social data point and updates the data point with that 
			information.

		Args:
			datum: the data point to be updated with secondary information

		Returns:
			datum: the data point updated with secondary information
		"""
		pass

	def search(self, searchTerm: str, sources: list, limit: int) -> list:
		return search(client=self, searchTerm=searchTerm, sources=sources, limit=limit)