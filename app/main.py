"""
GenAI-Based Tax Advisor for Individuals
Main FastAPI Application Entry Point
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Tax Advisor",
    description="GenAI-Based Tax Advisor for Salaried Individuals in India",
    version="0.1.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
from app.routers import upload, tax, chat, pages
app.include_router(upload.router, tags=["upload"])
app.include_router(tax.router, tags=["tax"])
app.include_router(chat.router, tags=["chat"])
app.include_router(pages.router, tags=["pages"])


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - Landing page of the Tax Advisor"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Tax Advisor - Home"}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Tax Advisor API is running"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)

