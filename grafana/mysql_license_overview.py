import requests
from requests.auth import HTTPBasicAuth
import mysql.connector
from mysql.connector import Error
import json
import config  # Import the config module

# Suppressing SSL warnings
requests.packages.urllib3.disable_warnings()

# Use the variables from config module
CC_IP = config.CC_IP
USERNAME = config.USERNAME
PASSWORD = config.PASSWORD
DB_CONFIG = config.DB_CONFIG

def get_token():
    token_url = f"https://{CC_IP}/dna/system/api/v1/auth/token"
    response = requests.post(token_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    response.raise_for_status()
    return response.json().get('Token')

def get_license_overview(token, device_type):
    license_overview_url = f"https://{CC_IP}/api/v1/licensemanager/compliance/overview?deviceType={device_type}&virtualAccount=All"
    headers = {"x-auth-token": token, "content-type": "application/json"}
    response = requests.get(license_overview_url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

def connect_db():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()
        return db, cursor
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        exit(1)

def insert_license_data(cursor, db, license_data, device_type):
    # Delete existing data for the specific device_type to ensure only fresh data is present
    cursor.execute("DELETE FROM license_data WHERE device_type = %s", (device_type,))

def create_table(cursor):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS license_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        device_type VARCHAR(255),
        total_devices INT,
        entitled_essentials INT,
        entitled_advantage INT,
        entitled_premier INT,
        deployed_essentials INT,
        deployed_advantage INT,
        deployed_premier INT,
        deployed_license_description TEXT,
        deployed_license_percentage FLOAT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """
    try:
        cursor.execute(create_table_query)
    except mysql.connector.Error as e:
        if e.errno == 1050:  # Error code for 'Table already exists'
            print("Table already exists. Continuing with data insertion.")
        else:
            raise

def insert_license_data(cursor, db, license_data, device_type):
    # Delete existing data for the specific device_type to ensure only fresh data is present
    cursor.execute("DELETE FROM license_data WHERE device_type = %s", (device_type,))

    # Initialize all license counts to zero
    entitled_essentials = entitled_advantage = entitled_premier = 0
    deployed_essentials = deployed_advantage = deployed_premier = 0

    # Extract entitled license data
    for license_type in license_data['response']['entitledDNALicenseData']:
        if license_type['title'] == 'Essentials':
            entitled_essentials = license_type['value']
        elif license_type['title'] == 'Advantage':
            entitled_advantage = license_type['value']
        elif license_type['title'] == 'Premier':
            entitled_premier = license_type['value']

    # Extract deployed license data
    for license_type in license_data['response']['deployedDNALicenseData']:
        if license_type['title'] == 'Essentials':
            deployed_essentials = license_type['value']
        elif license_type['title'] == 'Advantage':
            deployed_advantage = license_type['value']
        elif license_type['title'] == 'Premier':
            deployed_premier = license_type['value']

    total_devices = license_data['response']['totalDevices']
    deployed_license_description = license_data['response']['deployedLicenseDescription']
    deployed_license_percentage = license_data['response']['deployedLicensePercentage']

    sql = """
    INSERT INTO license_data(
        device_type,
        total_devices,
        entitled_essentials,
        entitled_advantage,
        entitled_premier,
        deployed_essentials,
        deployed_advantage,
        deployed_premier,
        deployed_license_description,
        deployed_license_percentage
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (
        device_type,
        total_devices,
        entitled_essentials,
        entitled_advantage,
        entitled_premier,
        deployed_essentials,
        deployed_advantage,
        deployed_premier,
        deployed_license_description,
        deployed_license_percentage
    ))
    db.commit()

def main():
    token = get_token()
    db, cursor = connect_db()
    create_table(cursor)  # Create the table if it doesn't exist

    device_types = ['switch', 'router', 'wireless', 'ise']

    for device_type in device_types:
        license_data = get_license_overview(token, device_type)
        insert_license_data(cursor, db, license_data, device_type)

    cursor.close()
    db.close()

if __name__ == "__main__":
    main()
