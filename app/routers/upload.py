"""
Upload Router - Salary Slip Upload and Parsing
Phase 1: PDF upload and hybrid parsing
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import shutil
from pathlib import Path
from app.services.pdf_parser import SalarySlipParser
from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
parser = SalarySlipParser()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Display upload page"""
    return templates.TemplateResponse(
        "upload.html",
        {"request": request, "title": "Upload Salary Slip"}
    )


@router.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    """Handle salary slip upload and parsing"""
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > settings.max_upload_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.max_upload_size / (1024*1024)}MB"
        )
    
    # Save file temporarily
    file_path = os.path.join(settings.upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
    
    try:
        # Parse the PDF
        salary_data, missing_fields = parser.parse(file_path)
        
        # Store parsed data in session (for prototype, we'll pass via query params or form)
        # In production, use proper session management
        
        # Redirect to form page with parsed data
        return templates.TemplateResponse(
            "form.html",
            {
                "request": request,
                "title": "Confirm & Complete Information",
                "salary_data": salary_data,
                "missing_fields": missing_fields,
                "parsing_confidence": salary_data.parsing_confidence
            }
        )
    
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")
    
    finally:
        # Clean up uploaded file after parsing (security: don't store PDFs)
        if os.path.exists(file_path):
            os.remove(file_path)

