import os
from PIL import Image
from src.langchainagenticai.state.state import TryOnState
from uiconfigfile import AppConfig

TARGET_WIDTH  = AppConfig.MAX_WIDTH
TARGET_HEIGHT = AppConfig.MAX_HEIGHT


def _preprocess_single(input_path: str, suffix: str) -> str:
    base, _ = os.path.splitext(input_path)
    output_path = f"{base}_{suffix}_preprocessed.png"
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)
        img.save(output_path, "PNG")
    return output_path


def preprocess_images(state: TryOnState) -> TryOnState:
    """Node 2 — Resize all images to 768x1024 RGB PNG."""
    try:
        # Preprocess all person photos
        person_preprocessed = [
            _preprocess_single(path, f"person_{i+1}")
            for i, path in enumerate(state["person_image_paths"])
        ]

        shirt_preprocessed = _preprocess_single(state["shirt_image_path"], "shirt") if state.get("shirt_image_path") else None
        pants_preprocessed = _preprocess_single(state["pants_image_path"], "pants") if state.get("pants_image_path") else None
        dress_preprocessed = _preprocess_single(state["dress_image_path"], "dress") if state.get("dress_image_path") else None

        return {
            **state,
            "status":                     "preprocessed",
            "person_images_preprocessed": person_preprocessed,
            "shirt_image_preprocessed":   shirt_preprocessed,
            "pants_image_preprocessed":   pants_preprocessed,
            "dress_image_preprocessed":   dress_preprocessed,
        }

    except Exception as e:
        return {**state, "status": "error", "error_message": f"Preprocessing failed: {str(e)}"}