from azure_text_analytics_connector import AzureTextAnalyticsConnector
import json, numpy, requests, xlwt, sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from open_social.open_social import OpenSocial

def extract_text_instagram(entry: dict) -> list:
	caption = [entry["caption"] if "caption" in entry.keys() else "caption"] 
	comments = [x["text"] for x in entry["secondary_information"]["comments"]]
	caption.extend(comments)
	return caption 

def extract_text_tumblr(entry: dict) -> list:
	summary = [entry["summary"]]
	notes = [x["added_text"] for x in entry["notes"] if x["type"] == "reblog" and "added_text" in x.keys()]
	summary.extend(notes) 
	return summary

def extract_text_twitter(entry: dict) -> list:
	text = entry["text"]
	return text

def extract_text_reddit(entry: dict) -> list:
	title = [entry["title"]]
	comments = [x["body"] for x in entry["secondary_information"]["comments"]]
	title.extend(comments)
	return title

def mine_text(atacInstance: object, data: list) -> tuple:
	docSet = atacInstance.create_document_set_list_text(data)
	lData = atac.call_text_analytics(docSet[0], "languages")
	sData = atac.call_text_analytics(docSet[0], "sentiment")
	kData = atac.call_text_analytics(docSet[0], "keyPhrases")
	return lData, sData, kData

def generate_text_analytics_aggregates(atacInstance: object, data: list) -> list:
	payloadTmp, payloadFinal = [], {"lAgg": {}, "sAgg": {"totalScore": 0, "rawScores": []}, "kAgg": {}}
	for entry in data:
		lAgg = atacInstance.languages_aggregator(entry[0])
		sAgg = atacInstance.sentiment_aggregator(entry[1])
		kAgg = atacInstance.key_phrases_aggregator(entry[2])
		payloadTmp.append({"lAgg": lAgg, "sAgg": sAgg, "kAgg": kAgg})
	for entry in payloadTmp:
		for k in list(entry["lAgg"].keys()):
			if k in payloadFinal["lAgg"].keys():
				payloadFinal["lAgg"][k] = {"count": payloadFinal["lAgg"][k]["count"] + entry["lAgg"][k]["count"], 
										   "confidence": numpy.mean([payloadFinal["lAgg"][k]["confidence"], entry["lAgg"][k]["confidence"]])}
			else:
				payloadFinal["lAgg"][k] = {"count": entry["lAgg"][k]["count"],
										   "confidence": entry["lAgg"][k]["confidence"]}
		payloadFinal["sAgg"]["totalScore"] = numpy.mean([payloadFinal["sAgg"]["totalScore"], entry["sAgg"]])
		payloadFinal["sAgg"]["rawScores"].append(entry["sAgg"])
		for k in list(entry["kAgg"].keys()):
			if k in payloadFinal["kAgg"].keys():
				payloadFinal["kAgg"][k] += entry["kAgg"][k]
			else:
				payloadFinal["kAgg"][k] = entry["kAgg"][k]
	return payloadFinal

if __name__ == '__main__':
	APP_NAME = "<azure text analytics app name>"
	APP_KEY1 = "<azure text analytics app key>"
	API_ENDP = "https://<region app is provisioned in>.api.cognitive.microsoft.com/text/analytics/v2.0/"
	# create clients
	atac = AzureTextAnalyticsConnector(APP_NAME, APP_KEY1, API_ENDP)
	opso = OpenSocial()
	# get data
	instagram = opso.get_data(opso.clients[4], "trump", 10, relevantUsers = ["cnn"])
	tumblr = opso.get_data(opso.clients[3], "trump", 10, blogs = ["cnnpolitics.tumblr.com"])
	twitter = opso.get_data(opso.clients[1], "trump", 10)
	reddit = opso.get_data(opso.clients[2], "trump", 10, subReddits = ["worldnews", "news", "politics"])
	# parse data
	igData = list(map(extract_text_instagram, instagram["instagram"]))
	tuData = list(map(extract_text_tumblr, tumblr["tumblr"]))
	twData = list(map(extract_text_twitter, twitter["twitter"]))
	reData = list(map(extract_text_reddit, reddit["reddit"]))
	# generate text analytics data
	igTextMine = [mine_text(atac, x) for x in igData]
	tuTextMine = [mine_text(atac, x) for x in tuData]
	twTextMine = [mine_text(atac, x) for x in twData] 
	reTextMine = [mine_text(atac, x) for x in reData]
	# generate aggregate data for each source
	igAggregates = generate_text_analytics_aggregates(atac, igTextMine)
	tuAggregates = generate_text_analytics_aggregates(atac, tuTextMine)
	twAggregates = generate_text_analytics_aggregates(atac, twTextMine)
	reAggregates = generate_text_analytics_aggregates(atac, reTextMine)
