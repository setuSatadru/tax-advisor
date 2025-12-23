"""
Static Pages Router
Phase 4: Privacy, Disclaimers, and Help pages
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/privacy", response_class=HTMLResponse)
async def privacy_page(request: Request):
    """Privacy policy and data handling information"""
    return templates.TemplateResponse(
        "privacy.html",
        {"request": request, "title": "Privacy & Data Handling"}
    )


@router.get("/disclaimer", response_class=HTMLResponse)
async def disclaimer_page(request: Request):
    """Redirect to privacy page with disclaimers"""
    return templates.TemplateResponse(
        "privacy.html",
        {"request": request, "title": "Disclaimers"}
    )

