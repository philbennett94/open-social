import json, os, sys, unittest
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from open_social.open_social import OpenSocial 

class OpenSocialTests(unittest.TestCase):

	def setUp(self):
		abspath = os.path.abspath(__file__)
		dname = os.path.dirname(abspath)
		os.chdir(dname)
		slash = "\\" if "win" in sys.platform else "/"
		with open("..{slash}open_social{slash}credentials{slash}info.json".format(slash=slash), "r") as _:
			self.credentials = json.load(_)

	def test_open_social(self):
		m = OpenSocial()
		facebook = m.get_data(m.clients[0], "trump", 10, pages = ["cnn"])
		twitter = m.get_data(m.clients[1], "trump", 10)
		reddit = m.get_data(m.clients[2], "trump", 10, subReddits = ["worldnews", "news", "politics"])
		tumblr = m.get_data(m.clients[3], "trump", 10, blogs = ["cnnpolitics.tumblr.com"])
		instagram = m.get_data(m.clients[4], "trump", 10, relevantUsers = ["cnn"])
		m.to_file("facebook", "trump", facebook)
		m.to_file("instagram", "trump", instagram)
		m.to_file("twitter", "trump", twitter)
		m.to_file("reddit", "trump", reddit)
		m.to_file("tumblr", "trump", tumblr)

	def test_evaluate_all_clients(self):
		m = OpenSocial()
		options = {
			"pages": ["cnn"],
			"subReddits": ["worldnews", "news", "politics"],
			"blogs": ["cnnpolitics.tumblr.com"],
			"relevantUsers": ["cnn"]}
		data = m.evaluate_all_clients(
			searchTerm="trump", 
			limit=10, 
			kwargs=options)
		for platform in data.keys():
			assert (platform in ["facebook", "instagram", "tumblr", "twitter", "reddit"])

if __name__ == '__main__':
	unittest.main() 