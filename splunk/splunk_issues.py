import requests
from requests.auth import HTTPBasicAuth
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

def get_issues(token):
    get_issues_url = f"https://{CC_IP}/dna/intent/api/v1/issues"
    headers = {"x-auth-token": token, "content-type": "application/json"}
    response = requests.get(get_issues_url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json().get('response', [])

def get_issue_details(issue_id, token):
    get_issue_details_url = f"https://{CC_IP}/api/assurance/v1/issue/{issue_id}"
    headers = {"x-auth-token": token, "content-type": "application/json"}
    response = requests.get(get_issue_details_url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json().get('response', {})

def send_to_splunk(data):
    headers = {
        'Authorization': f'Splunk {SPLUNK_HEC_TOKEN}',
        'Content-Type': 'application/json'
    }
    event = {
        "event": data,
        "sourcetype": "_json",
        "index": "cc_issues"  # Specify the index name here
    }
    response = requests.post(SPLUNK_HEC_ENDPOINT, headers=headers, json=event, verify=False)
    response.raise_for_status()

def main():
    token = get_token()
    issues = get_issues(token)
    for issue in issues:
        issue_id = issue.get('issueId')
        if issue_id:
            issue_details = get_issue_details(issue_id, token)
            send_to_splunk(issue_details)

if __name__ == "__main__":
    main()