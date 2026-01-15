import os
from pymongo import MongoClient
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# MongoDB URI from environment
# Example:
# mongodb+srv://username:password@srihealth.mznfvox.mongodb.net/srihealth?retryWrites=true&w=majority&appName=SriHealth
# -----------------------------
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise RuntimeError("❌ MONGODB_URI is not set in environment variables")

# -----------------------------
# Create MongoDB client
# -----------------------------
client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=5000  # prevent hanging if DB is unreachable
)

# -----------------------------
# Select database (explicitly from URI)
# -----------------------------
db = client.get_database()  # uses "srihealth" from your URI

# -----------------------------
# Collections
# -----------------------------
users_collection = db["users"]
predictions_collection = db["predictions"]

# -----------------------------
# Test connection
# -----------------------------
try:
    client.admin.command("ping")
    print("✅ MongoDB connected successfully")
except Exception as e:
    print("❌ MongoDB connection failed:", e)
