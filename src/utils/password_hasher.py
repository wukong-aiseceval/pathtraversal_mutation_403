import hashlib
import utils.db_interface as database

# Function for getting the password hash using the salt in the database
# Requires username to find the hash associated with the password
def get_hash_with_database_salt(username, password):
    # Gets the salt from the database
    salt = database.get_password_salt(username)
  
    # Adding salt at the last of the password
    dataBase_password = password+salt
    # Encoding the password
    hashed = hashlib.sha256(dataBase_password.encode())
    
    # Returns the password hash 
    return hashed.hexdigest()