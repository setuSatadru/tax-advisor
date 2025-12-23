"""
AI Advisor Service
Phase 2: Gemini-powered tax-saving suggestions and explanations
"""

import google.generativeai as genai
from typing import Dict, Any, List, Optional
from app.config import settings
from app.models.salary_slip import SalarySlipData, UserTaxProfile, TaxCalculationResult


class AIAdvisor:
    """AI-powered tax advisor using Google Gemini"""
    
    def __init__(self):
        self.model = None
        self.is_configured = False
        self._configure()
    
    def _configure(self):
        """Configure the Gemini API"""
        if settings.gemini_api_key and settings.gemini_api_key != "your_gemini_api_key_here":
            try:
                genai.configure(api_key=settings.gemini_api_key)
                # Using gemini-2.0-flash for fast, free responses
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                self.is_configured = True
            except Exception as e:
                print(f"Failed to configure Gemini: {e}")
                self.is_configured = False
    
    def _build_tax_context(
        self,
        salary_data: SalarySlipData,
        user_profile: UserTaxProfile,
        tax_result: TaxCalculationResult
    ) -> str:
        """Build context string from tax data for the AI prompt"""
        context = f"""
USER TAX PROFILE:
- Annual Gross Salary: ₹{salary_data.gross_salary:,.2f}
- Basic Salary: ₹{salary_data.basic_salary:,.2f}
- HRA Received: ₹{salary_data.hra:,.2f}
- Age: {user_profile.age if user_profile.age else 'Not specified'}
- City Type: {user_profile.city_type if user_profile.city_type else 'Not specified'}
- Rent Paid Annually: ₹{user_profile.rent_paid:,.2f} if user_profile.rent_paid else 'Not paying rent'

CURRENT DEDUCTIONS CLAIMED:
- Section 80C (PPF, ELSS, etc.): ₹{user_profile.section_80c:,.2f} (Max limit: ₹1,50,000)
- Section 80D (Health Insurance): ₹{user_profile.section_80d:,.2f} (Max limit: ₹25,000 for self, ₹50,000 for senior citizens)
- Section 80G (Donations): ₹{user_profile.section_80g:,.2f}
- Section 80TTA (Savings Interest): ₹{user_profile.section_80tta:,.2f} (Max limit: ₹10,000)
- Section 24(b) (Home Loan Interest): ₹{user_profile.section_24b:,.2f} (Max limit: ₹2,00,000)

TAX CALCULATION RESULTS:
OLD REGIME:
- Total Deductions: ₹{tax_result.old_regime['total_deductions']:,.2f}
- Taxable Income: ₹{tax_result.old_regime['taxable_income']:,.2f}
- Total Tax Payable: ₹{tax_result.old_regime['total_tax']:,.2f}
- Effective Tax Rate: {tax_result.old_regime['effective_tax_rate']:.2f}%

NEW REGIME:
- Total Deductions: ₹{tax_result.new_regime['total_deductions']:,.2f}
- Taxable Income: ₹{tax_result.new_regime['taxable_income']:,.2f}
- Total Tax Payable: ₹{tax_result.new_regime['total_tax']:,.2f}
- Effective Tax Rate: {tax_result.new_regime['effective_tax_rate']:.2f}%

RECOMMENDATION: {tax_result.recommended_regime.upper()} Regime
POTENTIAL SAVINGS: ₹{tax_result.savings_amount:,.2f} ({tax_result.savings_percentage:.2f}%)
"""
        return context
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for tax advisor"""
        return """You are an expert Indian tax advisor assistant. Your role is to:
1. Analyze the user's tax profile and calculation results
2. Provide specific, actionable tax-saving suggestions
3. Explain tax concepts in simple, easy-to-understand language
4. Focus on legitimate tax-saving strategies under Indian Income Tax Act

IMPORTANT RULES:
- Only suggest legal tax-saving methods
- Be specific about section numbers and limits
- Provide practical, actionable advice
- Use Indian Rupee (₹) for all amounts
- Keep explanations concise but informative
- Focus on what the user CAN still do to save taxes
- If a deduction is not fully utilized, highlight it
- Consider the user's current situation when suggesting investments

