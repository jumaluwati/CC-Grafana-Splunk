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
SPLUNK_HEC_TOKEN = 'INSERT YOUR TOKEN HERE'
SPLUNK_HEC_ENDPOINT = 'http://localhost:8088/services/collector'
