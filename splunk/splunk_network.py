import requests
from requests.auth import HTTPBasicAuth
import config  # Import the config module

# Suppressing SSL warnings
requests.packages.urllib3.disable_warnings()

# Use the variables from config module
CC_IP = config.CC_IP
USERNAME = config.USERNAME
PASSWORD = config.PASSWORD


SPLUNK_HEC_TOKEN = config.SPLUNK_HEC_TOKEN
SPLUNK_HEC_ENDPOINT = config.SPLUNK_HEC_ENDPOINT

def get_token():
    token_url = f"https://{CC_IP}/dna/system/api/v1/auth/token"
    response = requests.post(token_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    response.raise_for_status()
    return response.json().get('Token')

def get_network_health(token):
    get_health_url = f"https://{CC_IP}/dna/intent/api/v1/network-health"
    headers = {"x-auth-token": token, "content-type": "application/json"}
    response = requests.get(get_health_url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

def send_to_splunk(hec_url, hec_token, data):
    headers = {
        'Authorization': f'Splunk {hec_token}',
        'Content-Type': 'application/json'
    }
    event = {
        "event": data,
        "sourcetype": "_json",
        "index": "cc_network"  # Specify the index name here
    }
    response = requests.post(hec_url, headers=headers, json=event, verify=False)
    response.raise_for_status()

def main():
    token = get_token()
    health_data = get_network_health(token)
    
    # Send the network health data to Splunk
    send_to_splunk(SPLUNK_HEC_ENDPOINT, SPLUNK_HEC_TOKEN, health_data)

if __name__ == "__main__":
    main()