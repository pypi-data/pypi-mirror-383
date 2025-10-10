#!/usr/intel/bin/python3


import requests
import json
import hashlib
import hmac
import base64
import pandas as pd
import sys
from datetime import datetime,UTC

#Function to fetch the SPeTC ids based upon the Workweek and releasebranch
def spetc_ids_req(workweek,releasebranch):
    """
    Fetches SPeTC IDs for the given workweek and release branch using the SPeTC API.

    Args:
        workweek (str): The workweek identifier (e.g., 'WW35').
        releasebranch (str): The release branch name (e.g., 'main').

    Returns:
        spetc_ids or None: A comma-separated string of SPeTC IDs if found, otherwise None.
    """
    # Import the function to generate SPeTC headers
    from gen_spetc_headers import generateSpetcHeaders
    # API request details
    method = 'GET'
    url = "https://acds-central-api-prod.altera.com/test-infra-api/v3/testRuns/workWeek?*"
    publicAccessKey = "ddae53ec-95a9-410c-81ba-e1f127464e06"
    secretAccessKey = "3yNSztcvkVKAGkm4LQyz"
    contentType = ''
    contentMd5 = ''
    # Generate API request headers using the provided keys and method
    headers = generateSpetcHeaders(
        { 
            'clientId': publicAccessKey, 
            'secretKey': secretAccessKey, 
            'method': method, 
            'fullUrl': url,
            'contentType': contentType, 
            'contentMd5': contentMd5, 
            'cache': True 
        }
    )
    # Make the GET request to the SPeTC API
    response = requests.get(url, headers=headers,verify=True)
    #Checks whether response is successful or not.
    if (response.ok):
        # Parse the JSON response content
        jData = json.loads(response.content)
        # Convert JSON data to a pandas DataFrame
        response_df=  pd.DataFrame(jData)
        if releasebranch not in response_df['releaseVersion'].values:
            print(f"Error: Release Branch {releasebranch} not available.")
            sys.exit(0)
        # Filter the DataFrame based on workweek and releasebranch
        print(f"Fetching spetc_ids for {workweek} for releasebranch {releasebranch}")
        result=response_df.loc[(response_df['workWeek']==workweek) & (response_df['releaseVersion']==releasebranch) ,'testRunIds']
        # If no matching records found, return None
        if result.empty:
        	return None
        # Join the testRunIds into a comma-separated string
        spetc_ids=','.join(str(x) for x in result.iloc[0]) 
    else:
        print ("Response not found for the API")
        return None
    # Return the comma-separated SPeTC IDs (or None)
    return spetc_ids


