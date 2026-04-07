import os
from typing import Optional
from gradio_client import Client, handle_file
from PIL import Image
from src.langchainagenticai.state.state import TryOnState
from dotenv import load_dotenv

load_dotenv()


# ─────────────────────────────────────────────────────────────
# TOKEN HANDLING
# ─────────────────────────────────────────────────────────────
def _get_hf_tokens():
    tokens = []
    for key, value in os.environ.items():
        if key.startswith("HF_TOKEN") and value.strip():
            tokens.append(value.strip())
    return tokens or [None]


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def _save_result(output_path: str, base_dir: str, suffix: str) -> str:
    out_path = os.path.join(base_dir, f"result_{suffix}.png")
    with Image.open(output_path) as img:
        img.save(out_path, "PNG")
    return out_path


def _should_retry(err: str) -> bool:
    err = err.lower()
    return any(x in err for x in [
        "zerogpu", "quota", "429",
        "rate limit", "timeout",
        "503", "502", "runtime_error",
        "paused", "sleeping"
    ])


# ─────────────────────────────────────────────────────────────
# SAFE CLIENT CREATOR (OLD VERSION FIX)
# ─────────────────────────────────────────────────────────────
def _create_client(space_name: str, token: Optional[str]):
    if token:
        os.environ["HF_TOKEN"] = token

    client = Client(space_name)

    # 🔥 FORCE TOKEN INTO HEADERS (IMPORTANT FIX)
    if token:
        try:
            client.session.headers.update({
                "Authorization": f"Bearer {token}"
            })
        except:
            pass

    return client


# ─────────────────────────────────────────────────────────────
# IDM-VTON (UPPER BODY)
# ─────────────────────────────────────────────────────────────
def _run_idm_vton(person_path, garment_path, suffix, base_dir):
    tokens = _get_hf_tokens()
    last_error = None

    for i, token in enumerate(tokens):
        try:
            print(f"🔑 IDM-VTON token {i+1}/{len(tokens)}")

            client = _create_client("yisol/IDM-VTON", token)

            result = client.predict(
                dict={
                    "background": handle_file(person_path),
                    "layers": [],
                    "composite": None
                },
                garm_img=handle_file(garment_path),
                garment_des="upper body shirt top",
                is_checked=True,
                is_checked_crop=False,
                denoise_steps=30,
                seed=42,
                api_name="/tryon"
            )

            print("✅ IDM success")
            return _save_result(result[0], base_dir, suffix)

        except Exception as e:
            last_error = str(e)
            print(f"⚠️ IDM Error: {last_error[:100]}")

            if _should_retry(last_error):
                continue
            break

    raise RuntimeError(f"IDM-VTON failed: {last_error}")


# ─────────────────────────────────────────────────────────────
# FASHN (LOWER / DRESS)
# ─────────────────────────────────────────────────────────────
def _run_fashn(person_path, garment_path, category, suffix, base_dir):
    tokens = _get_hf_tokens()
    last_error = None

    for i, token in enumerate(tokens):
        try:
            print(f"🔑 FASHN token {i+1}/{len(tokens)}")

            client = _create_client("fashn-ai/fashn-vton-1.5", token)

            result = client.predict(
                person_image=handle_file(person_path),
                garment_image=handle_file(garment_path),
                category=category,
                garment_photo_type="model",
                num_timesteps=50,
                guidance_scale=1.5,
                seed=42,
                segmentation_free=True,
                api_name="/try_on"
            )

            result_path = result["path"] if isinstance(result, dict) else result

            print("✅ FASHN success")
            return _save_result(result_path, base_dir, suffix)

        except Exception as e:
            last_error = str(e)
            print(f"⚠️ FASHN Error: {last_error[:100]}")

            if _should_retry(last_error):
                continue
            break

    raise RuntimeError(f"FASHN failed: {last_error}")


# ─────────────────────────────────────────────────────────────
# PIPELINE LOGIC
# ─────────────────────────────────────────────────────────────
def _process_single_person(
    person_path,
    shirt_path: Optional[str],
    pants_path: Optional[str],
    dress_path: Optional[str],
    pose_idx,
    base_dir,
):

    if shirt_path and not pants_path and not dress_path:
        return _run_idm_vton(person_path, shirt_path, f"p{pose_idx}_top", base_dir)

    elif pants_path and not shirt_path and not dress_path:
        return _run_fashn(person_path, pants_path, "bottoms", f"p{pose_idx}_bottom", base_dir)

    elif dress_path and not shirt_path and not pants_path:
        return _run_fashn(person_path, dress_path, "one-pieces", f"p{pose_idx}_dress", base_dir)

    elif shirt_path and pants_path:
        temp = _run_idm_vton(person_path, shirt_path, f"p{pose_idx}_run1_top", base_dir)
        return _run_fashn(temp, pants_path, "bottoms", f"p{pose_idx}_run2_bottom", base_dir)

    elif dress_path and pants_path:
        temp = _run_fashn(person_path, dress_path, "one-pieces", f"p{pose_idx}_run1_dress", base_dir)
        return _run_fashn(temp, pants_path, "bottoms", f"p{pose_idx}_run2_bottom", base_dir)

    raise RuntimeError("No valid garment combination")


# ─────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────
def virtual_tryon(state: TryOnState) -> TryOnState:
    try:
        person_paths = state["person_images_preprocessed"]
        shirt = state.get("shirt_image_preprocessed")
        pants = state.get("pants_image_preprocessed")
        dress = state.get("dress_image_preprocessed")

        base_dir = os.path.dirname(person_paths[0])
        results = []

        for i, person in enumerate(person_paths, 1):
            print(f"\n🧍 Processing {i}/{len(person_paths)}")

            res = _process_single_person(
                person, shirt, pants, dress, i, base_dir
            )

            results.append(res)
            print(f"✅ Done: {res}")

        return {
            **state,
            "status": "tryon_complete",
            "result_image": results[0],
            "result_images": results,
        }

    except Exception as e:
        return {
            **state,
            "status": "error",
            "error_message": str(e)
        }