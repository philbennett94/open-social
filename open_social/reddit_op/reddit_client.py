from ..common.social_error import SocialError
from praw import Reddit
import datetime, json, sys, traceback  

class RedditClient(object):

	"""
	Summary:
		The RedditClient class wraps an instance of the praw.Reddit class. This class
		has built in support for common tasks like keyword matching to extract 
		relevant data points for the Reddit platform.
	"""
	
	def __init__(self, client_id: str, client_secret: str, user_agent: str):
		"""
		Summary:
			Creates an instance of RedditClient

		Args:
			client_id: a valid reddit application's client_id
			client_secret: a valid reddit application's client secret
			user_agent: a vaild reddit application's useragent

		Returns:
			An instance of the RedditClient class
		"""
		self.reddit = Reddit(
			client_id = client_id, 
			client_secret = client_secret, 
			user_agent = user_agent
		)

	def search(self, searchTerm: str, subreddits: list, limit: int = 10) -> list:
		"""
		Summary:
			Drives data extraction on the reddit platform. Loops through posts in 
			in user defined subreddits. Each post's title that contains the searchTerm
			is added to payload up to the count of limit. Each post is parsed to extract
			relevant data.

		Args:
			searchTerm: the string to match against post titles
			subreddits: the names of subreddits to extract data from. Data is extracted
						equally from each subreddit.
			limit: (optional) the total number of data points to extract. The real count of data
				   points returned from this function may be less than limit.

		Returns:
			payload: a list of parsed data points
		"""
		payload = []
		switch  = limit // len(subreddits)
		try:
			for subreddit in subreddits:
				count = 0
				submissionIds = self.reddit.subreddit(subreddit).search(searchTerm, limit=switch)
				for submissionId in submissionIds:
					entry = self.reddit.submission(id=submissionId)
					payload.append(self.parse(entry))
					count += 1
		except:
			etype, value, tb = sys.exc_info()
			error = SocialError(etype, value, tb)
			payload.append([{"error(s)": error.errorInfo}])
		finally:
			return payload

	def parse(self, response: object) -> dict:
		"""
		Summary: 
			Parses a reddit api response to extracgt relevant data. Praw responses
			are lazy, so this function evaluates the lazy response. The same
			proccess occurs for comments from the parent post. A parsed data point
			with comments is returned.
		
		Args:
			response: a reddit api response extracted using praw.

		Returns:
			payload: a parsed data point that includes relevant fields from the
					 api response and comment text.
		"""
		payload, redditor = {}, response.author
		payload["title"] = response.title
		payload["id"] = response.id
		payload["domain"] = response.domain
		payload["title"] = response.title
		payload["subreddit_id"] = response.subreddit_id 
		payload["subreddit_name"] = response.subreddit._path
		payload["user_screen_name"] = redditor.name
		payload["user_link_karma"] = redditor.link_karma
		payload["user_comment_karma"] = redditor.comment_karma
		payload["user_created_at"] = redditor.created_utc
		payload["permalink"] = response.permalink 
		payload["url"] = response.url
		payload["created_utc"] = response.created_utc
		payload["upvote_ratio"] = response.upvote_ratio
		payload["score"] = response.score
		payload["secondary_information"] = {"comments": []}
		for comment in self.reddit.submission(id=payload["id"]).comments:
			try:
				payload["secondary_information"]["comments"].append(
					{
						"body": comment.body, 
						"user_screen_name": comment.author.name
					})
			except:
				continue
		return payload