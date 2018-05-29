from . import instagram_login_helper
from ..common.abstract_social_client import AbstractSocialClient
from ..common.utils import search
import codecs, json, os, requests

class InstagramClient(AbstractSocialClient):

	"""
	Summary:
		The InstagramClient class wraps an instance of the instagram_private_api.Client class. 
		This class has built in support for common tasks like pagination and keyword matching 
		to extract relevant data points for the Instagram platform.
	"""

	def __init__(self, username: str, password: str, settings: dict = None):
		"""
		Summary: 
			Initializes an instance of the InstagramClient. The current working directory
			is switched so that the file can locate supporting modules in the same diectory
			given relative paths. The path is restored after the client is created.

		Args:
			username: your instagram username
			password: your instagram password
			settings: (optional) settings that override the client cache. See documentation for instagram private api.

		Returns:
			An instance of the InstagramClient class
		"""
		currpath = os.getcwd()
		abspath = os.path.abspath(__file__)
		dname = os.path.dirname(abspath)
		os.chdir(dname)
		self.instagram = instagram_login_helper.generate_client_from_cache(
			username = username, 
			password = password)
		os.chdir(currpath)

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
		sourceId = self.instagram.username_info(sourceName)["user"]["pk"]
		rawData = self.instagram.user_feed(sourceId)
		dataPage = rawData["items"] 
		nextPageLink = [sourceId, rawData["next_max_id"]]
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
		rawData      = self.instagram.user_feed(nextPageLink[0], max_id=nextPageLink[1])
		dataPage     = rawData["items"]
		nextPageLink = [nextPageLink[0], rawData["next_max_id"]]
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
		searchTerm      = searchTerm.lower()
		validFilter     = datum["caption"].keys()
		jsonAttributes  = ["text"]
		validAttributes = [attribute for attribute in jsonAttributes if attribute in validFilter]
		for attribute in validAttributes:
			if searchTerm in datum["caption"][attribute].lower():
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
		parsedDatum = {
			"id": datum["id"],
			"media_id": datum["caption"]["media_id"],
			"caption": datum["caption"]["text"],
			"date": datum["taken_at"],
			"like_count": datum["like_count"],
			"comment_count": datum["comment_count"],
			"pkId": datum["pk"] 
		}
		try:
			parsedDatum["location"] = datum["location"]
		except:
			pass
		parsedDatum = self.get_secondary_information(parsedDatum)
		return parsedDatum

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
		comments   = []
		firstPage  = self.instagram.media_comments(datum["media_id"])
		for comment in firstPage["comments"]:
			comments.append({
				"id": comment["pk"],
				"text": comment["text"],
				"time": comment["created_at"],
				"owner_id": comment["user"]["pk"],
				"owner_username": comment["user"]["username"],
				"full_name": comment["user"]["full_name"]
			})
		datum["secondary_information"].update({"comments": comments})
		return datum

	def search(self, searchTerm: str, sources: list, limit: int):
		return search(client=self, searchTerm=searchTerm, sources=sources, limit=limit)