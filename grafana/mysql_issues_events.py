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

def connect_db():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()
        return db, cursor
    except mysql.connector.Error as e:
        handle_db_error(e)


def handle_db_error(e):
    if e.errno == 1050:  # Error code for 'Table already exists'
        print("Table already exists. Skipping table creation.")
    else:
        print(f"Error code: {e.errno}, SQLSTATE: {e.sqlstate}, Message: {e.msg}")
        exit(1)

def create_table(cursor):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS cc_issues (
        id INT AUTO_INCREMENT PRIMARY KEY,
        issue_id VARCHAR(255) UNIQUE,
        category VARCHAR(255),
        priority VARCHAR(255),
        description TEXT,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """
    try:
        cursor.execute(create_table_query)
    except mysql.connector.Error as e:
        if e.errno == 1050:  # Error code for 'Table already exists'
            print("Table already exists. Continuing with data insertion.")
        else:
            raise

def sync_issues(cursor, db, current_issues, token):
    # Get all existing issue IDs from the database
    cursor.execute("SELECT issue_id FROM cc_issues")
    existing_issue_ids = {row[0] for row in cursor.fetchall()}

    # Insert or update current issues
    for issue in current_issues:
        issue_id = issue.get('issueId')
        if issue_id:
            issue_details = get_issue_details(issue_id, token)
            insert_or_update_issue(cursor, db, issue_id, issue_details.get('category'), issue_details.get('priority'), issue_details.get('description'))
            if issue_id in existing_issue_ids:
                existing_issue_ids.remove(issue_id)

    # Remove issues that are no longer present
    for issue_id in existing_issue_ids:
        delete_issue(cursor, db, issue_id)


def insert_or_update_issue(cursor, db, issue_id, category, priority, description):
    try:
        check_query = "SELECT category, priority, description FROM cc_issues WHERE issue_id = %s"
        cursor.execute(check_query, (issue_id,))
        existing_issue = cursor.fetchone()

        if existing_issue and (existing_issue[0], existing_issue[1], existing_issue[2]) != (category, priority, description):
            update_query = "UPDATE cc_issues SET category = %s, priority = %s, description = %s, last_updated = CURRENT_TIMESTAMP WHERE issue_id = %s"
            cursor.execute(update_query, (category, priority, description, issue_id))
        elif not existing_issue:
            insert_query = "INSERT INTO cc_issues (issue_id, category, priority, description) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (issue_id, category, priority, description))
        db.commit()
    except mysql.connector.Error as e:
        print(f"Error inserting or updating data in MySQL table: {e}")

def delete_issue(cursor, db, issue_id):
    delete_query = "DELETE FROM cc_issues WHERE issue_id = %s"
    cursor.execute(delete_query, (issue_id,))
    db.commit()

def main():
    token = get_token()
    issues = get_issues(token)
    db, cursor = connect_db()
    create_table(cursor)
    sync_issues(cursor, db, issues, token)
    cursor.close()
    db.close()
if __name__ == "__main__":
    main()