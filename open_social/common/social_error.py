import datetime, json, sys, traceback

class SocialError(object):

	"""
	Summary:
		A class used to document errors from data extraction in json format so that
		errors can be examined as a part of the payload reponse.
	"""
	
	def __init__(self):
		"""
		Summary:
			Initializes the SocialError class

		Args:
			None

		Returns:
			An instance of the SocialError class
		"""
		self.errorInfo = []

	def __str__(self):
		"""
		Summary:
			Generates a json string representation of the SocialError class

		Args:
			None

		Returns:
			A json string representation of the SocialErrorClass 
		"""
		return json.dumps(self.errorInfo)

	def add_error(self, errorType: object, errorValue: object, tracebackObject: object):
		"""
		Summary: 
			Adds a detailed error entry to the errorInfo list of an instance of SocialError

		Args:
			errorType: the type of the error that occured
			errorValue: the value of the error that occured
			tracebackObject: the instance of traceback that is related to the error

		Returns:
			None
		"""
		formattedException = traceback.format_exception(errorType, errorValue, tracebackObject)
		info = {
			"error_type": str(errorType),
			"error_location": formattedException[1],
			"error_issue": formattedException[2],
			"error_time": str(datetime.datetime.now())
		}
		self.errorInfo.append(info)