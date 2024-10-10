import requests

REPGEN_DOCS_URL = "https://repgen5.readthedocs.io/"
PROD_CDA_HOST = "https://cwms-data.usace.army.mil/cwms-data"

# Time in seconds before a request should timeout
REQUEST_TIMEOUT_SECONDS = 30
# The MAX number of times to retry a request
MAX_RETRIES = 3
# The amount of time to wait before retrying a request in seconds
BACKOFF_FACTOR = 1 
# Create a session for all requests
session = requests.Session()

CDA_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

# Specifies the allowed unit system of the level response
CDA_UNIT_SYSTEMS = ["SI", "EN", "Other"]

DB_OPTIONS = ["GENTS", "COPY", "SPKJSON", "JSON"]