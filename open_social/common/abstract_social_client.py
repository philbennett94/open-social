class AbstractSocialClient(object):

	"""
	Summary:
		Abstract class used to impose implementation guidelines for social clients
		whose parent libraries do not support pagination and data filtering.
	"""

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
		pass

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
		pass

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
		pass

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
		pass

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
		pass