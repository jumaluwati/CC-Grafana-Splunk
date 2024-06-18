# config.py

# Common credentials
CC_IP = 'sandboxdnac.cisco.com'
USERNAME = 'devnetuser'
PASSWORD = 'Cisco123!'

# Database configuration
DB_CONFIG = {
    'user': 'root',
    'password': 'cisco',
    'host': 'localhost',
    'database': 'cc_db',
    'raise_on_warnings': True,
}

# Splunk details
SPLUNK_HEC_TOKEN = 'e19bf18b-e9d8-466b-9327-84e3e520e208'
SPLUNK_HEC_ENDPOINT = 'http://localhost:8088/services/collector'
