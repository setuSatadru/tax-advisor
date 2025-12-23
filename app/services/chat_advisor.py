"""
Chat Advisor Service
Phase 3: Conversational Q&A with LLM for post-analysis queries
"""

import google.generativeai as genai
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re
from app.config import settings
from app.models.salary_slip import SalarySlipData, UserTaxProfile, TaxCalculationResult


class ChatMessage:
    """Represents a single chat message"""
    def __init__(self, role: str, content: str, metadata: Dict[str, Any] = None):
        self.role = role  # "user" or "assistant"
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()


class ChatSession:
    """Manages a conversation session with context"""
    def __init__(
        self,
        salary_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        tax_result: Dict[str, Any]
    ):
        self.salary_data = salary_data
        self.user_profile = user_profile
        self.tax_result = tax_result
        self.messages: List[ChatMessage] = []
        self.created_at = datetime.now().isoformat()
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to the conversation history"""
        self.messages.append(ChatMessage(role, content, metadata))
    
    def get_conversation_history(self, limit: int = 10) -> str:
        """Get formatted conversation history for context"""
        recent_messages = self.messages[-limit:] if len(self.messages) > limit else self.messages
        history = []
        for msg in recent_messages:
            role_label = "User" if msg.role == "user" else "Tax Advisor"
            history.append(f"{role_label}: {msg.content}")
        return "\n".join(history)


class ChatAdvisor:
    """AI-powered conversational tax advisor using Google Gemini"""
    
    def __init__(self):
        self.model = None
        self.is_configured = False
        self._configure()
        self.sessions: Dict[str, ChatSession] = {}
    
    def _configure(self):
        """Configure the Gemini API"""
        if settings.gemini_api_key and settings.gemini_api_key != "your_gemini_api_key_here":
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                self.is_configured = True
            except Exception as e:
                print(f"Failed to configure Gemini: {e}")
                self.is_configured = False
    
    def create_session(
        self,
        session_id: str,
        salary_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        tax_result: Dict[str, Any]
    ) -> ChatSession:
        """Create a new chat session with tax context"""
        session = ChatSession(salary_data, user_profile, tax_result)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get an existing chat session"""
        return self.sessions.get(session_id)
    
    def _build_tax_context(self, session: ChatSession) -> str:
        """Build context string from tax data"""
        salary = session.salary_data
        profile = session.user_profile
        result = session.tax_result
        
        context = f"""
USER'S TAX PROFILE (Current Financial Year):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Income Details:
- Annual Gross Salary: ₹{salary.get('gross_salary', 0):,.2f}
- Basic Salary: ₹{salary.get('basic_salary', 0):,.2f}
- HRA Received: ₹{salary.get('hra', 0):,.2f}
- Special Allowance: ₹{salary.get('special_allowance', 0):,.2f}

Personal Details:
- Age: {profile.get('age', 'Not specified')}
- City Type: {profile.get('city_type', 'Not specified')}
- Annual Rent Paid: ₹{profile.get('rent_paid', 0):,.2f}

Current Deductions Claimed:
- Section 80C: ₹{profile.get('section_80c', 0):,.2f} / ₹1,50,000 (max)
- Section 80D: ₹{profile.get('section_80d', 0):,.2f} / ₹25,000 (max for non-senior)
- Section 80G: ₹{profile.get('section_80g', 0):,.2f}
- Section 80TTA: ₹{profile.get('section_80tta', 0):,.2f} / ₹10,000 (max)
- Section 24(b): ₹{profile.get('section_24b', 0):,.2f} / ₹2,00,000 (max)

TAX CALCULATION RESULTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OLD REGIME:
- Total Deductions: ₹{result.get('old_regime', {}).get('total_deductions', 0):,.2f}
- Taxable Income: ₹{result.get('old_regime', {}).get('taxable_income', 0):,.2f}
- Total Tax Payable: ₹{result.get('old_regime', {}).get('total_tax', 0):,.2f}

NEW REGIME:
- Total Deductions: ₹{result.get('new_regime', {}).get('total_deductions', 0):,.2f}
- Taxable Income: ₹{result.get('new_regime', {}).get('taxable_income', 0):,.2f}
- Total Tax Payable: ₹{result.get('new_regime', {}).get('total_tax', 0):,.2f}

RECOMMENDED REGIME: {result.get('recommended_regime', 'N/A').upper()}
SAVINGS: ₹{result.get('savings_amount', 0):,.2f}
"""
        return context
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for conversational Q&A"""
        return """You are an expert Indian Tax Advisor AI assistant. You are having a conversation with a user who has just completed their tax calculation and wants to ask follow-up questions.

