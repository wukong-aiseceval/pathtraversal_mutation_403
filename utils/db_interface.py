import sqlite3

# Function for verifying user credentials
def verify_credentials(username, password):
    if password == False:
        return "Bad!"
    
    else:
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
    # Connects to the database
    conn = sqlite3.connect("src/database/database.db")
    c = conn.cursor()

    # Gets the salt for the given username from the database
    c.execute("SELECT salt FROM accounts WHERE username = ?", (username,))
    result = c.fetchone()

    conn.commit()
    conn.close()

    if result is not None:
        return result[0]  # Return the salt value if found
    else:
        return False  # Return False if no matching username is found

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