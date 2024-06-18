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

# Getting the token from DNA Center
token_url = f"https://{CC_IP}/dna/system/api/v1/auth/token"
response = requests.post(token_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
response.raise_for_status()  # Check if the request was successful
token = response.json().get('Token')

# Define the headers for DNA Center
dnac_headers = {"x-auth-token": token, "content-type": "application/json"}

# Define the headers for Splunk
splunk_headers = {
    "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}",
    "Content-Type": "application/json"
}

# Function to send data to Splunk
def send_to_splunk(data):
    event = {
        "event": data,
        "sourcetype": "_json",
        "index": "cc_license"  # Specify the index name here
    }
    response = requests.post(SPLUNK_HEC_ENDPOINT, headers=splunk_headers, data=json.dumps(event), verify=False)
    response.raise_for_status()

# Function to get license overview data
def get_license_overview(url):
    response = requests.get(url, headers=dnac_headers, verify=False)
    response.raise_for_status()
    return response.json()

# URLs for different device types
license_overview_urls = {
    "switch": f"https://{CC_IP}/api/v1/licensemanager/compliance/overview?deviceType=switch&virtualAccount=All"
    #"router": f"https://{CC_IP}/api/v1/licensemanager/compliance/overview?deviceType=router&virtualAccount=All",
    #"wireless": f"https://{CC_IP}/api/v1/licensemanager/compliance/overview?deviceType=wireless&virtualAccount=All",
    #"ise": f"https://{CC_IP}/api/v1/licensemanager/compliance/overview?deviceType=ise&virtualAccount=All"
}

# Collect and send data for each device type
for device_type, url in license_overview_urls.items():
    license_overview = get_license_overview(url)
    send_to_splunk(license_overview)
    print(f"Sent {device_type} license overview to Splunk.")
