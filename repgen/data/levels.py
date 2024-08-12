# stdlib 
from urllib.parse import quote
# third party
import requests
import sys
import os

# custom
from repgen import PROD_CDA_HOST, REQUEST_TIMEOUT_SECONDS

class Level:
    @staticmethod
    def getLevelById(levelId: str, office: str, effectiveDate: str, timeZone: str = "", unit: str = "", *args, **kwargs) -> dict:
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
        '''
        
        if not levelId:
            raise ValueError("levelId is required: i.e. levelId='KEYS.Elev.Inst.0.Top of Conservation'")
        else:
            # Encode the levelId for % and / characters that are not allowed in the URL
            levelId = quote(levelId)
        params = {"effective-date": effectiveDate, "timezone": timeZone, "unit": unit, "office": office, **kwargs}
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        # Encode only the values
        encoded_params = {k: quote(str(v)) for k, v in params.items()}
        print(encoded_params)
        print(f"{PROD_CDA_HOST}/levels/{levelId}")
        response = requests.get(f"{PROD_CDA_HOST}/levels/{levelId}" , params=encoded_params, timeout=REQUEST_TIMEOUT_SECONDS)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error getting levels for levelId {levelId} and office {office}: {response.status_code}")

if __name__ == "__main__":
    # Invoke this script for testing with: (to make sure to import the top level repgen package)
    # python -m repgen.data.levels
    
    print("NOTE: This script should ONLY be called directly for testing purposes.")
    print(Level.getLevelById(levelId="KEYS.Elev.Inst.0.Top of Conservation", office="SWT", effectiveDate="2024-06-21", timeZone="America/Chicago", unit="ft"))