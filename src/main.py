import asyncio
import websockets
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import json
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
            # Generate an RSA key pair
            client.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )

            # Extract the public key
            client.public_key = client.private_key.public_key()

            # Serialize the public key in PEM format
            pem_public_key = client.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            # Send the public key to the client
            await websocket.send(pem_public_key.decode())

        # Checks if the client is trying to log in
        if message == "USER_LOGIN":
            # Asks the client for the credentials
            await websocket.send("SEND_CREDENTIALS")

            # Waits for the client to send credentials
            encrypted_credentials = await websocket.recv()

            # Decrypt the credentials using the server's private key
            decrypted_credentials = client.private_key.decrypt(
                encrypted_credentials,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # Save the credentials as a single variable
            credentials = decrypted_credentials.decode()
            
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
                encrypted_token = client_public_key.encrypt(
                    token.encode(),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )

                # Sends token to the client
                await websocket.send(encrypted_token) 

            else: 
                await websocket.send("INVALID_CREDENTIALS")

async def start_server():
    server = await websockets.serve(websocket_server, 'localhost', 9000)
    await server.wait_closed()

asyncio.run(start_server())
