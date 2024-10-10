import pytz
import re

def TZ(tz):
	return pytz.timezone(tz)

def filterAddress(address):
	if address is None:
		return (None, None)

	# Check for protocol (e.g. https://)
	# We don't actually care about it, so discard it (repgen only works with http or https)
	match = re.match(r"(https?:\/\/)?(.+)", address)
	host = match.group(2)
	query = None

	# Repgen4 supports host:port:sid
	# Since this only parses HTTP URLs,
	# only accept host:port/path
	if '/' in host:
		parts = host.split('/', 1)
		host = parts[0]
		query = parts[1] if len(parts) > 1 else None
	elif host.count(':') > 1:
		raise ValueError(f"Oracle DB '{host}' is not supported. Use CDA.")
	
	# Check if port was specified, and add one if not
	if ':' not in host:
		host += (":443" if match.group(1) is not None and match.group(1).startswith("https") else ":80")

	return (host, query)


def pascalToCamel(obj):
	"""
	Convert a dictionary with pascal-case keys to a dictionary with camelCase keys.
	
	Args:
		obj (dict): The dictionary to convert.
	
	Returns:
		dict: The converted dictionary.
	"""
	_camelObj = {}
	for key in obj.keys():
		# for keys with multiple hyphens - in the name, split and capitalize each part ignoring the first
		_cKey = key.split("-")[0] + "".join([i.capitalize() for i in key.split("-")[1:]])
		value = obj[key]
		# Cleanup strings that should otherwise be None
		if isinstance(value, str) and value.upper() == "NULL":
			value = None
		_camelObj[_cKey] = value
	return _camelObj