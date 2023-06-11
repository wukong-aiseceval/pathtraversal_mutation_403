import asyncio
import websockets
import json
import rsa
import utils.db_interface as database
import utils.password_hasher as hasher

# Class for holding client data
class ClientData:
    def __init__(self):
        self.private_key = None
        self.public_key = None

# Main thread for handling the connection
async def websocket_server(websocket, path):
    client = ClientData()

    # Handle incoming messages from the client
    async for message in websocket:
        # Checks if the client requested a handshake
        if message == "HANDSHAKE":
            # Generate a rsa key pair
            pub_key, priv_key = rsa.newkeys(1024)

            # Exports the keys to clint data class
            client.public_key = pub_key.save_pkcs1("PEM")
            client.private_key = priv_key.save_pkcs1("PEM")

            # Send the public key to the client
            await websocket.send(client.public_key)

        # Checks if the client is trying to log in
        if message == "USER_LOGIN":
            # Asks the client for the credentials
            await websocket.send("SEND_CREDENTIALS")

            # Waits for the client to send credentials
            encrypted_credentials = await websocket.recv()

            print(encrypted_credentials)

            # Loads the private key from client data
            loaded_private_key = rsa.PrivateKey.load_pkcs1(client.private_key)

            # Decrypt the credentials using the server's private key
            credentials = rsa.decrypt(encrypted_credentials.encode(), loaded_private_key)
            
            # Loads the credentials from json
            loaded_credentials = json.loads(credentials)

            # Verifies the credentials with the database
            username = loaded_credentials['Username']
            password = hasher.get_hash_with_database_salt(username=username, password=loaded_credentials['Password'])

            verify_status = database.verify_credentials(username=username, password=password)

            # Checks the status of the credential verification
            if verify_status == 'Good!':
                # Asks the client for their public key so the server can send the user token
                await websocket.send("PUB_KEY?")

                # Waits for client response
                client_public_key = await websocket.recv()

                # Gets the token from database
                token = database.retrieve_user_token(username)

                # Encrypts the token with the clients public key
                encrypted_token = False

                # Sends token to the client
                await websocket.send(encrypted_token) 

            else: 
                await websocket.send("INVALID_CREDENTIALS")

async def start_server():
    server = await websockets.serve(websocket_server, 'localhost', 9000)
    await server.wait_closed()

asyncio.run(start_server())
