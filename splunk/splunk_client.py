import datetime
import requests
from requests.auth import HTTPBasicAuth
import json
import config  # Import the config module

# Suppressing SSL warnings
requests.packages.urllib3.disable_warnings()

# Use the variables from config module
CC_IP = config.CC_IP
USERNAME = config.USERNAME
PASSWORD = config.PASSWORD

# Splunk details
SPLUNK_HEC_TOKEN = config.SPLUNK_HEC_TOKEN
SPLUNK_HEC_ENDPOINT = config.SPLUNK_HEC_ENDPOINT

def get_token():
    token_url = f"https://{CC_IP}/dna/system/api/v1/auth/token"
    response = requests.post(token_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    response.raise_for_status()
    return response.json().get('Token')


def get_data(token):
    api_url = f"https://{CC_IP}/api/assurance/v1/host/dash/healthdetail"
    
    # Get the current time in milliseconds since epoch
    current_time = int(datetime.datetime.now().timestamp() * 1000)
    
    # Define the payload with dynamic time values
    payload = {
        "typeList": {
            "type": "SITE",
            "typeIdList": [],
            "startTime": current_time - (5 * 60 * 1000),  # 5 minutes before current time
            "endTime": current_time,
            "filters": {
                "ssid": [],
                "frequency": ""
            },
            "currentTime": current_time,
            "timeAPITime": current_time
        },
        "option": "CLIENT",
        "selectedTypeIdList": ["/2db4f09f-0389-44d6-88d3-80fabb9ebbe8/"]
    }
    
    headers = {
        'X-Auth-Token': token,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(api_url, headers=headers, json=payload, verify=False)
    response.raise_for_status()
    return response.json()

def send_to_splunk(data):
    headers = {
        'Authorization': f'Splunk {SPLUNK_HEC_TOKEN}',
        'Content-Type': 'application/json'
    }
    event = {
        "event": data,
        "sourcetype": "_json",
        "index": "cc_client"  # Specify the index name here
    }
    response = requests.post(SPLUNK_HEC_ENDPOINT, headers=headers, data=json.dumps(event), verify=False)
    response.raise_for_status()

def main():
    # Fetch token and data from the API
    token = get_token()
    data = get_data(token)

    # Send data to Splunk
    send_to_splunk(data)

if __name__ == "__main__":
    main()
