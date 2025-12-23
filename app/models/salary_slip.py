"""
Data Models for Salary Slip
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class SalarySlipData(BaseModel):
    """Parsed salary slip data"""
    # Basic Information
    employee_name: Optional[str] = None
    employee_id: Optional[str] = None
    pan: Optional[str] = None
    month: Optional[str] = None
    year: Optional[int] = None
    
    # Salary Components
    basic_salary: float = 0.0
    dearness_allowance: float = 0.0  # DA
    hra: float = 0.0
    conveyance_allowance: float = 0.0  # Separate from transport
    transport_allowance: float = 0.0  # Keep separate from conveyance
    special_allowance: float = 0.0
    medical_allowance: float = 0.0
    lta: float = 0.0
    bonus: float = 0.0
    other_allowances: float = 0.0
    
    # Gross Salary
    gross_salary: float = 0.0
    
    # Deductions
    pf_employee: float = 0.0
    pf_employer: float = 0.0
    professional_tax: float = 0.0
    income_tax: float = 0.0
    other_deductions: float = 0.0
    
    # Net Salary
    net_salary: float = 0.0
    
    # Metadata
    parsing_confidence: Dict[str, Any] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    assumptions_made: list[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "basic_salary": 500000,
                "hra": 120000,
                "gross_salary": 800000,
                "pf_employee": 60000,
                "net_salary": 720000
            }
        }


class UserTaxProfile(BaseModel):
    """User tax profile data collected via forms"""
    # Personal Information
    age: Optional[int] = None
    is_senior_citizen: bool = False
    
    # HRA Information
    rent_paid: Optional[float] = None
    city_type: Optional[str] = None  # "metro" or "non-metro"
    
    # Deductions
    section_80c: float = 0.0
    section_80d: float = 0.0
    section_80g: float = 0.0
    section_80tta: float = 0.0
    section_24b: float = 0.0  # Home loan interest
    other_deductions: Dict[str, float] = Field(default_factory=dict)
    
    # Additional Information
    has_home_loan: bool = False
    has_health_insurance: bool = False
    has_parents_health_insurance: bool = False
    parents_senior_citizen: bool = False


class TaxCalculationInput(BaseModel):
    """Input for tax calculation"""
    salary_slip: SalarySlipData
    user_profile: UserTaxProfile
    financial_year: str = "2024-25"


class TaxCalculationResult(BaseModel):
    """Tax calculation results"""
    # Old Regime
    old_regime: Dict[str, Any]
    
    # New Regime
    new_regime: Dict[str, Any]
    
    # Comparison
    recommended_regime: str  # "old" or "new"
    savings_amount: float
    savings_percentage: float
    
    # Assumptions
    assumptions: list[str] = Field(default_factory=list)


class TaxSuggestion(BaseModel):
    """Individual tax-saving suggestion"""
    section: str
    title: str
    current_status: str
    potential_saving: str
    action_items: list[str] = Field(default_factory=list)
    priority: str = "medium"  # high, medium, low


class AIInsights(BaseModel):
    """AI-generated tax insights and suggestions"""
    # Metadata
    ai_generated: bool = False
    error: Optional[str] = None
    
    # Content
    summary: str = ""
    regime_explanation: str = ""
    suggestions: list[TaxSuggestion] = Field(default_factory=list)
    additional_tips: list[str] = Field(default_factory=list)
    disclaimer: str = ""
    
    class Config:
        json_schema_extra = {
            "example": {
                "ai_generated": True,
                "summary": "Based on your income, the Old Regime saves you ₹25,000.",
                "suggestions": [
                    {
                        "section": "80C",
                        "title": "Maximize 80C",
                        "current_status": "₹50,000 claimed",
                        "potential_saving": "₹1,00,000 more available",
                        "action_items": ["Invest in PPF", "Consider ELSS"],
                        "priority": "high"
                    }
                ]
            }
        }
