import asyncio
import websockets
import json
import utils.db_interface as database
import utils.password_hasher as hasher

# Main thread for handling the connection
async def websocket_server(websocket, path):
    # Handle incoming messages from the client
    async for message in websocket:
        # Checks if the client is trying to log in
        if message == "USER_LOGIN":
            # Asks the client for the credentials
            await websocket.send("SEND_CREDENTIALS")

            # Waits for the client to send credentials
            credentials = await websocket.recv()
            
            # Loads the credentials from json
            loaded_credentials = json.loads(credentials)

            # Verifies the credentials with the database
            username = loaded_credentials['Username']
            password = hasher.get_hash_with_database_salt(username=username, password=loaded_credentials['Password'])

            verify_status = database.verify_credentials(username=username, password=password)

            # Checks the status of the credential verification
            if verify_status == 'Good!':
                # Gets the token from database
                token = database.retrieve_user_token(username)

                # Sends token to the client
                await websocket.send(token) 

            else: 
                await websocket.send("INVALID_CREDENTIALS")

async def start_server():
    server = await websockets.serve(websocket_server, 'localhost', 9000)
    await server.wait_closed()

asyncio.run(start_server())
