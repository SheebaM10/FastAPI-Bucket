from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import Literal
import os
import uuid
import shutil
import mimetypes

from s3_config import s3_client, BUCKET_NAME

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure subfolders exist
for sub in ["images", "pdfs", "html"]:
    os.makedirs(os.path.join(UPLOAD_FOLDER, sub), exist_ok=True)

def get_mime_type(filename: str):
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"

def upload_to_s3(file_path: str, bucket_subfolder: str, key: str):
    try:
        s3_client.upload_file(file_path, BUCKET_NAME, f"{bucket_subfolder}/{key}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")

@app.post("/upload/{filetype}/")
async def upload_file(filetype: Literal["images", "pdfs", "html"], file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1].lower()

    # Validate file types
    if filetype == "images" and ext not in ("jpg", "jpeg", "png", "gif"):
        raise HTTPException(status_code=400, detail="Invalid image file.")
    if filetype == "pdfs" and ext != "pdf":
        raise HTTPException(status_code=400, detail="Only PDF files allowed.")
    if filetype == "html" and ext != "html":
        raise HTTPException(status_code=400, detail="Only HTML files allowed.")

    unique_filename = f"{uuid.uuid4()}.{ext}"
    save_path = os.path.join(UPLOAD_FOLDER, filetype, unique_filename)

    try:
        # Save locally
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Upload to S3
        upload_to_s3(save_path, filetype, unique_filename)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    return {"uuid": unique_filename, "message": "Upload successful"}

@app.get("/view/{filetype}/{uuid_filename}")
def view_file(filetype: Literal["images", "pdfs", "html"], uuid_filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filetype, uuid_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type=get_mime_type(uuid_filename))

@app.get("/download/{filetype}/{uuid_filename}")
def download_file(filetype: Literal["images", "pdfs", "html"], uuid_filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filetype, uuid_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type=get_mime_type(uuid_filename),
        filename=uuid_filename
    )