FORMAT YOUR RESPONSE AS JSON with these exact keys:
{
    "summary": "A 2-3 sentence summary of the tax situation",
    "regime_explanation": "Why the recommended regime is better for this user",
    "suggestions": [
        {
            "section": "Section name (e.g., 80C, 80D)",
            "title": "Short title of the suggestion",
            "current_status": "What the user has currently",
            "potential_saving": "How much more they could save",
            "action_items": ["Specific action 1", "Specific action 2"],
            "priority": "high/medium/low"
        }
    ],
    "additional_tips": ["General tip 1", "General tip 2"],
    "disclaimer": "Standard disclaimer about consulting a CA for complex situations"
}"""

    async def generate_tax_suggestions(
        self,
        salary_data: SalarySlipData,
        user_profile: UserTaxProfile,
        tax_result: TaxCalculationResult
    ) -> Dict[str, Any]:
        """Generate AI-powered tax-saving suggestions"""
        
        # Return fallback if not configured
        if not self.is_configured or not self.model:
            return self._get_fallback_suggestions(salary_data, user_profile, tax_result)
        
        try:
            # Build the prompt
            tax_context = self._build_tax_context(salary_data, user_profile, tax_result)
            
            prompt = f"""{self._get_system_prompt()}

Here is the user's tax information:
{tax_context}

Analyze this information and provide personalized tax-saving suggestions. Focus on:
1. Unused deduction potential (especially 80C if not at max)
2. HRA optimization if applicable
3. Health insurance benefits (80D)
4. Any other relevant deductions based on their profile

