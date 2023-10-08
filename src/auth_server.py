from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from utils import db_interface as database
from utils import password_hasher as hasher
from utils import email_checker as email_interface

app = FastAPI()

# Check setup
print("Checking user images folder...")
if os.path.isdir("user_images") == False:
    os.mkdir("user_images")
    print("Created 'user_images' directory!")

if os.path.isdir("user_images/pfp") == False:
    os.mkdir("user_images/pfp")
    print("Created 'user_images/pfp' directory!")

if os.path.isdir("user_images/banner") == False:
    os.mkdir("user_images/banner")
    print("Created 'user_images/banner' directory!")

# Check location of assets folder
if os.path.isdir("assets"):
    assets_folder = "assets"

else: 
    assets_folder = "src/assets"

print("Setup check complete!")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return "Welcome to Lif Auth Server!"

@app.get("/login/{username}/{password}")
async def login(username: str, password: str):
    # Gets password hash
    password_hash = hasher.get_hash_with_database_salt(username=username, password=password)

    # Checks if password hash was successful
    if not password_hash:
        return {"Status": "Unsuccessful", "Token": "None"}

    # Verifies credentials with database
    status = database.verify_credentials(username=username, password=password_hash)

    if status == "Good!":
        # Gets token from database
        token = database.retrieve_user_token(username=username)

        # Returns info to client
        return {"Status": "Successful", "Token": token}
    else:
        # Tells client credentials are incorrect
        return {"Status": "Unsuccessful", "Token": "None"}

@app.get("/verify_token/{username}/{token}")
async def verify_token(username: str, token: str):
    # Gets token from database
    database_token = database.retrieve_user_token(username=username)

    if not database_token:
        return {"Status": "Unsuccessful"}
    elif database_token == token:
        return {"Status": "Successful"}
    else:
        return {"Status": "Unsuccessful"}

@app.get("/get_pfp/{username}")
async def get_pfp(username: str):
    # Checks if the user has a profile pic uploaded
    if os.path.isfile(f"user_images/pfp/{username}"):
        return FileResponse(f"user_images/pfp/{username}", media_type='image/gif')
    else:
        # Returns default image if none is uploaded
        return FileResponse(f'{assets_folder}/default_pfp.png', media_type='image/gif')

@app.get("/get_banner/{username}")
async def get_banner(username: str):
    # Checks if the user has a profile pic uploaded
    if os.path.isfile(f"user_images/banner/{username}"):
        return FileResponse(f"user_images/banner/{username}", media_type='image/gif')
    else:
        # Returns default image if none is uploaded
        return FileResponse(f'{assets_folder}/default_banner.png', media_type='image/gif')
    
@app.post("/create_lif_account")
async def create_lif_account(request: Request):
    # Get POST data
    data = await request.json()
    username = data["username"]
    password = data["password"]
    email = data["email"]

    # Check username usage
    username_status = database.check_username(username)
    if username_status:
        raise HTTPException(status_code=409, detail="Username Already in Use!")

    # Check email usage
    email_status = database.check_email(email)
    if email_status:
        raise HTTPException(status_code=409, detail="Email Already in Use!")

    # Check if email is valid
    email_isValid = email_interface.is_valid_email(email)
    if not email_isValid:
        raise HTTPException(status_code=400, detail="Invalid Email!")

    # Hash user password
    password_hash = hasher.get_hash_gen_salt(password)

    # Create user account
    database.create_account(username=username, password=password_hash['password'], email=email, password_salt=password_hash['salt'])

    return {"Status": "Ok"}  

@app.get("/check_account_info_usage/{type}/{info}")
async def check_account_info_usage(type: str, info: str):
    if type == "username":
        # Check username usage
        username_status = database.check_username(info)
        if username_status:
            raise HTTPException(status_code=409, detail="Username Already in Use!")
        else:
            return {"Status": "Ok"}

    if type == "email":
        # Check email usage
        email_status = database.check_email(info)
        if email_status:
            raise HTTPException(status_code=409, detail="Email Already in Use!")
        else:
            return {"Status": "Ok"}

    if type == "emailValid":
        # Check if email is valid
        email_isValid = email_interface.is_valid_email(info)
        if not email_isValid:
            raise HTTPException(status_code=400, detail="Invalid Email!")
        else:
            return {"Status": "Ok"}

@app.get("/create_account/{username}/{email}/{password}")
async def create_account(username: str, email: str, password: str):
    # Check username usage
    username_status = database.check_username(username)
    if username_status:
        return {"status": "unsuccessful", "reason": "Username Already in Use!"}

    # Check email usage
    email_status = database.check_email(email)
    if email_status:
        return {"status": "unsuccessful", "reason": "Email Already in Use!"}

    # Check if email is valid
    email_isValid = email_interface.is_valid_email(email)
    if not email_isValid:
        return {"status": "unsuccessful", "reason": "Email is Invalid!"}

    # Hash user password
    password_hash = hasher.get_hash_gen_salt(password)

    # Create user account
    database.create_account(username=username, password=password_hash['password'], email=email, password_salt=password_hash['salt'])

    return {"status": "ok"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
