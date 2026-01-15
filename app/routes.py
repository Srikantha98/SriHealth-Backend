from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from datetime import datetime
from typing import Dict

from .model import UserRegister, UserLogin, Token
from .database import users_collection, predictions_collection
from .auth import hash_password, verify_password, create_access_token, get_current_user
from .predict import predict_mri

router = APIRouter()


# -----------------------------
# Register a new user
# -----------------------------
@router.post("/auth/register", status_code=201)
def register(user: UserRegister):
    """
    Register a new user.
    Checks for existing email and hashes password before saving to MongoDB.
    """
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    user_dict = {
        "email": user.email,
        "password": hash_password(user.password),
        "created_at": datetime.utcnow(),
        "name": getattr(user, "name", "")
    }

    users_collection.insert_one(user_dict)
    return {"message": "User registered successfully"}


# -----------------------------
# Login user
# -----------------------------
@router.post("/auth/login", response_model=Token)
def login(user: UserLogin):
    """
    Authenticate user and return JWT access token with user info.
    """
    db_user = users_collection.find_one({"email": user.email})

    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token_data = {
        "sub": db_user["email"],
        "name": db_user.get("name", "User")
    }

    token = create_access_token(token_data)

    # Return token and user info for frontend convenience
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "name": db_user.get("name", "User"),
            "email": db_user["email"]
        }
    }


# -----------------------------
# Predict MRI (Protected)
# -----------------------------
@router.post("/predict")
def predict(
    file: UploadFile = File(...),
    current_user_email: str = Depends(get_current_user)
) -> Dict[str, str | float]:
    """
    Predict Alzheimer stage from uploaded MRI.
    Protected endpoint: requires JWT authentication.
    Stores prediction in MongoDB.

    Returns:
        dict: {
            "class": "Mild Dementia",
            "confidence": 92.5
        }
    """
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No MRI file uploaded"
        )

    try:
        # Read image bytes
        image_bytes = file.file.read()

        # Run AddNet prediction
        result: Dict[str, str | float] = predict_mri(image_bytes)

        if "class" not in result or "confidence" not in result:
            raise ValueError("Prediction result must include 'class' and 'confidence'")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prediction failed: {str(e)}"
        )
    finally:
        file.file.close()  # avoid resource leaks

    # Store prediction in MongoDB
    predictions_collection.insert_one({
        "user_email": current_user_email,
        "prediction": result,
        "filename": file.filename,
        "timestamp": datetime.utcnow()
    })

    # Return result to frontend
    return result
