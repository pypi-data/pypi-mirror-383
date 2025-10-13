import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

print("DEBUG: Starting api/database.py...")

# Load environment variables from .env file
load_dotenv()
print("DEBUG: load_dotenv() executed.")

MONGO_DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DEBUG: DATABASE_URL loaded is: '{MONGO_DATABASE_URL}'") # IMPORTANT LINE

# Add a check to prevent crashing if the URL is not found
if not MONGO_DATABASE_URL:
    print("FATAL ERROR: DATABASE_URL not found in .env file or environment!")
    # We exit here to make the error obvious
    exit()

# Set up a client-server session with MongoDB
client = AsyncIOMotorClient(MONGO_DATABASE_URL)
print("DEBUG: Motor client created.")

# Get the specific database and collection
database = client.myapi_db
item_collection = database.get_collection("items")
print("DEBUG: Database and collection are set. api/database.py finished.")