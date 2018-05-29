from ..common.abstract_social_client import AbstractSocialClient
from ..common.utils import search
from facebook import GraphAPI
import json, requests

class FacebookClient(AbstractSocialClient):

	"""
	Summary:
		The FacebookClient class wraps an instance of the facebook.GraphAPI class. This class
		has built in support for common tasks like pagination and keyword matching to extract 
		relevant data points for the Facebook platform.
	"""
	
	def __init__(self, access_token: str):
		"""
		Summary:
			Creates an instance of FacebookClient

		Args:
			access_token: your facebook graph api access token

		Returns:
			An instance of the FacebookClient class
		"""
		self.facebook = GraphAPI(
			access_token = access_token)

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
		sourceId = self.facebook.get_object(sourceName)["id"]
		rawData = self.facebook.get_connections(sourceId, "posts", fields="permalink_url,message,name,id", limit=100)
		dataPage = rawData["data"] 
		nextPageLink = [rawData["paging"]["next"]]
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
			nextPageLink: a string linking to the next page of data
		"""
		rawData = requests.get(nextPageLink[0]).json()
		dataPage = rawData["data"]
		nextPageLink = [rawData["paging"]["next"]]
		return dataPage, nextPageLink

	def match(self, searchTerm: str, datum: dict) -> bool:

		"""
		Summary:
			Logic to filter relevant posts. If a post has one or more of the 
			json attributes used for checking it's validity, then we check to 
			see if the value of those json attributes contains the search term.

		Args:
			searchTerm: a word or phrase to search over
			datum: the data to be checked for relevance

		Returns:
			True if datum[<jsonAttributes>] contains searchTerm, else False
		"""
		searchTerm = searchTerm.lower()
		validFilter = datum.keys()
		jsonAttributes = ["message", "name"]
		validAttributes = [attribute for attribute in jsonAttributes if attribute in validFilter]
		for attribute in validAttributes:
			if searchTerm in datum[attribute].lower():
				return True
		return False

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
		datum = self.get_secondary_information(datum)
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
		datum["secondary_information"] = {}
		datum["secondary_information"].update({"comments" : self.facebook.get_connections(datum["id"], "comments")})
		return datum

	def search(self, searchTerm: str, sources: list, limit: int) -> list:
		return search(client=self, searchTerm=searchTerm, sources=sources, limit=limit)