# stdlib 
from urllib.parse import quote
import re
# third party
from repgen import session
from requests.exceptions import HTTPError
from requests import Response
from json.decoder import JSONDecodeError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# custom
from repgen import PROD_CDA_HOST, REQUEST_TIMEOUT_SECONDS, \
    MAX_RETRIES, BACKOFF_FACTOR, CDA_UNIT_SYSTEMS

_retry_strategy = Retry(
    total=MAX_RETRIES,
    status_forcelist=[429, 500, 502, 503, 504],  
    backoff_factor=BACKOFF_FACTOR, 
)

session.mount("https://", HTTPAdapter(max_retries=_retry_strategy))


def printError(err: HTTPError, response: Response) -> None:
    '''
    Prints the error and response if present

    Args:
        err (HTTPError): The HTTPError object.
        response (Response): The Response object.
    '''
    print(f"HTTPError: {err}")
    if err.response.status_code == 404:
        print(f"HTTPError: 404 Not Found")
    elif err.response.status_code == 400:
        print(f"HTTPError: 400 Bad Request")
    print(f"Response: {err.response.text}")
    if response:
        print(f"Response: {response.text}") 

class LocationsApi:
    @staticmethod
    def getLocationById(locationId: str, office: str, unit: str = "", *args, **kwargs) -> dict:
        '''
        Get location for a site from the CDA API.

        Args:
            locationId (str): Specifies the requested location.
            office (str): Specifies the office of the Location to be returned.
            unit (str, optional): Desired unit for the values retrieved.

        Returns:
           {
            active?: boolean;
            boundingOfficeId?: string;
            countyName?: string;
            description?: string;
            elevation?: number;
            horizontalDatum?: string;
            latitude?: number;
            locationKind?: string;
            locationType?: string;
            longName?: string;
            longitude?: number;
            mapLabel?: string;
            name: string;
            nation?: LocationNationEnum;
            nearestCity?: string;
            officeId: string;
            publicName?: string;
            publishedLatitude?: number;
            publishedLongitude?: number;
            stateInitial?: string;
            timezoneName?: string;
            verticalDatum?: string;
        }
        '''
        
        if not locationId:
            raise ValueError("locationId is required: i.e. locationId='KEYO2'")
        elif not office:
            raise ValueError("office is required: i.e. office='SWT'")
        elif unit not in CDA_UNIT_SYSTEMS:
            raise ValueError(f"unit must be one of {', '.join(CDA_UNIT_SYSTEMS)}: i.e. unit='EN'\n\n\tYou entered '{unit}'")
        else:
            # Encode the levelId for % and / characters that are not allowed in the URL
            locationId = quote(locationId)
        params = {"unit": unit, "office": office, **kwargs}
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        # Encode only the values
        # encoded_params = {k: quote(str(v)) for k, v in params.items()}
        try:
            response = session.get(f"{PROD_CDA_HOST}/locations/{locationId}" , 
                                   params=params, 
                                   timeout=REQUEST_TIMEOUT_SECONDS)
            print(f"[//locations/{locationId}]\t", response.url)
            # Raise HTTPError if one occurred
            response.raise_for_status()
        except HTTPError as err:
            printError(err, response)
        if response.status_code == 200:
            data = response.json()
            # replace all keys that are pascal-case with camelCase
            # do this so we can use the camelCase keys in the repgen code
            _camelObj = {}
            for key in data.keys():
                # for keys with multiple hyphens - in the name, split and capitalize each part ignoring the first
                _cKey = key.split("-")[0] + "".join([i.capitalize() for i in key.split("-")[1:]])
                value = data[key]
                # Cleanup strings that should otherwise be None
                if isinstance(value, str) and value.upper() == "NULL":
                    value = None
                _camelObj[_cKey] = value
            return _camelObj
        else:
            raise Exception(f"Error getting metadata for locationId {locationId} and office {office}: {response.status_code}\n{response.text}")

if __name__ == "__main__":
    # Invoke this script for testing with: (to make sure to import the top level repgen package)
    # python -m repgen.data.locations
    
    print("WARNING: This script should ONLY be called directly for testing purposes.")
    print("TEST: LocationsApi.getLocationById")
    print(LocationsApi.getLocationById(
            locationId="KEYS", 
            office="SWT", 
            unit="EN"))