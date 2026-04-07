import os
from PIL import Image
from src.langchainagenticai.state.state import TryOnState


def validate_images(state: TryOnState) -> TryOnState:
    """Node 1 — Validate all uploaded images."""
    try:
        person_paths = state["person_image_paths"]
        shirt_path   = state.get("shirt_image_path")
        pants_path   = state.get("pants_image_path")
        dress_path   = state.get("dress_image_path")

        def _check(path: str, label: str):
            if not os.path.exists(path):
                return f"{label} not found on disk."
            try:
                with Image.open(path) as img:
                    img.verify()
            except Exception:
                return f"{label} is corrupted or invalid."
            return None

        # Validate person photos
        if not person_paths:
            return {**state, "status": "error", "error_message": "Please upload at least one person photo."}

        for i, path in enumerate(person_paths, 1):
            err = _check(path, f"Person photo {i}")
            if err:
                return {**state, "status": "error", "error_message": err}

        # At least one garment required
        if not shirt_path and not pants_path and not dress_path:
            return {**state, "status": "error", "error_message": "Please upload at least one garment."}

        # Validate garments
        for path, label in [(shirt_path, "Shirt"), (pants_path, "Pants"), (dress_path, "Dress")]:
            if path:
                err = _check(path, label)
                if err:
                    return {**state, "status": "error", "error_message": err}

        return {**state, "status": "validated"}

    except Exception as e:
        return {**state, "status": "error", "error_message": f"Validation failed: {str(e)}"}