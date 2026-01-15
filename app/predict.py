import os
import io
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image

from .model_def import AddNet

# -----------------------------
# Device configuration
# -----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -----------------------------
# Class names (must match training order)
# -----------------------------
CLASS_NAMES = [
    "Mild Dementia",
    "Moderate Dementia",
    "Non Demented",
    "Very mild Dementia"
]

# -----------------------------
# Load trained model
# -----------------------------
model = AddNet().to(device)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "addnet_model.pth")

model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

# -----------------------------
# Image preprocessing pipeline
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

# -----------------------------
# Prediction function
# -----------------------------
def predict_mri(image_bytes: bytes) -> dict:
    """
    Run MRI image through AddNet CNN and return predicted class and confidence.

    Args:
        image_bytes (bytes): MRI image in bytes.

    Returns:
        dict: {
            "class": "Mild Dementia",
            "confidence": 92.5  # in percentage
        }
    """
    try:
        # Load and convert image to grayscale
        image = Image.open(io.BytesIO(image_bytes)).convert("L")
    except Exception as e:
        raise ValueError(f"Invalid image file: {e}")

    # Preprocess image and add batch dimension
    image_tensor = transform(image).unsqueeze(0).to(device)

    # Forward pass
    with torch.no_grad():
        outputs = model(image_tensor)
        probs = F.softmax(outputs, dim=1)  # Convert logits to probabilities
        conf, pred_idx = torch.max(probs, dim=1)  # Max probability and index

    return {
        "class": CLASS_NAMES[pred_idx.item()],
        "confidence": round(conf.item() * 100, 2)
    }
