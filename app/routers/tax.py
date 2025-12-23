"""
Tax Calculation Router
Phase 2: Tax computation with AI-powered suggestions
"""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from app.services.tax_calculator import TaxCalculator
from app.services.ai_advisor import AIAdvisor
from app.models.salary_slip import SalarySlipData, UserTaxProfile
from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
calculator = TaxCalculator()
ai_advisor = AIAdvisor()


@router.post("/calculate", response_class=HTMLResponse)
async def calculate_tax(
    request: Request,
    # Salary Slip Data
    basic_salary: float = Form(...),
    dearness_allowance: float = Form(0.0),
    hra: float = Form(0.0),
    conveyance_allowance: float = Form(0.0),
    transport_allowance: float = Form(0.0),
    special_allowance: float = Form(0.0),
    medical_allowance: float = Form(0.0),
    lta: float = Form(0.0),
    bonus: float = Form(0.0),
    gross_salary: float = Form(...),
    pf_employee: float = Form(0.0),
    professional_tax: float = Form(0.0),
    income_tax: float = Form(0.0),
    net_salary: float = Form(0.0),
    # User Profile
    age: Optional[int] = Form(None),
    rent_paid: Optional[float] = Form(None),
    city_type: Optional[str] = Form(None),
    section_80c: float = Form(0.0),
    section_80d: float = Form(0.0),
    section_80g: float = Form(0.0),
    section_80tta: float = Form(0.0),
    section_24b: float = Form(0.0),
):
    """Calculate tax and display summary with AI suggestions"""
    try:
        # Build SalarySlipData
        salary_data = SalarySlipData(
            basic_salary=basic_salary,
            dearness_allowance=dearness_allowance,
            hra=hra,
            conveyance_allowance=conveyance_allowance,
            transport_allowance=transport_allowance,
            special_allowance=special_allowance,
            medical_allowance=medical_allowance,
            lta=lta,
            bonus=bonus,
            gross_salary=gross_salary,
            pf_employee=pf_employee,
            professional_tax=professional_tax,
            income_tax=income_tax,
            net_salary=net_salary
        )
        
        # Build UserTaxProfile
        user_profile = UserTaxProfile(
            age=age,
            is_senior_citizen=(age >= 60) if age else False,
            rent_paid=rent_paid,
            city_type=city_type,
            section_80c=section_80c,
            section_80d=section_80d,
            section_80g=section_80g,
            section_80tta=section_80tta,
            section_24b=section_24b,
            has_home_loan=(section_24b > 0),
            has_health_insurance=(section_80d > 0)
        )
        
        # Calculate tax
        result = calculator.calculate(salary_data, user_profile)
        
        # Generate AI suggestions (Phase 2)
        ai_insights = await ai_advisor.generate_tax_suggestions(
            salary_data, user_profile, result
        )
        
        # Get section explanations
        section_explanations = ai_advisor.get_section_explanations()
        
        # Convert Pydantic models to dicts for JSON serialization in template
        salary_data_dict = salary_data.model_dump()
        user_profile_dict = user_profile.model_dump()
        result_dict = result.model_dump()
        
        # Display summary
        return templates.TemplateResponse(
            "summary.html",
            {
                "request": request,
                "title": "Tax Summary",
                "salary_data": salary_data_dict,
                "user_profile": user_profile_dict,
                "result": result_dict,
                "ai_insights": ai_insights,
                "section_explanations": section_explanations
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating tax: {str(e)}")
