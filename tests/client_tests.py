import json, os, sys, unittest
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from open_social.facebook_op.facebook_client import FacebookClient
from open_social.instagram_op.instagram_client import InstagramClient 
from open_social.reddit_op.reddit_client import RedditClient 
from open_social.tumblr_op.tumblr_client import TumblrClient 
from open_social.twitter_op.twitter_client import TwitterClient 
import open_social.instagram_op.instagram_login_helper

class ClientTests(unittest.TestCase):

	def setUp(self):
		abspath = os.path.abspath(__file__)
		dname = os.path.dirname(abspath)
		os.chdir(dname)
		slash = "\\" if "win" in sys.platform else "/"
		with open("..{slash}open_social{slash}credentials{slash}info.json".format(slash=slash), "r") as _:
			self.credentials = json.load(_)

	def test_facebook_client(self):
		accessToken = self.credentials["facebook"]["access_token"]
		facebookClient = FacebookClient(access_token = accessToken)
		data = facebookClient.search("trump", ["cnn"], 10)
		assert (len(data) > 0 and len(data) <= 10)

	def test_instagram_client(self):
		username = self.credentials["instagram"]["username"]
		password = self.credentials["instagram"]["password"]
		instagramClient = InstagramClient(username = username, password = password)
		data = instagramClient.search("the", ["kingjames"], 10)
		assert (len(data) > 0 and len(data) <= 10)

	def test_reddit_client(self):
		clientId = self.credentials["reddit"]["client_id"]
		clientSecret = self.credentials["reddit"]["client_secret"]
		userAgent = self.credentials["reddit"]["user_agent"]
		redditClient = RedditClient(client_id = clientId, client_secret = clientSecret, user_agent = userAgent)
		data = redditClient.search("trump", ["worldnews", "news", "politics"])
		assert (len(data) > 0 and len(data) <= 10)

	def test_tumblr_client(self):
		consumerKey = self.credentials["tumblr"]["consumer_key"]
		consumerSecret = self.credentials["tumblr"]["consumer_secret"]
		oauthToken = self.credentials["tumblr"]["oauth_token"]
		oauthSecret = self.credentials["tumblr"]["oauth_secret"]
		tumblrClient = TumblrClient(consumer_key = consumerKey, consumer_secret = consumerSecret, oauth_token = oauthToken, oauth_secret = oauthSecret)
		data = tumblrClient.search("trump", ["cnnpolitics.tumblr.com"], 10)
		assert (len(data) > 0 and len(data) <= 10)

	def test_twitter_client(self):
		appKey = self.credentials["twitter"]["app_key"]
		appSecret = self.credentials["twitter"]["app_secret"]
		oauthToken = self.credentials["twitter"]["oauth_token"]
		oauthTokenSecret = self.credentials["twitter"]["oauth_token_secret"]
		twitterClient = TwitterClient(app_key = appKey, app_secret = appSecret, oauth_token = oauthToken, oauth_token_secret = oauthTokenSecret)
		data = twitterClient.search("trump")
		assert (len(data) > 0 and len(data) <= 10)

if __name__ == '__main__':
	unittest.main()