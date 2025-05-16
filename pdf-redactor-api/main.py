from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
import logging
import json

from extract_files import extract_layout
from detect_pii import detect_pii
from redact_regions import redact_and_extract_regions
from restore_pdf import restore_pdf_by_uuid

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow CORS (restrict to your extension ID in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "PDF Redactor API is running"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename}")

    # Validate PDF
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    try:
        # Save original PDF
        file_id   = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
        contents  = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        logger.info(f"Saved to {file_path}")

        # 1) Ingestion & Preprocessing
        layout_info = await extract_layout(file_path)
        logger.info(f"Extracted {len(layout_info)} text spans")

        # 2) Sensitive-info Detection
        pii_spans = await detect_pii(layout_info)
        logger.info(f"Found {len(pii_spans)} PII spans")

        # 3) Redaction & Metadata Linking
        redaction_info = await redact_and_extract_regions(file_path, pii_spans)
        logger.info("Redaction complete")

        # Build sidecar metadata
        sidecar = {"regions": redaction_info["regions"]}

        # Response includes redacted PDF path and sidecar JSON
        analysis_result = {
            "file_id": file_id,
            "original_name": file.filename,
            "size_bytes": len(contents),
            "path": file_path,
            "layout": layout_info,
            "pii_spans": pii_spans,
            "redacted_pdf": redaction_info["redacted_pdf"],
            "sidecar": sidecar
        }

        return JSONResponse({
            "status": "success",
            "message": "PDF uploaded and redacted",
            "result": analysis_result
        })

    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/restore")
async def restore_pdf_endpoint(
    file: UploadFile = File(...),
    sidecar: str      = Form(...)   # sidecar JSON as form field
):
    logger.info(f"Restoring PDF: {file.filename}")

    try:
        # 1) Save the uploaded redacted PDF
        tmp_id   = str(uuid.uuid4())
        redacted_path = os.path.join(UPLOAD_DIR, f"{tmp_id}_redacted.pdf")
        data     = await file.read()
        with open(redacted_path, "wb") as f:
            f.write(data)

        # 2) Parse sidecar JSON
        sidecar_obj = json.loads(sidecar)
        # Build lookup map: uuid -> region record
        sidecar_map = {r["uuid"]: r for r in sidecar_obj["regions"]}

        # 3) Restore
        restored_path = restore_pdf_by_uuid(redacted_path, sidecar_map)
        logger.info(f"Restored PDF saved to: {restored_path}")

        # 4) Send back restored PDF
        return FileResponse(
            restored_path,
            media_type="application/pdf",
            filename=os.path.basename(restored_path)
        )

    except Exception as e:
        logger.error(f"Error restoring PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting PDF Redactor API server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
