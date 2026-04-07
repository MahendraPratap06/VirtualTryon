import os
import uuid
import aiofiles
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from starlette.requests import Request
from typing import Optional, List
from dotenv import load_dotenv

from uiconfigfile import AppConfig
from src.langchainagenticai.main import run_pipeline

load_dotenv()

app = FastAPI(title=AppConfig.APP_NAME, version=AppConfig.APP_VERSION)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def save_upload(file: UploadFile, suffix: str) -> str:
    ext = file.filename.split(".")[-1].lower()
    if ext not in AppConfig.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type not allowed. Use: {AppConfig.ALLOWED_EXTENSIONS}")
    contents = await file.read()
    if len(contents) > AppConfig.MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"File too large. Max: {AppConfig.MAX_FILE_SIZE_BYTES // (1024*1024)}MB")
    path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{suffix}.png")
    async with aiofiles.open(path, "wb") as f:
        await f.write(contents)
    return path


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/tryon")
async def virtual_tryon(
    # Accept up to 3 person photos
    person_image_1: UploadFile           = File(...),
    person_image_2: Optional[UploadFile] = File(None),
    person_image_3: Optional[UploadFile] = File(None),
    # Garments
    shirt_image:    Optional[UploadFile] = File(None),
    pants_image:    Optional[UploadFile] = File(None),
    dress_image:    Optional[UploadFile] = File(None),
):
    # Validate at least one garment
    shirt_provided = shirt_image and shirt_image.filename
    pants_provided = pants_image and pants_image.filename
    dress_provided = dress_image and dress_image.filename

    if not shirt_provided and not pants_provided and not dress_provided:
        raise HTTPException(status_code=400, detail="Please upload at least one garment.")

    # Save person photos
    person_paths = [await save_upload(person_image_1, "person_1")]

    if person_image_2 and person_image_2.filename:
        person_paths.append(await save_upload(person_image_2, "person_2"))

    if person_image_3 and person_image_3.filename:
        person_paths.append(await save_upload(person_image_3, "person_3"))

    # Save garments
    shirt_path = await save_upload(shirt_image, "shirt") if shirt_provided else None
    pants_path = await save_upload(pants_image, "pants") if pants_provided else None
    dress_path = await save_upload(dress_image, "dress") if dress_provided else None

    # Run pipeline
    result = await run_pipeline(
        person_image_paths=person_paths,
        shirt_image_path=shirt_path,
        pants_image_path=pants_path,
        dress_image_path=dress_path,
    )

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error_message"])

    # Build URL list for all results
    result_urls = [
        f"/static/uploads/{os.path.basename(p)}"
        for p in result["result_images"]
    ]

    return JSONResponse(content={
        "status":             "success",
        "result_image_url":   result_urls[0],
        "result_image_urls":  result_urls,
        "pose_count":         len(result_urls),
    })


@app.get("/health")
async def health():
    return {"status": "ok", "app": AppConfig.APP_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=AppConfig.HOST, port=AppConfig.PORT, reload=AppConfig.RELOAD)