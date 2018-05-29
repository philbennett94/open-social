# open-social
	                                              _       _ 
	                                             (_)     | |
	   ___  _ __   ___ _ __ ______ ___  ___   ___ _  __ _| |
	  / _ \| '_ \ / _ \ '_ \______/ __|/ _ \ / __| |/ _` | |
	 | (_) | |_) |  __/ | | |     \__ \ (_) | (__| | (_| | |
	  \___/| .__/ \___|_| |_|     |___/\___/ \___|_|\__,_|_|
	       | |                                              
	       |_|             Phil Bennett github@philbennett94

open-social (OPSO) is a python library built to make gethering data from social media platforms easier. 
OPSO currently supports facebook, instagram, tumblr, twitter, and reddit. 

## OPSO in Action

open-social was used to generate data that was then mined to produce the Power BI dashboard below. You will find a workflow to generate data similar to the data used in this dashboard in *examples/text_analysis.py*.

![alt text](https://github.com/philbennett94/open-social/blob/master/opso-example-analysis.PNG)

## General Information
**Dependencies**

OPSO relies on five other python libraries to support it's core functionality. 
All of these libraries are great resources for data mining on social media platforms, and you are encouraged to explore them and support their authors.
Please note that some of the libraries OPSO depends on may break without warning.
1. Facebook support via [facebook-sdk](https://github.com/mobolic/facebook-sdk)
2. Instagram support via [instagram_private_api](https://github.com/ping/instagram_private_api)
3. Tumblr support via [PyTumblr](https://github.com/tumblr/pytumblr)
4. Twitter support via [twython](https://github.com/ryanmcgrath/twython)
5. Reddit support via [PRAW](https://github.com/praw-dev/praw)

**Build v0**

OPSO uses pipenv to manage dependencies. You can find out more about pipenv at its official [site](https://docs.pipenv.org/) and official [github repository](https://github.com/pypa/pipenv).

Anyone using this package as of now should know that this is version 0, and it still has some kinks. If you would like to contribute, do not hesitate to fork OPSO. If you run into an issue, please report it as soon as possible.

**Other Notes**

You can host a privacy policy statement for a facebook/instagram application on github. 

Facebook recently changed their privacy policy regarding their graph api. You must request access to public page data from Facebook directly. You will not be able to use the FacebookClient available in OPSO on any data except for your own unless access is granted to you by Facebook.

You can review and collect your Facebook application's access token(s) from the [Access Token Tool](https://developers.facebook.com/tools/accesstoken/).

## Getting Started
**How Does it Work?**

open-social wraps multiple social media api wrappers so they can be accessed from a single client. Data is gathered using search functionality that varies slightly from client to client, but in all instances filters data returned from social media api's based on a search term defined by the user. Users can leverage OPSO to gather data from one or more of the supported api's.

**Implementation**

1. Create applications for use with Facebook Graph API, Tumblr REST API, Twitter REST API, and Reddit REST API. You will also need an Instagram account.
2. Create a file called info.json in the credentials directory (path: *open_social/credentials/info.json*). *info.json* is where you will store your application credentials. The correct format for *info.json* is shown below. You must have fields that correlate to the platform application(s) you are using: for example, if you are extracting data from instagram then you will need the instagram document attribute with valid username and password values in your *info.json* file.
```json
{
	"facebook":{
		"access_token":""
	},
	"instagram":{
		"username":"",
		"password":""
	},
	"twitter":{
		"app_key":"",
		"app_secret":"",
		"oauth_token":"",
		"oauth_token_secret":""
	},
	"reddit":{
		"client_id":"",
		"client_secret":"",
		"user_agent":""
	},
	"tumblr":{
		"consumer_key":"",
		"consumer_secret":"",
		"oauth_token":"",
		"oauth_secret":""
	}
}
```
3. Import OpenSocial into your python project:
```python
from open_social.open_social import OpenSocial
```
4. Use the OpenSocial class to collect data from multiple social media platforms:

Individual Data Grabs

```python
opso = OpenSocial()
# by default, all clients are created and OpenSocial.clients = [FacebookClient, TwitterClient, RedditClient, TumblrClient, InstaGramClient]
# specify a client by accessing an element of the clients list
# specify a search term, limit - the upper limit for the number of search results returned, and platform specific data sources
facebook = opso.get_data(opso.clients[0], "<searchTerm>", 10, pages = ["cnn"])
twitter = opso.get_data(opso.clients[1], "<searchTerm>", 10)
reddit = opso.get_data(opso.clients[2], "<searchTerm>", 10, subReddits = ["worldnews", "news", "politics"])
tumblr = opso.get_data(opso.clients[3], "<searchTerm>", 10, blogs = ["cnnpolitics.tumblr.com"])
instagram = opso.get_data(opso.clients[4], "<searchTerm>", 10, relevantUsers = ["cnn"])
```

Collective Data Grabs

```python
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
```
Data is returned as a list of dictionaries where each dictionary entry is a datapoint returned from a social media platform's api. OPSO parses data returned from each social media platform differently. A parsed response contains only a subset of fields returned by the api's.
