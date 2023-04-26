import sqlite3

# Function for verifying user credentials
def verifyCredentials(username, password):
    # Connects to database
    conn = sqlite3.connect("src/database.db")
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