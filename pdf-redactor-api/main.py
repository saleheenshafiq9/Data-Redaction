from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
import uuid
import logging
from extract_files import extract_layout
from detect_pii import detect_pii
from redact_regions import redact_and_extract_regions

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow CORS from any Chrome extension
# In production, you should restrict this to your specific extension ID
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, use your specific extension ID
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename}")
    
    # Check if it's a PDF (based on content type or extension)
    if not file.content_type == "application/pdf" and not file.filename.lower().endswith('.pdf'):
        logger.warning(f"File rejected: {file.content_type} is not a PDF")
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
        
        # Read and save the file
        contents = await file.read()
        logger.info(f"Read {len(contents)} bytes")
        
        with open(file_path, "wb") as f:
            f.write(contents)
        logger.info(f"Saved to {file_path}")

        layout_info = await extract_layout(file_path)
        logger.info(f"Extracted {len(layout_info)} text spans with coords")

        pii_spans = await detect_pii(layout_info) 
        logger.info(f"Found {len(pii_spans)} PII spans")
        
        redaction_info = await redact_and_extract_regions(file_path, pii_spans)
        # This is a placeholder for your actual processing logic
        analysis_result = {
            "file_id": file_id,
            "original_name": file.filename,
            "size_bytes": len(contents),
            "path": file_path,
            # Add your analysis results here
            "layout": layout_info,
            "pii_spans": pii_spans,
            "redacted_pdf": redaction_info["redacted_pdf"],
            "redaction_regions": redaction_info["regions"]
        }
        
        logger.info("Processing complete")
        return JSONResponse(content={
            "status": "success",
            "message": "PDF successfully uploaded and processed",
            "result": analysis_result
        })
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/")
async def root():
    return {"message": "PDF Redactor API is running"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting PDF Redactor API server")
    uvicorn.run(app, host="0.0.0.0", port=8000)