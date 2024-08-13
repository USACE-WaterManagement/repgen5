# stdlib 
from urllib.parse import quote
# third party
from repgen import session
from requests.exceptions import HTTPError
from requests import Response
from json.decoder import JSONDecodeError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# custom
from repgen import PROD_CDA_HOST, REQUEST_TIMEOUT_SECONDS, \
    MAX_RETRIES, BACKOFF_FACTOR

_retry_strategy = Retry(
    total=MAX_RETRIES,
    status_forcelist=[429, 500, 502, 503, 504],  
    method_whitelist=["GET"], 
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
class LevelsApi:
    
    @staticmethod
    def getLevelById(levelId: str, office: str, effectiveDate: str, unit: str = "", timeZone: str = "GMT", *args, **kwargs) -> dict:
        '''
        Get levels for a site from the CDA API.

        Args:
            levelId (str): Specifies the requested location level.
            office (str): Specifies the office of the Location Level to be returned.
            effectiveDate (str): Specifies the effective date of Location Level to be returned.
            timeZone (str, optional): Specifies the time zone of the values of the effective date field (unless otherwise specified), as well as the time zone of any times in the response. If this field is not specified, the default time zone of UTC shall be used.
            unit (str, optional): Desired unit for the values retrieved.

        Returns:
            LevelResponse: A structured response containing location level details.
            
        Example:
            Level.getLevelById(
                levelId="KEYS.Elev.Inst.0.Top of Conservation", 
                office="SWT", 
                effectiveDate="2024-06-21T00:00:00", 
                timeZone="America/Chicago", 
                unit="ft"
            )
        '''
        
        if not levelId:
            raise ValueError("levelId is required: i.e. levelId='KEYS.Elev.Inst.0.Top of Conservation'")
        elif not office:
            raise ValueError("office is required: i.e. office='SWT'")
        elif not effectiveDate:
            raise ValueError("effectiveDate is required: i.e. effectiveDate='2024-06-21T00:00:00'")
        elif not unit:
            raise ValueError("unit is required: i.e. unit='ft'")
        else:
            # Encode the levelId for % and / characters that are not allowed in the URL
            levelId = quote(levelId)
        params = {"effective-date": effectiveDate, "timezone": quote(timeZone), "unit": unit, "office": office, **kwargs}
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        # Encode only the values
        # encoded_params = {k: quote(str(v)) for k, v in params.items()}
        try:
            response = session.get(f"{PROD_CDA_HOST}/levels/{levelId}" , 
                                   params=params, 
                                   timeout=REQUEST_TIMEOUT_SECONDS)
            print(f"[/levels/{levelId}]\t", response.url)
            # Raise HTTPError if one occurred
            response.raise_for_status()
        except HTTPError as err:
            printError(err, response)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error getting levels for levelId {levelId} and office {office}: {response.status_code}\n{response.text}")

    @staticmethod
    def getLevels(levelIdMask: str, 
                  office: str, 
                  unit: str = None, 
                  datum: str = None, 
                  begin: str = None, 
                  end: str = None, 
                  timeZone: str = None, 
                  format: str = "json", 
                  page: str = None,
                  pageSize = None,
                  *args, **kwargs) -> dict:
        '''
        Get levels for a site from the CDA API.

        Args:
            levelIdMask (str): pecifies the name(s) of the location level(s) whose data is to be included in the response. Uses * for all.
            office (str): Specifies the owning office of the location level(s) whose data is to be included in the response. If this field is not specified, matching location level information from all offices shall be returned.
            unit (str, optional): Specifies the unit or unit system of the response. Valid values for the unit field are:
                1. EN (DEFAULT) - Specifies English unit system. Location level values will be in the default English units for their parameters.
                2. SI - Specifies the SI unit system. Location level values will be in the default SI units for their parameters.
                3. Other - Any unit returned in the response to the units URI request that is appropriate for the requested parameters.
            datum (str, optional):pecifies the elevation datum of the response. This field affects only elevation location levels. Valid values for this field are:
                1. NAVD88 - The elevation values will in the specified or default units above the NAVD-88 datum.
                2. NGVD29 - The elevation values will be in the specified or default units above the NGVD-29 datum.
            begin (str, optional): Specifies the start of the time window for data to be included in the response. If this field is not specified, any required time window begins 24 hours prior to the specified or default end time.
            end (str, optional): Specifies the end of the time window for data to be included in the response. If this field is not specified, any required time window ends at the current time
            timeZone (str, optional): Specifies the time zone of the values of the begin and end fields (unless otherwise specified), as well as the time zone of any times in the response. If this field is not specified, the default time zone of UTC shall be used.
            format (str, optional): Specifies the encoding format of the response. Requests specifying an Accept header:application/json;version=2 must not include this field. Valid format field values for this URI are:
                1. tab
                2. csv
                3. xml
                4. wml2 (only if name field is specified)
                5. json (default)
            page (str, optional): This identifies where in the request you are. This is an opaque value, and can be obtained from the 'next-page' value in the response.
            pageSize (str, optional): How many entries per page returned. Default 100.

        Returns:
            dict: A structured response containing location level details.
            
        Example:
            Level.getLevels(
                levelIdMask="KEYS.Elev.Inst.0.*", 
                office="SWT", 
                effectiveDate="2024-06-21T00:00:00", 
                timeZone="America/Chicago", 
                unit="ft"
            )
        '''
        
        if not levelIdMask:
            raise ValueError("levelIdMask is required: i.e. levelIdMask='KEYS.Elev.Inst.0.*'")
        elif not office:
            raise ValueError("office is required: i.e. office='SWT'")
        params = {
            "level-id-mask": levelIdMask, 
            "office": office, 
            "unit": unit, 
            "datum": datum, 
            "begin": begin, 
            "end": end, 
            "timezone": timeZone, 
            "format": format, 
            "page": page, 
            "page-size": pageSize, 
            **kwargs
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        # Encode only the values
        # encoded_params = {k: quote(str(v)) for k, v in params.items()}
        try:
            response = session.get(f"{PROD_CDA_HOST}/levels" , 
                                    headers={
                                        "Accept": "*/*"
                                    },
                                    params=params, 
                                    timeout=REQUEST_TIMEOUT_SECONDS)
            print("[/levels]\t", response.url)
            # Raise HTTPError if one occurred
            response.raise_for_status()
        except HTTPError as err:
            printError(err, response)
            
        if response.status_code == 200:
            try:
                return response.json()
            except JSONDecodeError as err:
                print(f"JSONDecodeError: {err}")
                print(f"Response: {response.text}")
        else:
            raise Exception(f"Error getting levels for levelIdMask {levelIdMask} and office {office}: {response.status_code}\n{response.text}")

if __name__ == "__main__":
    # Invoke this script for testing with: (to make sure to import the top level repgen package)
    # python -m repgen.data.levels
    
    print("WARNING: This script should ONLY be called directly for testing purposes.")
    print("TEST: Level.getLevelById")
    print(LevelsApi.getLevelById(
            levelId="KEYS.Elev.Inst.0.Top of Conservation", 
            office="SWT", 
            effectiveDate="2024-06-21T00:00:00", 
            timeZone="America/Chicago", 
            unit="ft"))
    print("TEST: Level.getLevels")
    print(LevelsApi.getLevels(levelIdMask="KEYS.Elev.Inst.0.Top of Conservation", 
                          begin="2024-06-11T00:00:00-05:00",
                          end="2024-06-12T00:00:00-05:00",
                          timeZone="America/Chicago",
                          office="SWT"))