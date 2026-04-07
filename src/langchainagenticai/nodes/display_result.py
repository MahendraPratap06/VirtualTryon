import os
from src.langchainagenticai.state.state import TryOnState


def display_result(state: TryOnState) -> TryOnState:
    """Node 4 — Verify results and clean up temp files."""
    try:
        result_images = state.get("result_images", [])

        if not result_images:
            return {**state, "status": "error", "error_message": "No result images were generated."}

        # Verify all results exist
        for path in result_images:
            if not os.path.exists(path):
                return {**state, "status": "error", "error_message": f"Result image missing: {path}"}

        # Clean up preprocessed images
        for path in state.get("person_images_preprocessed", []):
            if path and os.path.exists(path):
                os.remove(path)

        for key in ["shirt_image_preprocessed", "pants_image_preprocessed", "dress_image_preprocessed"]:
            path = state.get(key)
            if path and os.path.exists(path):
                os.remove(path)

        inter = state.get("intermediate_result_path")
        if inter and os.path.exists(inter):
            os.remove(inter)

        return {**state, "status": "success"}

    except Exception as e:
        return {**state, "status": "error", "error_message": f"Display result failed: {str(e)}"}