YOUR CAPABILITIES:
1. Answer questions about Indian income tax for salaried individuals
2. Explain tax concepts in simple, easy-to-understand language
3. Explore hypothetical scenarios ("What if I invest ₹50,000 more in 80C?")
4. Provide specific, actionable tax-saving advice
5. Clarify assumptions and provide confidence levels in your answers

IMPORTANT RULES:
1. Only discuss legal tax-saving methods under Indian Income Tax Act
2. Use the user's actual tax data provided in context for personalized answers
3. When answering hypotheticals, show BEFORE and AFTER calculations
4. Always be transparent about assumptions you're making
5. Provide confidence levels (High/Medium/Low) for recommendations
6. If uncertain, clearly state it and suggest consulting a CA
7. Use Indian Rupee (₹) format for all amounts
8. Keep responses concise but informative

RESPONSE FORMAT:
Always structure your response as JSON with these keys:
{
    "answer": "Your main response to the user's question (can include markdown formatting)",
    "confidence": "high/medium/low",
    "confidence_reason": "Brief explanation of why this confidence level",
    "assumptions": ["List of assumptions made in this answer"],
    "scenario_calculation": {
        "applicable": true/false,
        "before": {"description": "...", "tax": 0},
        "after": {"description": "...", "tax": 0},
        "savings": 0
    },
    "follow_up_suggestions": ["Suggested follow-up questions the user might ask"],
    "disclaimer": "Any important caveats or disclaimers"
}

