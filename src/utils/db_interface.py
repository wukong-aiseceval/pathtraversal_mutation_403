import secrets
import yaml
import uuid
import mysql.connector

# Global database connection
db_connection = None

# Load config.yml
# Run by the main file after the config checks have been completed
def load_config():
    global configurations

    with open("config.yml", "r") as config:
        contents = config.read()
        configurations = yaml.safe_load(contents)

# Function to establish a database connection
def connect_to_database():
    # Handle connecting to the database
    def connect():
        global db_connection
        db_connection = mysql.connector.connect(
            host=configurations['mysql-host'],
            user=configurations['mysql-user'],
            password=configurations['mysql-password'],
            database=configurations['mysql-database']
        )
    
    # Check if there is a MySQL connection
    if db_connection is None:
        connect()
    else:
        # Check if existing connection is still alive
        if not db_connection.is_connected():
            connect()

# Function for verifying user credentials
def verify_credentials(username, password):
    if password is None:
        return "Bad!"
    
    else:
        connect_to_database()
        cursor = db_connection.cursor()

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
    cursor = db_connection.cursor()

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
    cursor = db_connection.cursor()

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
    cursor = db_connection.cursor()

    # Gets all accounts from the MySQL database
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (username,))
    item = cursor.fetchone()

    found_username = False

    # Set 'found_username' to 'True' if username was found
    if item:
        found_username = True

    cursor.close()

    # Returns the status
    return found_username

def check_email(email):
    connect_to_database()
    cursor = db_connection.cursor()

    found_email = False

    # Get email from MySQL database
    cursor.execute("SELECT * FROM accounts WHERE email = %s", (email,))
    item = cursor.fetchone()

    # Set 'found_email' to 'True' if email was found
    if item:
        found_email = True

    cursor.close()

    # Returns the status
    return found_email

def create_account(username, email, password, password_salt):
    connect_to_database()

    # Define database cursor
    cursor = db_connection.cursor()

    # Generate user token
    token = str(secrets.token_hex(16 // 2))

    # Generate user id
    user_id = str(uuid.uuid4()) 

    cursor.execute("INSERT INTO accounts (username, password, email, token, salt, bio, pronouns, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                   (username, password, email, token, password_salt, None, None, user_id))

    db_connection.commit()
    cursor.close()

def check_token(username: str, token: str):
    connect_to_database()
    cursor = db_connection.cursor()

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
    cursor = db_connection.cursor()

    # Grab user info from database
    cursor.execute("UPDATE accounts SET bio = %s WHERE username = %s", (data, username))
    db_connection.commit()

    return "Ok"

def update_user_pronouns(username, data):
    connect_to_database()
    cursor = db_connection.cursor()

    # Update pronouns in database
    cursor.execute("UPDATE accounts SET pronouns = %s WHERE username = %s", (data, username))
    db_connection.commit()

    return "Ok"

def get_bio(username):
    connect_to_database()
    cursor = db_connection.cursor()

    cursor.execute("SELECT * FROM accounts WHERE username = %s", (username,))
    data = cursor.fetchone()

    return data[6]

def get_pronouns(username):
    connect_to_database()
    cursor = db_connection.cursor()

    cursor.execute("SELECT * FROM accounts WHERE username = %s", (username,))
    data = cursor.fetchone()

    return data[7]

def update_user_salt(username: str, salt: str):
    connect_to_database()
    cursor = db_connection.cursor()

    # Update salt in database
    cursor.execute("UPDATE accounts SET salt = %s WHERE username = %s", (salt, username))
    db_connection.commit()

def update_password(username: str, password: str):
    connect_to_database()
    cursor = db_connection.cursor()

    # Update password in database
    cursor.execute("UPDATE accounts SET password = %s WHERE username = %s", (password, username))
    db_connection.commit()

def get_user_email(username: str):
    connect_to_database()
    cursor = db_connection.cursor()

    cursor.execute("SELECT * FROM accounts WHERE username = %s", (username,))
    data = cursor.fetchone()

    return data[3]

def get_username(account_id: str):
    connect_to_database()
    cursor = db_connection.cursor()

    cursor.execute("SELECT * FROM accounts WHERE user_id = %s", (account_id,))
    data = cursor.fetchone()

    return data[1]