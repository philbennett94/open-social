# CREDIT: https://github.com/ping/instagram_private_api
import codecs, datetime, json, os.path, sys

try:
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)

def to_json(pythonObject: object) -> dict:
	"""
	Summary:
		Serializes a python object to json
		CREDIT: https://github.com/ping/instagram_private_api

	Args:
		pythonObject: a python object

	Returns:
		A dictionary representing the serialized object
	"""
	if isinstance(pythonObject, bytes):
		return {'__class__': 'bytes', '__value__': codecs.encode(pythonObject, 'base64').decode()}
	raise TypeError(repr(pythonObject) + ' is not JSON serializable')

def from_json(jsonObject: object) -> object:
	"""
		Summary:
			Decodes a serailized json object
			CREDIT: https://github.com/ping/instagram_private_api

		Args:
			jsonObject: the object to be decoded

		Returns:
			A base64 decoded object
	"""
	if '__class__' in jsonObject and jsonObject['__class__'] == 'bytes':
		return codecs.decode(jsonObject['__value__'].encode(), 'base64')
	return jsonObject

def onlogin_callback(api: object, newSettingsFile: str):
	"""
	Summary:
		Saves client settings for the InstagramClient to avoid re-login
		CREDIT: https://github.com/ping/instagram_private_api

	Args:
		api: an instance of instagram_private_api.Client
		newSettingsFile: the name or path of the file to save the settings to

	Returns:
		None 
	"""
	cacheSettings = api.settings
	with open(newSettingsFile, 'w') as outfile:
		json.dump(cacheSettings, outfile, default=to_json)
		print('SAVED: {0!s}'.format(newSettingsFile))

def generate_client_from_cache(username: str, password: str, settingsFilePath: str = None) -> object:
	"""
	Summary:
		Generates an instance of instagram_private_api.Client that reuses saved settings,
		like cookies, to minimize login attempts. If no file exists, then a settings file
		will be generated.
		CREDIT: https://github.com/ping/instagram_private_api

	Args:
		username: a valid instagram username
		password: a valid instagram password
		settingsFilePath: (optional) the path to the file that holds settings

	Returns:
		An instance of instagram_private_api.Client
	"""
	try:
		if settingsFilePath == None:
			settingsFile = "instagram_client_cache.json"
		else:
			settingsFile = settingsFilePath
		if not os.path.isfile(settingsFile):
			# settings file does not exist
			print('Unable to find file: {0!s}'.format(settingsFile))
			# login new
			api = Client(
				username, password,
				on_login=lambda x: onlogin_callback(x, settingsFile))
		else:
			with open(settingsFile) as fileData:
				cachedSettings = json.load(fileData, object_hook=from_json)
			print('Reusing settings: {0!s}'.format(settingsFile))
			#deviceId = cachedSettings.get('device_id')
			# reuse auth settings
			api = Client(
				username, password,
				settings=cachedSettings)
		return api
	except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
		print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))
		# Login expired
		# Do relogin but use default ua, keys and such
		api = Client(
			username, password,
			on_login=lambda x: onlogin_callback(x, settingsFilePath))
	except ClientLoginError as e:
		print('ClientLoginError {0!s}'.format(e))
		exit(9)
	except ClientError as e:
		print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
		exit(9)
	except Exception as e:
		print('Unexpected Exception: {0!s}'.format(e))
		exit(99)

def show_cookie_expiry(api: object) -> str:
	"""
	Summary:
		Returns the time a cookie will expire for saved settings linked to an instance of
		instagram_private_api.Client
		CREDIT: https://github.com/ping/instagram_private_api

	Args:
		api: an instance of instagram_private_api.Client

	Returns:
		A string documenting when the cookie will expire
	"""
	cookieExpiry = api.cookie_jar.expires_earliest
	return 'Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(cookieExpiry).strftime('%Y-%m-%dT%H:%M:%SZ'))