For scenario calculations, only include if the user is asking a "what if" question."""

    def _detect_scenario_question(self, question: str) -> bool:
        """Detect if the question is a scenario/hypothetical question"""
        scenario_patterns = [
            r'what if',
            r'what happens if',
            r'if i invest',
            r'if i pay',
            r'if i claim',
            r'if i increase',
            r'if i decrease',
            r'if i start',
            r'if i get',
            r'what would happen',
            r'how much.*if',
            r'suppose i',
            r'assuming i',
            r'can i save.*by',
            r'would it help if',
        ]
        question_lower = question.lower()
        return any(re.search(pattern, question_lower) for pattern in scenario_patterns)
    
    async def get_response(
        self,
        session_id: str,
        user_question: str
    ) -> Dict[str, Any]:
        """Get AI response to user's question"""
        
        session = self.get_session(session_id)
        if not session:
            return self._get_error_response("Session not found. Please start a new calculation.")
        
        # Add user message to history
        session.add_message("user", user_question)
        
        # Check if AI is configured
        if not self.is_configured or not self.model:
            return self._get_fallback_response(session, user_question)
        
        try:
            # Build the prompt
            tax_context = self._build_tax_context(session)
            conversation_history = session.get_conversation_history(limit=6)
            is_scenario = self._detect_scenario_question(user_question)
            
            prompt = f"""{self._get_system_prompt()}

USER'S TAX DATA:
{tax_context}

CONVERSATION HISTORY:
{conversation_history}

CURRENT QUESTION: {user_question}

{"This appears to be a SCENARIO/HYPOTHETICAL question. Please include detailed before/after calculations in your response." if is_scenario else ""}

Respond ONLY with valid JSON. No markdown code blocks."""

            # Generate response
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response if it has markdown code blocks
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                response_text = "\n".join(lines)
            
            # Parse the response
            result = json.loads(response_text)
            result["ai_generated"] = True
            result["is_scenario"] = is_scenario
            
            # Add assistant response to history
            session.add_message("assistant", result.get("answer", ""), {
                "confidence": result.get("confidence"),
                "is_scenario": is_scenario
            })
            
            return result
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract useful content
            return self._get_fallback_response(session, user_question, 
                                               error=f"Failed to parse AI response: {e}")
        except Exception as e:
            return self._get_fallback_response(session, user_question, 
                                               error=str(e))
    
    def _get_fallback_response(
        self, 
        session: ChatSession, 
        question: str,
        error: str = None
    ) -> Dict[str, Any]:
        """Generate a rule-based fallback response"""
        question_lower = question.lower()
        
        # Common question patterns and responses
        if any(word in question_lower for word in ['80c', 'ppf', 'elss', 'lic']):
            answer = self._get_80c_response(session)
        elif any(word in question_lower for word in ['80d', 'health', 'insurance', 'medical']):
            answer = self._get_80d_response(session)
        elif any(word in question_lower for word in ['hra', 'rent', 'house rent']):
            answer = self._get_hra_response(session)
        elif any(word in question_lower for word in ['regime', 'old', 'new', 'which is better']):
            answer = self._get_regime_response(session)
        elif any(word in question_lower for word in ['nps', 'pension', '80ccd']):
            answer = self._get_nps_response(session)
        elif any(word in question_lower for word in ['home loan', 'housing loan', '24b', '24(b)']):
            answer = self._get_home_loan_response(session)
        else:
            answer = self._get_generic_response(session)
        
        response = {
            "answer": answer,
            "confidence": "medium",
            "confidence_reason": "This is a rule-based response. For more personalized advice, ensure Gemini API is configured.",
            "assumptions": ["Based on general tax rules for FY 2024-25", "Assuming salaried individual taxpayer"],
            "scenario_calculation": {"applicable": False},
            "follow_up_suggestions": [
                "What are the best 80C investment options?",
                "Should I choose old or new tax regime?",
                "How can I maximize my HRA exemption?"
            ],
            "disclaimer": "This is automated advice. Please consult a Chartered Accountant for complex situations.",
            "ai_generated": False,
            "is_scenario": False
        }
        
        if error:
            response["error"] = error
        
        # Add to history
        session.add_message("assistant", answer, {"confidence": "medium"})
        
        return response
    
    def _get_80c_response(self, session: ChatSession) -> str:
        current_80c = session.user_profile.get('section_80c', 0)
        remaining = max(0, 150000 - current_80c)
        
        return f"""**Section 80C Deductions**

You have currently invested **₹{current_80c:,.0f}** under Section 80C.

{"✅ Great! You've maximized your 80C limit." if remaining == 0 else f"💡 You can invest **₹{remaining:,.0f} more** to reach the ₹1,50,000 limit."}

**Popular 80C Investment Options:**
1. **PPF** - Safe, 7.1% interest, 15-year lock-in
2. **ELSS Mutual Funds** - Equity-linked, 3-year lock-in, potential high returns
3. **Life Insurance Premium** - Term insurance recommended
4. **NSC** - 5-year lock-in, fixed returns
5. **5-Year Tax Saver FD** - Low risk, fixed returns
6. **Home Loan Principal** - If applicable

{"**Potential Tax Savings:** If you invest the remaining ₹" + f"{remaining:,.0f}, you could save approximately ₹{remaining * 0.3:,.0f} in taxes (assuming 30% tax bracket)." if remaining > 0 else ""}
"""

    def _get_80d_response(self, session: ChatSession) -> str:
        current_80d = session.user_profile.get('section_80d', 0)
        is_senior = session.user_profile.get('age', 0) and session.user_profile.get('age', 0) >= 60
        max_limit = 50000 if is_senior else 25000
        remaining = max(0, max_limit - current_80d)
        
        return f"""**Section 80D - Health Insurance Deductions**

Your current 80D claim: **₹{current_80d:,.0f}**

**Deduction Limits:**
- Self & Family: Up to ₹{max_limit:,.0f}
- Parents (if under 60): Additional ₹25,000
- Parents (if 60+): Additional ₹50,000
- Preventive Health Check-up: ₹5,000 (within overall limit)

{"✅ You've maximized your basic 80D limit." if remaining == 0 else f"💡 You can claim **₹{remaining:,.0f} more** for health insurance premiums."}

**Tips:**
1. Consider adding parents to your health insurance for extra deduction
2. Keep receipts for preventive health check-ups
3. Super top-up policies also qualify for 80D
"""

    def _get_hra_response(self, session: ChatSession) -> str:
        hra = session.salary_data.get('hra', 0)
        rent = session.user_profile.get('rent_paid', 0)
        basic = session.salary_data.get('basic_salary', 0)
        city = session.user_profile.get('city_type', 'non-metro')
        
        if not rent:
            return f"""**HRA (House Rent Allowance) Exemption**

Your HRA component: **₹{hra:,.0f}** per annum

⚠️ **You haven't declared rent paid.** If you pay rent, you can claim HRA exemption.

**HRA Calculation:**
Minimum of:
1. Actual HRA received
2. Rent paid minus 10% of basic salary
3. 50% of basic (metro) or 40% of basic (non-metro)

**To claim HRA:**
- Collect rent receipts from your landlord
- Get landlord's PAN if rent > ₹1,00,000/year
- Maintain rent agreement
"""
        else:
            # Calculate HRA exemption
            ten_percent_basic = basic * 0.10
            city_limit = basic * 0.50 if city == "metro" else basic * 0.40
            rent_minus_ten = rent - ten_percent_basic
            exemption = min(hra, rent_minus_ten, city_limit)
            exemption = max(0, exemption)
            
            return f"""**HRA (House Rent Allowance) Exemption**

**Your Details:**
- HRA Received: ₹{hra:,.0f}
- Rent Paid: ₹{rent:,.0f}
- Basic Salary: ₹{basic:,.0f}
- City Type: {city.title()}

**HRA Exemption Calculation:**
1. Actual HRA: ₹{hra:,.0f}
2. Rent - 10% of Basic: ₹{rent_minus_ten:,.0f}
3. {50 if city == 'metro' else 40}% of Basic: ₹{city_limit:,.0f}

**Your HRA Exemption: ₹{exemption:,.0f}** (minimum of above three)
"""

    def _get_regime_response(self, session: ChatSession) -> str:
        result = session.tax_result
        recommended = result.get('recommended_regime', 'new')
        old_tax = result.get('old_regime', {}).get('total_tax', 0)
        new_tax = result.get('new_regime', {}).get('total_tax', 0)
        savings = result.get('savings_amount', 0)
        
        return f"""**Old vs New Tax Regime Comparison**

**Your Tax Calculation:**
| Regime | Total Tax |
|--------|-----------|
| Old Regime | ₹{old_tax:,.0f} |
| New Regime | ₹{new_tax:,.0f} |

**Recommendation: {recommended.upper()} REGIME**
You save **₹{savings:,.0f}** by choosing the {recommended} regime.

**Key Differences:**

| Feature | Old Regime | New Regime |
|---------|-----------|------------|
| 80C, 80D, etc. | ✅ Allowed | ❌ Not Allowed |
| HRA Exemption | ✅ Allowed | ❌ Not Allowed |
| Standard Deduction | ₹50,000 | ₹50,000 |
| Tax Rates | Higher | Lower |

**When to choose Old Regime:**
- High deductions (>₹3-4 lakhs)
- Claiming HRA
- Significant 80C investments

**When to choose New Regime:**
- Low/no deductions
- Simpler tax filing preferred
- Higher income with fewer investments
"""

    def _get_nps_response(self, session: ChatSession) -> str:
        return """**NPS (National Pension System) Tax Benefits**

**Section 80CCD(1):**
- Part of overall 80C limit of ₹1,50,000
- Employee contribution to NPS

**Section 80CCD(1B):**
- **Additional ₹50,000** deduction
- Over and above 80C limit
- Only in OLD REGIME

**Section 80CCD(2):**
- Employer contribution to NPS
- Up to 10% of salary (14% for govt employees)
- Available in both regimes!

**Example Savings:**
If you invest ₹50,000 in NPS under 80CCD(1B):
- 30% bracket: Save ~₹15,000 + cess
- 20% bracket: Save ~₹10,000 + cess

**Note:** NPS has a lock-in until age 60. Consider this before investing.
"""

    def _get_home_loan_response(self, session: ChatSession) -> str:
        current_24b = session.user_profile.get('section_24b', 0)
        
        return f"""**Home Loan Tax Benefits**

Your current Section 24(b) claim: **₹{current_24b:,.0f}**

**Section 24(b) - Interest on Home Loan:**
- Self-occupied: Up to **₹2,00,000** per year
- Let-out property: No limit (but loss capped at ₹2L)
- Available only in **OLD REGIME**

**Section 80C - Principal Repayment:**
- Part of overall ₹1,50,000 limit
- Includes stamp duty & registration (first year)

**Section 80EEA (First-time buyers):**
- Additional ₹1,50,000 for affordable housing
- Loan sanctioned before March 2022

{"💡 You can claim **₹" + f"{200000 - current_24b:,.0f}** more under Section 24(b)." if current_24b < 200000 else "✅ You've maximized your Section 24(b) claim."}

**Tip:** Keep interest certificate from bank for claiming deduction.
"""

    def _get_generic_response(self, session: ChatSession) -> str:
        gross = session.salary_data.get('gross_salary', 0)
        recommended = session.tax_result.get('recommended_regime', 'new')
        
        return f"""I'd be happy to help with your tax questions!

**Your Quick Summary:**
- Gross Salary: ₹{gross:,.0f}
- Recommended Regime: {recommended.upper()}

**Common Questions I Can Help With:**
1. **Section 80C** - PPF, ELSS, LIC, NSC investments
2. **Section 80D** - Health insurance deductions
3. **HRA Exemption** - House rent allowance benefits
4. **Tax Regime** - Old vs New comparison
5. **NPS** - Additional ₹50,000 deduction
6. **Home Loan** - Section 24(b) interest deduction

**Try asking:**
- "What if I invest ₹50,000 more in 80C?"
- "How is HRA exemption calculated?"
- "Should I switch to the new regime?"

Please ask a specific question for detailed guidance!
"""

    def _get_error_response(self, message: str) -> Dict[str, Any]:
        """Return an error response"""
        return {
            "answer": f"⚠️ {message}",
            "confidence": "low",
            "confidence_reason": "Error occurred",
            "assumptions": [],
            "scenario_calculation": {"applicable": False},
            "follow_up_suggestions": [],
            "disclaimer": "Please try again or start a new calculation.",
            "ai_generated": False,
            "is_scenario": False,
            "error": message
        }


# Global instance
chat_advisor = ChatAdvisor()

