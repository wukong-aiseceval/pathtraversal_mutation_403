import secrets
import yaml
import mysql.connector

# Global database connection
conn = None

# Load config.yml
# Run by the main file after the config checks have been completed
def load_config():
    global configurations

    with open("config.yml", "r") as config:
        contents = config.read()
        configurations = yaml.safe_load(contents)

# Function to establish a database connection
def connect_to_database():
    global conn
    if conn is None:
        conn = mysql.connector.connect(
            host=configurations['mysql-host'],
            user=configurations['mysql-user'],
            password=configurations['mysql-password'],
            database=configurations['mysql-database']
        )

# Function for verifying user credentials
def verify_credentials(username, password):
    if password is None:
        return "Bad!"
    
    else:
        connect_to_database()
        cursor = conn.cursor()

        # Gets all accounts from the MySQL database
        cursor.execute("SELECT * FROM accounts")
        items = cursor.fetchall()

        foundAccount = False

        # Looks for the account in the database
        for account in items:
            databaseUser = account[1]
            databasePass = account[2]

            # Checks if the credentials match
            if username == databaseUser and password == databasePass:
                foundAccount = True

        cursor.close()

        # Checks if the account was found
        if foundAccount:
            return "Good!"
        else:
            return "Bad!"

def get_password_salt(username):
    connect_to_database()
    cursor = conn.cursor()

    # Gets the salt for the given username from the MySQL database
    cursor.execute("SELECT salt FROM accounts WHERE username = %s", (username,))
    result = cursor.fetchone()

    cursor.close()

    if result is not None:
        return result[0]  # Return the salt value if found
    else:
        return False  # Return False if no matching username is found

def retrieve_user_token(username):
    connect_to_database()
    cursor = conn.cursor()

    # Gets all accounts from the MySQL database
    cursor.execute("SELECT * FROM accounts")
    items = cursor.fetchall()

    found_token = False

    # Gets the token from the MySQL database
    for item in items:
        database_username = item[1]
        database_token = item[4]

        if username == database_username:
            found_token = database_token

    cursor.close()

    # Returns the token
    return found_token

def check_username(username):
    connect_to_database()
    cursor = conn.cursor()

    # Gets all accounts from the MySQL database
    cursor.execute("SELECT * FROM accounts")
    items = cursor.fetchall()

    found_username = False

    # Search for username in the MySQL database
    for item in items:
        database_username = item[0]

        if username == database_username:
            found_username = True

    cursor.close()

    # Returns the status
    return found_username

def check_email(email):
    connect_to_database()
    cursor = conn.cursor()

    # Gets all accounts from the MySQL database
    cursor.execute("SELECT * FROM accounts")
    items = cursor.fetchall()

    found_email = False

    # Search for email in the MySQL database
    for item in items:
        database_email = item[2]

        if email == database_email:
            found_email = True

    cursor.close()

    # Returns the status
    return found_email

def create_account(username, email, password, password_salt):
    connect_to_database()
    cursor = conn.cursor()

    # Generate user token
    token = str(secrets.token_hex(16 // 2))

    cursor.execute("INSERT INTO accounts (username, password, email, token, salt) VALUES (%s, %s, %s, %s, %s)",
                   (username, password, email, token, password_salt))

    conn.commit()
    cursor.close()

def check_token(username: str, token: str):
    connect_to_database()
    cursor = conn.cursor()

    # Gets all accounts from the MySQL database
    cursor.execute("SELECT * FROM accounts")
    items = cursor.fetchall()

    found_token = False

    for user in items:
        database_user = user[1]
        database_token = user[4]

        if database_user == username and database_token == token:
            found_token = True

    return found_token

def update_user_bio(username, data):
    connect_to_database()
    cursor = conn.cursor()

    # Grab user info from database
    cursor.execute("UPDATE accounts SET bio = %s WHERE username = %s", (data, username))
    conn.commit()

    return "Ok"

def update_user_pronouns(username, data):
    connect_to_database()
    cursor = conn.cursor()

    # Grab user info from database
    cursor.execute("UPDATE accounts SET pronouns = %s WHERE username = %s", (data, username))
    conn.commit()

    return "Ok"

def get_bio(username):
    connect_to_database()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM accounts WHERE username = %s", (username,))
    data = cursor.fetchone()

    return data[6]

def get_pronouns(username):
    connect_to_database()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM accounts WHERE username = %s", (username,))
    data = cursor.fetchone()

    return data[7]