import requests
from requests.auth import HTTPBasicAuth
import mysql.connector
from mysql.connector import Error
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

def get_network_health(token):
    get_health_url = f"https://{CC_IP}/dna/intent/api/v1/network-health"
    headers = {"x-auth-token": token, "content-type": "application/json"}
    response = requests.get(get_health_url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

def connect_db():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()
        return db, cursor
    except mysql.connector.Error as e:
        handle_db_error(e)

def insert_network_health(cursor, db, health_data):
    # Delete existing data to ensure only fresh data is present
    cursor.execute("DELETE FROM network_health_2")


def create_tables(cursor):
    create_network_health_general_table_query = """
    CREATE TABLE IF NOT EXISTS network_health_general (
        id INT AUTO_INCREMENT PRIMARY KEY,
        measured_by VARCHAR(255),
        latest_health_score INT,
        monitored_devices INT,
        monitored_healthy_devices INT,
        monitored_unhealthy_devices INT,
        no_health_devices INT,
        total_devices INT,
        monitored_poor_health_devices INT,
        monitored_fair_health_devices INT
    )
    """
    create_network_health_category_table_query = """
    CREATE TABLE IF NOT EXISTS network_health_category (
        id INT AUTO_INCREMENT PRIMARY KEY,
        network_health_general_id INT,
        category VARCHAR(255),
        health_score INT,
        good_percentage FLOAT,
        bad_percentage FLOAT,
        fair_percentage FLOAT,
        no_health_percentage FLOAT,
        good_count INT,
        bad_count INT,
        fair_count INT,
        no_health_count INT,
        FOREIGN KEY (network_health_general_id) REFERENCES network_health_general(id)
    )
    """
    try:
        cursor.execute(create_network_health_general_table_query)
        cursor.execute(create_network_health_category_table_query)

        # Check if the 'total_count' column exists in the 'network_health_category' table
        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME = 'network_health_category'
            AND COLUMN_NAME = 'total_count'
        """, (DB_CONFIG['database'],))
        result = cursor.fetchone()

        # If the 'total_count' column does not exist, add it
        if not result:
            cursor.execute("""
                ALTER TABLE network_health_category
                ADD COLUMN total_count INT AS (
                    good_count + bad_count + fair_count + no_health_count
                ) STORED;
            """)
            print("Added 'total_count' column to 'network_health_category' table.")

    except mysql.connector.Error as e:
        if e.errno == 1050:  # Error code for 'Table already exists'
            print("Table already exists. Continuing with data insertion.")
        else:
            raise


def insert_network_health(cursor, db, health_data):
    # Delete existing data to ensure only fresh data is present
    cursor.execute("DELETE FROM network_health_category")
    cursor.execute("DELETE FROM network_health_general")

    add_network_health_general_query = """
        INSERT INTO network_health_general(
            measured_by,
            latest_health_score,
            monitored_devices,
            monitored_healthy_devices,
            monitored_unhealthy_devices,
            no_health_devices,
            total_devices,
            monitored_poor_health_devices,
            monitored_fair_health_devices
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    general_health_data = (
        health_data['measuredBy'],
        health_data['latestHealthScore'],
        health_data['monitoredDevices'],
        health_data['monitoredHealthyDevices'],
        health_data['monitoredUnHealthyDevices'],
        health_data['noHealthDevices'],
        health_data['totalDevices'],
        health_data['monitoredPoorHealthDevices'],
        health_data['monitoredFairHealthDevices']
    )
    cursor.execute(add_network_health_general_query, general_health_data)
    network_health_general_id = cursor.lastrowid

    add_network_health_category_query = """
        INSERT INTO network_health_category(
            network_health_general_id,
            category,
            health_score,
            good_percentage,
            bad_percentage,
            fair_percentage,
            no_health_percentage,
            good_count,
            bad_count,
            fair_count,
            no_health_count
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    for category_data in health_data['healthDistirubution']:
        # You will need to extract the additional data from the category_data
        # For example:
        good_percentage = category_data.get('goodPercentage')
        bad_percentage = category_data.get('badPercentage')
        fair_percentage = category_data.get('fairPercentage')
        no_health_percentage = category_data.get('noHealthPercentage')
        good_count = category_data.get('goodCount')
        bad_count = category_data.get('badCount')
        fair_count = category_data.get('fairCount')
        no_health_count = category_data.get('noHealthCount')

        category_health_data = (
            network_health_general_id,
            category_data['category'],
            category_data['healthScore'],
            good_percentage,
            bad_percentage,
            fair_percentage,
            no_health_percentage,
            good_count,
            bad_count,
            fair_count,
            no_health_count
        )
        cursor.execute(add_network_health_category_query, category_health_data)
    
    db.commit()

def main():
    token = get_token()
    health_data = get_network_health(token)
    db, cursor = connect_db()
    create_tables(cursor)
    insert_network_health(cursor, db, health_data)
    cursor.close()
    db.close()

if __name__ == "__main__":
    main()
