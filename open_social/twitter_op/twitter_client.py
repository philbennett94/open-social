from ..common.social_error import SocialError
from twython import Twython
import datetime, json, sys, traceback 

class TwitterClient(object):

	"""
	Summary:
		The TwitterClient class wraps an instance of the twython.Twython class. This class facilitates
		searching the twitter rest api for data relevant to a search term.
	"""

	def __init__(self, app_key: str, app_secret: str, oauth_token: str, oauth_token_secret: str):

		"""
		Summary:
			Initializes an instance of TwitterClient

		Args:
			app_key: a valid twitter rest api application's application key
			app_secret: a valid twitter rest api application's application secret
			oauth_token: a valid twitter rest api application's oatuh token
			oauth_token_secret: a valid twitter rest api aplication's oatuh token secret

		Returns:
			An instance of the TwitterClient class
		"""
		self.twitter = Twython(
			app_key = app_key, 
			app_secret = app_secret, 
			oauth_token = oauth_token, 
			oauth_token_secret = oauth_token_secret)

	def search(self, searchTerm: str, limit: int = 10) -> list:
		"""
		Summary:
			Wraps twython's built in search functionality to gather data points from 
			the twitter rest api up to the limit. The search considers "popular" tweets
			as candidates to match the search term. Items are then parsed to extract relevant
			information.

		Args:
			searchTerm: the term to match against
			limit: the upper limit of results returned by the search

		Returns:
			A list of parsed data points.
		"""
		payload = []
		count = 0
		try:
			for entry in self.twitter.cursor(self.twitter.search, q=searchTerm, result_type="popular"):
				if(count == limit):
					break
				payload.append(self.parse(entry))
				count += 1
		except:
			etype, value, tb = sys.exc_info()
			error = SocialError(etype, value, tb)
			payload.append([{"error(s)": error.errorInfo}])
		finally:
			return payload

	def parse(self, response: dict) -> dict:
		"""
		Summary:
			Parses a single data point returned from the twitter rest api

		Args:
			response: a data point returned by the twitter rest api

		Returns:
			A parsed twitter rest api data point
		"""
		payload = {}
		payload["created_at"]           = response["created_at"]
		payload["id"]                   = response["id"]
		payload["text"]                 = response["text"]
		payload["user_id"]              = response["user"]["id"]
		payload["user_name"]            = response["user"]["name"]
		payload["user_screen_name"]     = response["user"]["screen_name"]
		payload["user_location"]        = response["user"]["location"]
		payload["user_description"]     = response["user"]["description"]
		payload["user_followers_count"] = response["user"]["followers_count"]
		payload["user_friends_count"]   = response["user"]["friends_count"]
		payload["user_timezone"]        = response["user"]["time_zone"]
		payload["user_statuses_count"]  = response["user"]["statuses_count"]
		payload["user_language"]        = response["user"]["lang"]
		payload["retweet_count"]        = response["retweet_count"]
		payload["favorite_count"]       = response["favorite_count"]
		try:
			payload["tweet_url"] = response["entities"]["urls"][0]["url"]
		except:
			payload["tweet_url"] = "no tweet url"
		return payload