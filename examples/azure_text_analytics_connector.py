import json, numpy, requests, sys, utils

class AzureTextAnalyticsConnector(object):

  def __init__(self, APP_NAME, APP_KEY1, API_ENDP):
    self.appName  = APP_NAME
    self.appKey   = APP_KEY1
    self.endpoint = API_ENDP
    self.headers  = {"Ocp-Apim-Subscription-Key": APP_KEY1}

  def __str__(self) -> str:
    return "Azure Text Analytics Connector\n\
            App Name: {name}\n\
            App Key: {key}\n\
            App Endpoint: {endpoint}".format(
              name = self.appName,
              key = self.appKey,
              endpoint = self.endpoint)

  def call_text_analytics(self, docs: dict, apiType: str) -> dict:
    # apiType: "languages", "sentiment", keyPhrases"
    apiUrl = self.endpoint + apiType
    response = requests.post(apiUrl, headers=self.headers, json=docs)
    payload = response.json()
    return payload

  def sentiment_aggregator(self, output: dict) -> float:
    return numpy.mean([score["score"] for score in output["documents"]])

  def key_phrases_aggregator(self, output: dict) -> dict:
    volumeCount = {}
    allPhrases = [y for x in [phrase["keyPhrases"] for phrase in output["documents"]] for y in x]
    for phrase in allPhrases:
      if phrase in volumeCount.keys():
        volumeCount[phrase] += 1
      else:
        volumeCount[phrase] = 1
    return volumeCount

  def languages_aggregator(self, output: dict) -> dict:
    payload = {}
    for doc in output["documents"]:
      for detectedLanguage in doc["detectedLanguages"]:
        if not detectedLanguage["name"] in payload.keys():
          payload[detectedLanguage["name"]] = {"count": 1, "confidence": detectedLanguage["score"]}
        else:
          payload[detectedLanguage["name"]]["count"] += 1
          payload[detectedLanguage["name"]]["confidence"] = numpy.mean([payload[detectedLanguage["name"]]["confidence"], detectedLanguage["score"]])
    return payload

  def create_document_set_large_text(self, text: str) -> list:
    """
    Maximum size of a single document: 5,000 characters as measured by String.Length.
    Maximum size of entire request: 1 MB
    Maximum number of documents in a request: 1,000 documents 
    The rate limit is 100 calls per minute. Note that you can submit a large quantity of documents in a single call (up to 1000 documents).
    """
    payload = []
    textBatches = [chunk for chunk in self.chunks(text, 5000)]
    documentLimit = self.estimate_limit(textBatches[0])
    if documentLimit > 1000:
      documentLimit = 1000
    if len(textBatches) > documentLimit:
      switch = documentLimit
    else:
      switch = len(textBatches)
    documentSet = {"documents": []}
    while textBatches:
      i = 0
      while i < switch and textBatches:
        textTarget = textBatches.pop(0)
        documentSet["documents"].append(self.create_document(i, textTarget))
        i += 1
      payload.append(documentSet)
    return payload

  def create_document_set_list_text(self, text: list) -> list:
    setCount = 0
    documentLimit = 1000
    payload = []
    docSet = {"documents": []}
    sizeLimit = self.estimate_limit("")
    currentSizeLimit = sizeLimit 
    for doc in text:
      docSize = utils.total_size(doc)
      if ((docSize > sizeLimit) or (len(doc) > 5000)):
        payload.extend(self.create_document_set_large_text(doc))
      elif ((currentSizeLimit - docSize >= 0) and (setCount < 1000)):
        docSet["documents"].append(self.create_document(setCount, doc))
        currentSizeLimit -= docSize
        setCount += 1
      else:
        payload.append(docSet)
        docSet = {"documents": []}
        currentSizeLimit = sizeLimit
        docSet["documents"].append(self.create_document(setCount, doc))
        currentSizeLimit -= docSize
        setCount = 1
    payload.append(docSet)
    return payload

  def estimate_limit(self, text: str) -> int:
    return (1000000 - utils.total_size({"documents": []}) + utils.total_size(self.headers)) // utils.total_size(self.create_document(0, text))

  def create_document(self, id: int, text: str) -> dict:
    return {"id": str(id), "text": text}

  def chunks(self, s: str, n: int) -> str:
    """
    Produce `n`-character chunks from `s`.
    CREDIT https://stackoverflow.com/questions/7111068/split-string-by-count-of-characters
    """
    for start in range(0, len(s), n):
      yield s[start:start+n]