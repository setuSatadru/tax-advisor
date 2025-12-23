"""
Tax Computation Engine
Phase 1: Deterministic tax calculation for Old vs New Regime
"""

from typing import Dict, Any
from app.models.salary_slip import SalarySlipData, UserTaxProfile, TaxCalculationResult
from app.config import (
    OLD_REGIME_SLABS,
    NEW_REGIME_SLABS,
    STANDARD_DEDUCTION,
    CESS_RATE,
    TAX_DEDUCTION_SECTIONS
)


class TaxCalculator:
    """Deterministic tax calculation engine"""
    
    def calculate_hra_exemption(
        self,
        hra_received: float,
        basic_salary: float,
        rent_paid: float,
        city_type: str
    ) -> float:
        """
        Calculate HRA exemption
        Minimum of:
        1. Actual HRA received
        2. Rent paid - 10% of basic salary
        3. 50% of basic (metro) or 40% of basic (non-metro)
        """
        if not rent_paid or rent_paid <= 0:
            return 0.0
        
        # Calculate 10% of basic
        ten_percent_basic = basic_salary * 0.10
        
        # Calculate city-based limit
        if city_type == "metro":
            city_limit = basic_salary * 0.50
        else:
            city_limit = basic_salary * 0.40
        
        # Calculate rent minus 10% basic
        rent_minus_ten_percent = rent_paid - ten_percent_basic
        
        # Return minimum of three
        exemption = min(
            hra_received,
            rent_minus_ten_percent,
            city_limit
        )
        
        return max(0.0, exemption)
    
    def calculate_tax_by_slabs(self, taxable_income: float, slabs: list) -> float:
        """Calculate tax based on income slabs"""
        tax = 0.0
        remaining_income = taxable_income
        
        for slab in slabs:
            min_income = slab["min"]
            max_income = slab["max"]
            rate = slab["rate"] / 100
            
            if remaining_income <= 0:
                break
            
            if taxable_income > min_income:
                slab_income = min(remaining_income, max_income - min_income)
                if slab_income > 0:
                    tax += slab_income * rate
                    remaining_income -= slab_income
        
        return tax
    
    def calculate_old_regime(
        self,
        salary_data: SalarySlipData,
        user_profile: UserTaxProfile
    ) -> Dict[str, Any]:
        """Calculate tax under Old Regime"""
        # Gross Salary
        gross_salary = salary_data.gross_salary
        
        # Standard Deduction
        standard_deduction = STANDARD_DEDUCTION
        
        # HRA Exemption
        hra_exemption = 0.0
        if salary_data.hra > 0 and user_profile.rent_paid:
            hra_exemption = self.calculate_hra_exemption(
                salary_data.hra,
                salary_data.basic_salary,
                user_profile.rent_paid,
                user_profile.city_type or "non-metro"
            )
        
        # Section 80C (max 1.5L)
        section_80c = min(user_profile.section_80c, TAX_DEDUCTION_SECTIONS["80C"]["max_limit"])
        
        # Section 80D
        if user_profile.is_senior_citizen:
            max_80d = TAX_DEDUCTION_SECTIONS["80D"]["max_limit_senior"]
        else:
            max_80d = TAX_DEDUCTION_SECTIONS["80D"]["max_limit"]
        section_80d = min(user_profile.section_80d, max_80d)
        
        # Section 80G
        section_80g = user_profile.section_80g
        
        # Section 80TTA (max 10K)
        section_80tta = min(user_profile.section_80tta, TAX_DEDUCTION_SECTIONS["80TTA"]["max_limit"])
        
        # Section 24(b) - Home Loan Interest (max 2L for self-occupied)
        section_24b = min(user_profile.section_24b, TAX_DEDUCTION_SECTIONS["24B"]["max_limit"])
        
        # Total Deductions
        total_deductions = (
            standard_deduction +
            hra_exemption +
            section_80c +
            section_80d +
            section_80g +
            section_80tta +
            section_24b
        )
        
        # Taxable Income
        taxable_income = max(0, gross_salary - total_deductions)
        
        # Calculate Tax
        tax_before_cess = self.calculate_tax_by_slabs(taxable_income, OLD_REGIME_SLABS)
        
        # Add Cess
        cess = tax_before_cess * CESS_RATE
        total_tax = tax_before_cess + cess
        
        return {
            "gross_salary": gross_salary,
            "standard_deduction": standard_deduction,
            "hra_exemption": hra_exemption,
            "section_80c": section_80c,
            "section_80d": section_80d,
            "section_80g": section_80g,
            "section_80tta": section_80tta,
            "section_24b": section_24b,
            "total_deductions": total_deductions,
            "taxable_income": taxable_income,
            "tax_before_cess": tax_before_cess,
            "cess": cess,
            "total_tax": total_tax,
            "effective_tax_rate": (total_tax / gross_salary * 100) if gross_salary > 0 else 0
        }
    
    def calculate_new_regime(
        self,
        salary_data: SalarySlipData,
        user_profile: UserTaxProfile
    ) -> Dict[str, Any]:
        """Calculate tax under New Regime"""
        # Gross Salary
        gross_salary = salary_data.gross_salary
        
        # Standard Deduction
        standard_deduction = STANDARD_DEDUCTION
        
        # New Regime: No other deductions allowed
        # (HRA, 80C, 80D, etc. are not applicable)
        
        # Taxable Income
        taxable_income = max(0, gross_salary - standard_deduction)
        
        # Calculate Tax
        tax_before_cess = self.calculate_tax_by_slabs(taxable_income, NEW_REGIME_SLABS)
        
        # Add Cess
        cess = tax_before_cess * CESS_RATE
        total_tax = tax_before_cess + cess
        
        return {
            "gross_salary": gross_salary,
            "standard_deduction": standard_deduction,
            "total_deductions": standard_deduction,
            "taxable_income": taxable_income,
            "tax_before_cess": tax_before_cess,
            "cess": cess,
            "total_tax": total_tax,
            "effective_tax_rate": (total_tax / gross_salary * 100) if gross_salary > 0 else 0
        }
    
    def calculate(self, salary_data: SalarySlipData, user_profile: UserTaxProfile) -> TaxCalculationResult:
        """Main calculation method"""
        # Calculate both regimes
        old_regime_result = self.calculate_old_regime(salary_data, user_profile)
        new_regime_result = self.calculate_new_regime(salary_data, user_profile)
        
        # Compare and recommend
        old_tax = old_regime_result["total_tax"]
        new_tax = new_regime_result["total_tax"]
        
        if old_tax < new_tax:
            recommended = "old"
            savings = new_tax - old_tax
        else:
            recommended = "new"
            savings = old_tax - new_tax
        
        savings_percentage = (savings / max(old_tax, new_tax) * 100) if max(old_tax, new_tax) > 0 else 0
        
        # Collect assumptions
        assumptions = []
        if not user_profile.rent_paid and salary_data.hra > 0:
            assumptions.append("HRA exemption not calculated (rent paid not provided)")
        if user_profile.section_80c == 0:
            assumptions.append("No Section 80C investments declared")
        
        return TaxCalculationResult(
            old_regime=old_regime_result,
            new_regime=new_regime_result,
            recommended_regime=recommended,
            savings_amount=round(savings, 2),
            savings_percentage=round(savings_percentage, 2),
            assumptions=assumptions
        )

