import os
from pymongo import MongoClient
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# MongoDB URI
# -----------------------------
MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError("❌ MONGODB_URI is not set in environment variables")

# -----------------------------
# Create MongoDB client (with TLS)
# -----------------------------
client = MongoClient(
    MONGODB_URI,
    tls=True,                       # force TLS 1.2+
    tlsAllowInvalidCertificates=True,  # Render SSL workaround
    serverSelectionTimeoutMS=5000   # prevent hanging if DB is unreachable
)

# -----------------------------
# Select database
# -----------------------------
db = client.get_database()  # uses database from URI, or you can do db = client["srihealth"]

# -----------------------------
# Collections
# -----------------------------
users_collection = db["users"]
predictions_collection = db["predictions"]

print("✅ MongoDB connected successfully")
