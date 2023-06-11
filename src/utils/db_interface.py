import sqlite3

# Function for verifying user credentials
def verify_credentials(username, password):
    # Connects to database
    conn = sqlite3.connect("src/database/database.db")
    c = conn.cursor()

    # Gets all accounts from database
    c.execute("SELECT * FROM accounts")
    items = c.fetchall()
    conn.commit()

    foundAccount = False

    # Looks for the account in the database
    for account in items:
        databaseUser = account[0]
        databasePass = account[1]

        # Checks if the credentials match 
        if username == databaseUser and password == databasePass:
            foundAccount = True

    # Checks if the account was found
    if foundAccount == True:
        conn.close()
        return "Good!"
    
    else: 
        conn.close()
        return "Bad!"
    
def get_password_salt(username):
    # Connects to database
    conn = sqlite3.connect("src/database/database.db")
    c = conn.cursor()

    # Gets all accounts from database
    c.execute("SELECT * FROM accounts")
    items = c.fetchall()
    conn.commit()

    found_salt = False

    # Finds the salt in the database
    for item in items:
        database_salt = item[4]
        database_username = item[0]

        if username == database_username:
            found_salt = database_salt

    conn.commit()
    conn.close()

    # Returns salt
    return found_salt

def retrieve_user_token(username):
    # Connects to database
    conn = sqlite3.connect("src/database/database.db")
    c = conn.cursor()

    # Gets all accounts from database
    c.execute("SELECT * FROM accounts")
    items = c.fetchall()
    conn.commit()

    found_token = False

    # Gets the token from the database
    for item in items:
        database_username = item[0]
        database_token = item[3]

        if username == database_username:
            found_token = database_token

    # Returns the token
    return found_token