"""
Configuration and Constants
Phase 0: Scope and Tax Sections Definition
"""

from typing import List, Dict
import os


class Settings:
    """Application settings"""
    def __init__(self):
        # API Keys
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        
        # App Settings
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.debug: bool = os.getenv("DEBUG", "True").lower() == "true"
        
        # File Upload Settings
        self.max_upload_size: int = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions: List[str] = [".pdf"]
        self.upload_dir: str = "uploads"
        
        # Database
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///./tax_advisor.db")


# Phase 0: Define Tax Sections and Scope
# ======================================

# Supported Tax Deduction Sections (for salaried individuals)
TAX_DEDUCTION_SECTIONS = {
    "80C": {
        "name": "Section 80C",
        "max_limit": 150000,
        "description": "Investments in PPF, ELSS, NSC, Life Insurance Premium, etc.",
        "examples": ["PPF", "ELSS", "NSC", "Life Insurance Premium", "Principal Repayment of Home Loan"]
    },
    "80D": {
        "name": "Section 80D",
        "max_limit": 25000,  # For self
        "max_limit_senior": 50000,  # For senior citizens
        "description": "Health Insurance Premium",
        "examples": ["Health Insurance Premium (Self)", "Health Insurance Premium (Parents)"]
    },
    "80G": {
        "name": "Section 80G",
        "max_limit": None,  # Varies
        "description": "Donations to Charitable Institutions",
        "examples": ["Donations"]
    },
    "80TTA": {
        "name": "Section 80TTA",
        "max_limit": 10000,
        "description": "Interest on Savings Account",
        "examples": ["Savings Account Interest"]
    },
    "80TTB": {
        "name": "Section 80TTB",
        "max_limit": 50000,
        "description": "Interest on Deposits (Senior Citizens)",
        "examples": ["Fixed Deposit Interest (Senior Citizens)"]
    },
    "HRA": {
        "name": "House Rent Allowance (HRA)",
        "max_limit": None,  # Calculated based on salary components
        "description": "HRA exemption based on rent paid, salary, and location",
        "calculation_based": True
    },
    "24B": {
        "name": "Section 24(b) - Home Loan Interest",
        "max_limit": 200000,  # For self-occupied property
        "description": "Interest on Home Loan",
        "examples": ["Home Loan Interest"]
    },
    "80EE": {
        "name": "Section 80EE",
        "max_limit": 50000,
        "description": "Additional deduction on Home Loan Interest (First-time homebuyers)",
        "examples": ["Additional Home Loan Interest"]
    },
    "80EEA": {
        "name": "Section 80EEA",
        "max_limit": 150000,
        "description": "Deduction on Home Loan Interest (Affordable Housing)",
        "examples": ["Affordable Housing Loan Interest"]
    },
    "80EEB": {
        "name": "Section 80EEB",
        "max_limit": 150000,
        "description": "Deduction on Interest on Loan for Electric Vehicle",
        "examples": ["Electric Vehicle Loan Interest"]
    }
}

# Tax Slabs for Old Regime (FY 2024-25)
OLD_REGIME_SLABS = [
    {"min": 0, "max": 250000, "rate": 0},
    {"min": 250000, "max": 500000, "rate": 5},
    {"min": 500000, "max": 1000000, "rate": 20},
    {"min": 1000000, "max": float('inf'), "rate": 30}
]

# Tax Slabs for New Regime (FY 2024-25)
NEW_REGIME_SLABS = [
    {"min": 0, "max": 300000, "rate": 0},
    {"min": 300000, "max": 700000, "rate": 5},
    {"min": 700000, "max": 1000000, "rate": 10},
    {"min": 1000000, "max": 1200000, "rate": 15},
    {"min": 1200000, "max": 1500000, "rate": 20},
    {"min": 1500000, "max": float('inf'), "rate": 30}
]

# Standard Deduction (applicable to both regimes)
STANDARD_DEDUCTION = 50000

# Health and Education Cess
CESS_RATE = 0.04  # 4% on tax

# Phase 0: Explicit Exclusions
# ============================
EXCLUDED_FEATURES = [
    "Form 16 processing",
    "User authentication and login",
    "Freelancer income",
    "Pension income",
    "Self-employed income",
    "Capital gains",
    "Other income sources beyond salary"
]

# Supported Salary Slip Fields
SALARY_SLIP_FIELDS = {
    "basic_salary": "Basic Salary",
    "dearness_allowance": "Dearness Allowance",
    "hra": "House Rent Allowance",
    "conveyance_allowance": "Conveyance Allowance",
    "transport_allowance": "Transport Allowance",
    "special_allowance": "Special Allowance",
    "medical_allowance": "Medical Allowance",
    "lta": "Leave Travel Allowance",
    "bonus": "Bonus",
    "gross_salary": "Gross Salary",
    "pf_employee": "PF (Employee Contribution)",
    "pf_employer": "PF (Employer Contribution)",
    "professional_tax": "Professional Tax",
    "income_tax": "Income Tax (TDS)",
    "net_salary": "Net Salary"
}

settings = Settings()

