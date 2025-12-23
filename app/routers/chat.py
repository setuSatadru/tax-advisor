"""
Chat Router
Phase 3: Conversational Q&A endpoints
"""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import uuid
import json
from app.services.chat_advisor import chat_advisor

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/chat/start")
async def start_chat_session(
    request: Request,
    salary_data: str = Form(...),
    user_profile: str = Form(...),
    tax_result: str = Form(...)
):
    """Start a new chat session with tax context"""
    try:
        # Parse JSON data
        salary_data_dict = json.loads(salary_data)
        user_profile_dict = json.loads(user_profile)
        tax_result_dict = json.loads(tax_result)
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create chat session
        chat_advisor.create_session(
            session_id,
            salary_data_dict,
            user_profile_dict,
            tax_result_dict
        )
        
        # Return chat page
        return templates.TemplateResponse(
            "chat.html",
            {
                "request": request,
                "title": "Tax Advisor Chat",
                "session_id": session_id,
                "salary_data": salary_data_dict,
                "user_profile": user_profile_dict,
                "tax_result": tax_result_dict
            }
        )
    
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting chat: {str(e)}")


@router.post("/chat/message")
async def send_message(
    request: Request,
    session_id: str = Form(...),
    message: str = Form(...)
):
    """Send a message and get AI response"""
    try:
        if not message.strip():
            return JSONResponse({
                "success": False,
                "error": "Message cannot be empty"
            })
        
        # Get AI response
        response = await chat_advisor.get_response(session_id, message.strip())
        
        return JSONResponse({
            "success": True,
            "response": response
        })
    
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get conversation history for a session"""
    try:
        session = chat_advisor.get_session(session_id)
        
        if not session:
            return JSONResponse({
                "success": False,
                "error": "Session not found"
            })
        
        history = []
        for msg in session.messages:
            history.append({
                "role": msg.role,
                "content": msg.content,
                "metadata": msg.metadata,
                "timestamp": msg.timestamp
            })
        
        return JSONResponse({
            "success": True,
            "history": history
        })
    
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })


@router.get("/chat/suggestions")
async def get_suggestions():
    """Get suggested questions for the chat"""
    suggestions = [
        {
            "category": "Tax Savings",
            "questions": [
                "How can I save more tax under 80C?",
                "What are the best ELSS mutual funds?",
                "Should I invest in NPS for additional tax benefits?"
            ]
        },
        {
            "category": "Deductions",
            "questions": [
                "How is HRA exemption calculated?",
                "Can I claim both home loan and HRA?",
                "What qualifies under Section 80D?"
            ]
        },
        {
            "category": "Scenarios",
            "questions": [
                "What if I invest ₹1,00,000 more in 80C?",
                "What if I start paying rent of ₹20,000/month?",
                "What if I get health insurance for my parents?"
            ]
        },
        {
            "category": "Regime Selection",
            "questions": [
                "Why is the new regime better for me?",
                "When should I choose the old regime?",
                "Can I switch regimes next year?"
            ]
        }
    ]
    
    return JSONResponse({
        "success": True,
        "suggestions": suggestions
    })