Respond ONLY with valid JSON, no markdown formatting."""

            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse the response
            response_text = response.text.strip()
            
            # Clean up response if it has markdown code blocks
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                # Remove first and last lines if they are code block markers
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                response_text = "\n".join(lines)
            
            import json
            suggestions = json.loads(response_text)
            suggestions["ai_generated"] = True
            suggestions["error"] = None
            return suggestions
            
        except Exception as e:
            print(f"AI generation error: {e}")
            fallback = self._get_fallback_suggestions(salary_data, user_profile, tax_result)
            fallback["error"] = str(e)
            return fallback
    
    def _get_fallback_suggestions(
        self,
        salary_data: SalarySlipData,
        user_profile: UserTaxProfile,
        tax_result: TaxCalculationResult
    ) -> Dict[str, Any]:
        """Generate rule-based fallback suggestions when AI is not available"""
        
        suggestions = []
        additional_tips = []
        
        # Check 80C utilization
        max_80c = 150000
        remaining_80c = max_80c - user_profile.section_80c
        if remaining_80c > 0:
            suggestions.append({
                "section": "Section 80C",
                "title": "Maximize 80C Deductions",
                "current_status": f"Currently claimed: ₹{user_profile.section_80c:,.0f}",
                "potential_saving": f"You can invest ₹{remaining_80c:,.0f} more (up to ₹1,50,000 limit)",
                "action_items": [
                    "Invest in PPF (Public Provident Fund) - Safe, 7%+ returns",
                    "Consider ELSS mutual funds for tax saving with growth potential",
                    "Life insurance premiums also qualify under 80C"
                ],
                "priority": "high" if remaining_80c > 50000 else "medium"
            })
        
        # Check 80D utilization
        max_80d = 50000 if user_profile.is_senior_citizen else 25000
        remaining_80d = max_80d - user_profile.section_80d
        if remaining_80d > 0:
            suggestions.append({
                "section": "Section 80D",
                "title": "Health Insurance Benefits",
                "current_status": f"Currently claimed: ₹{user_profile.section_80d:,.0f}",
                "potential_saving": f"You can claim ₹{remaining_80d:,.0f} more",
                "action_items": [
                    "Get health insurance if you don't have one",
                    "Consider adding parents to health coverage for additional ₹25,000-50,000 deduction",
                    "Preventive health check-up expenses (up to ₹5,000) also qualify"
                ],
                "priority": "high" if user_profile.section_80d == 0 else "medium"
            })
        
        # Check HRA optimization
        if salary_data.hra > 0 and not user_profile.rent_paid:
            suggestions.append({
                "section": "HRA Exemption",
                "title": "Claim HRA Exemption",
                "current_status": "HRA not being claimed (no rent information provided)",
                "potential_saving": "Significant tax savings possible if you pay rent",
                "action_items": [
                    "If you pay rent, collect rent receipts from landlord",
                    "Get landlord's PAN if annual rent exceeds ₹1,00,000",
                    "Ensure rent agreement is in place"
                ],
                "priority": "high"
            })
        
        # Check Home Loan
        if user_profile.section_24b == 0:
            suggestions.append({
                "section": "Section 24(b)",
                "title": "Home Loan Interest Deduction",
                "current_status": "No home loan interest claimed",
                "potential_saving": "Up to ₹2,00,000 deduction available for self-occupied property",
                "action_items": [
                    "If you have a home loan, claim the interest component",
                    "For under-construction property, interest can be claimed in 5 installments",
                    "Principal repayment qualifies under Section 80C"
                ],
                "priority": "low"
            })
        
        # Check NPS (additional 80CCD)
        additional_tips.append("Consider NPS (National Pension System) for additional ₹50,000 deduction under Section 80CCD(1B)")
        additional_tips.append("Keep all investment proofs and receipts organized for verification")
        additional_tips.append("Submit investment declarations to employer before March for proper TDS deduction")
        
        # Regime-specific explanation
        if tax_result.recommended_regime == "old":
            regime_explanation = (
                f"The Old Regime is better for you because your deductions "
                f"(₹{tax_result.old_regime['total_deductions']:,.0f}) are substantial. "
                f"With significant investments in 80C, health insurance, or HRA claims, "
                f"the old regime allows you to reduce your taxable income significantly."
            )
        else:
            regime_explanation = (
                f"The New Regime is better for you because your current deductions are limited. "
                f"The new regime offers lower tax rates with higher basic exemption, making it "
                f"more beneficial when deductions are below ₹3-4 lakhs."
            )
        
        return {
            "ai_generated": False,
            "error": None,
            "summary": f"Based on your annual income of ₹{salary_data.gross_salary:,.0f}, "
                      f"the {tax_result.recommended_regime.upper()} regime saves you "
                      f"₹{tax_result.savings_amount:,.0f} in taxes.",
            "regime_explanation": regime_explanation,
            "suggestions": suggestions,
            "additional_tips": additional_tips,
            "disclaimer": "This is automated advice based on general rules. For complex tax situations, "
                         "investments, or specific queries, please consult a qualified Chartered Accountant."
        }
    
    def get_section_explanations(self) -> Dict[str, str]:
        """Get explanations for different tax sections"""
        return {
            "80C": """
                <strong>Section 80C</strong> allows deductions up to ₹1,50,000 for investments in:
                PPF, ELSS, NSC, Life Insurance, Principal repayment of home loan, 
                Tuition fees, 5-year Fixed Deposits, and more.
            """,
            "80D": """
                <strong>Section 80D</strong> allows deductions for health insurance premiums:
                Up to ₹25,000 for self/family, additional ₹25,000-50,000 for parents.
                Includes preventive health check-up expenses up to ₹5,000.
            """,
            "HRA": """
                <strong>HRA Exemption</strong> is calculated as minimum of:
                (1) Actual HRA received, (2) Rent paid minus 10% of basic salary,
                (3) 50% of basic for metro cities or 40% for non-metro.
            """,
            "24B": """
                <strong>Section 24(b)</strong> allows deduction of home loan interest:
                Up to ₹2,00,000 for self-occupied property.
                No limit for let-out property (but overall loss capped at ₹2,00,000).
            """,
            "80TTA": """
                <strong>Section 80TTA</strong> allows deduction up to ₹10,000 on 
                interest earned from savings bank accounts. Not applicable to FD interest.
            """,
            "80G": """
                <strong>Section 80G</strong> provides deductions for donations to 
                eligible charitable institutions. Deduction can be 50% or 100% of donation 
                depending on the institution.
            """,
            "standard_deduction": """
                <strong>Standard Deduction</strong> of ₹50,000 is available to all 
                salaried individuals under both tax regimes. This is automatically applied.
            """
        }

