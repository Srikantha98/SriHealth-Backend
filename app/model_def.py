import torch.nn as nn

# -----------------------------
# Model configuration
# -----------------------------
IMAGE_SIZE = 128
NUM_CLASSES = 4

# -----------------------------
# CNN Model Definition
# -----------------------------
class AddNet(nn.Module):
    """
    Convolutional Neural Network for Alzheimer MRI classification.

    Input: 1 × 128 × 128 grayscale MRI image
    Output: 4 Alzheimer disease classes (Mild, Moderate, Non Demented, Very mild)
    """

    def __init__(self):
        super().__init__()

        # Feature extraction layers
        self.features = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),

            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
        )

        # Flatten layer
        self.flatten = nn.Flatten()

        # Classification layers
        self.fc = nn.Sequential(
            nn.Linear(64 * (IMAGE_SIZE // 4) * (IMAGE_SIZE // 4), 128),
            nn.ReLU(),
            nn.Linear(128, NUM_CLASSES)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.flatten(x)  # flatten for FC
        x = self.fc(x)
        return x
