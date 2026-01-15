from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import ConnectionFailure
from app.routes import router as api_router
from app.database import db  # MongoDB database object

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(
    title="SriHealth Alzheimer Prediction API",
    description="Backend API for Alzheimer Disease Prediction using MRI",
    version="1.0.0",
)

# -----------------------------
# CORS (allow frontend access)
# -----------------------------
origins = [
    "http://localhost:5173",                  # React local dev
    "https://your-frontend-domain.vercel.app"  # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Include API routes
# -----------------------------
app.include_router(api_router)

# -----------------------------
# Root endpoint
# -----------------------------
@app.get("/")
def root():
    """Root endpoint to verify API is running."""
    return {"message": "Welcome to SriHealth Alzheimer Prediction API"}

# -----------------------------
# MongoDB test endpoint
# -----------------------------
@app.get("/test-db")
def test_db():
    """
    Test MongoDB connection by listing collections.
    """
    try:
        collections = db.list_collection_names()
        return {"status": "connected ✅", "collections": collections}
    except ConnectionFailure as e:
        return {"status": "failed ❌", "error": str(e)}
    except Exception as e:
        return {"status": "failed ❌", "error": str(e)}

# -----------------------------
# Startup event to check DB connection
# -----------------------------
@app.on_event("startup")
def startup_event():
    """
    Startup event: ping MongoDB to verify connectivity.
    """
    try:
        # db.command("ping") works, but safer via client
        db.client.admin.command("ping")
        print("✅ MongoDB connected successfully")
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
