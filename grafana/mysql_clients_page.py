import datetime
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

def connect_db():
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
        return db, cursor
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        exit(1)

def create_client_scores_table(cursor):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS client_scores (
        id INT AUTO_INCREMENT PRIMARY KEY,
        client_type VARCHAR(255) NOT NULL,
        score_value INT,
        client_count INT,
        UNIQUE (client_type)
    )
    """
    try:
        cursor.execute(create_table_query)
    except mysql.connector.Error as e:
        if e.errno == 1050:  # Error code for 'Table already exists'
            print("Table already exists. Continuing with data insertion.")
        else:
            raise

def insert_client_scores_data(data, cursor, db):
    # Delete existing data to ensure only fresh data is present
    cursor.execute("DELETE FROM client_scores")

    # Extract and insert the relevant data
    for response_item in data['response']:
        for score_detail in response_item['scoreDetail']:
            score_category = score_detail['scoreCategory']['scoreCategory']
            if score_category == "CLIENT_TYPE":
                value = score_detail['scoreCategory']['value']
                if value.upper() in ['ALL', 'WIRED', 'WIRELESS']:
                    insert_query = """
                        INSERT INTO client_scores (client_type, score_value, client_count)
                        VALUES (%s, %s, %s)
                    """
                    score_values = (
                        value.upper(),
                        score_detail.get('scoreValue', -1),
                        score_detail.get('clientCount', 0)
                    )
                    cursor.execute(insert_query, score_values)
                    # Break after inserting 3 rows
                    if cursor.rowcount >= 3:
                        break
        # Break the outer loop as well if 3 rows have been inserted
        if cursor.rowcount >= 3:
            break

    db.commit()

def main():
    db, cursor = connect_db()

    # Create the client_scores table if it doesn't exist
    create_client_scores_table(cursor)

    # Fetch token and data from the API
    token = get_token()
    data = get_data(token)

    # Process and insert data into the database
    insert_client_scores_data(data, cursor, db)

    cursor.close()
    db.close()

if __name__ == "__main__":
    main()