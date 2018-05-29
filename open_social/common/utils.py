from .social_error import SocialError
import datetime, json, sys, traceback

def search(client: object, searchTerm: str, sources: list, limit: int) -> list:
	"""
	Summary:
		Facilitates search for FacebookClient, InstagramClient, and TumblrClient

	Args:
		client: a valid instance of FacebookClient, InstagramClient, or TumblrClient
		searchTerm: the searchTerm to match against for use in validating relevant data
					points
		sources: a list of sources to search over. This could be a list of subreddits,
				 public facebook pages, or instagram usernames
		limit: the upper limit for the count of data points returned by the search

	Returns:
		A list of relevant data points that has a count no greater than limit
	"""
	payload = []
	switch = limit // len(sources)
	searchTerm = searchTerm.lower()
	try:
		for source in sources:
			count = 0
			dataPage, nextPageLink = client.get_page(source)
			while count < switch:	
				for datum in dataPage:
					if count == switch:
						break
					else:
						if client.match(searchTerm, datum):
							entry = client.parse(datum)
							payload.append(entry)
							count += 1
				dataPage, nextPageLink = client.update_page(nextPageLink)
	except:
		etype, value, tb = sys.exc_info()
		print(etype, value, tb)
		error = SocialError(etype, value, tb)
		payload.append([{"error(s)": error.errorInfo}])
	finally:
		return payload