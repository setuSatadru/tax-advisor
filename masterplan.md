
## 1. App Overview and Objectives

**App Name (Working):** GenAI-Based Tax Advisor for Individuals

**Objective:**  
Build a prototype web application that assists salaried individual taxpayers by automating salary slip analysis, gathering additional tax-relevant information through forms, and providing personalized tax-saving insights. The app will clearly compare old and new tax regimes, generate AI-driven tax-saving recommendations, and support conversational Q&A for enhanced clarity.

---

## 2. Target Audience

- Salaried professionals in India  
- Non-expert users who find tax filing confusing  
- Users seeking to maximize tax savings without relying heavily on external consultants  
- Early prototype focus excludes freelancers, pensioners, etc. (future expansion possible)

---

## 3. Core Features and Functionality

- **Secure Document Upload & Parsing:**  
  - Upload text-based salary slip PDFs  
  - Hybrid parsing approach (text extraction + normalization + rules-based identification)  
  - Fail gracefully on missing or ambiguous fields

- **User Input Form:**  
  - After upload, users confirm extracted data and provide missing details via structured forms  
  - Mandatory completion before proceeding

- **Tax Computation Engine:**  
  - Deterministic code calculates taxable income, compares old vs new tax regimes, and computes tax payable  
  - Covers key deduction sections: 80C, 80D, HRA, etc.

- **Assumptions Handling:**  
  - Soft assumptions with explicit user disclosure and acknowledgment  
  - Defaults filled where possible, transparent communication of assumptions

- **AI-powered Advisor:**  
  - LLM used in a hybrid manner: assists in some complex calculations and edge cases  
  - Generates natural-language insights, tax-saving suggestions, and explanations  
  - Handles user Q&A post-analysis with confidence and transparency

- **User Experience:**  
  - Server-rendered, linear step-by-step wizard  
  - Clear, minimalist UI focusing on correctness and user trust  
  - Explicit assumption banners and input validation

---

## 4. High-level Technical Stack Recommendations

| Layer               | Technology / Approach                          | Notes                                   |
|---------------------|-----------------------------------------------|-----------------------------------------|
| Platform            | Web Application (Desktop-first)                | Best for PDF upload and structured forms|
| Backend Philosophy  | Modular, Single Deployment                      | Clear separation without microservices  |
| Backend Ecosystem   | Python (FastAPI framework)                      | Strong AI and PDF tooling, fast iteration |
| Frontend Philosophy | Server-rendered, Form-first UI                   | Simple, linear wizard UX                  |
| LLM Integration     | Hybrid (Single provider: Gemini Free API)      | Thin abstraction layer for flexibility   |
| PDF Parsing         | Hybrid parsing (text extraction + rules)       | Deterministic, avoids LLM hallucination  |
| User Input Handling | Structured form for missing details             | Mandatory confirmation step               |
| Assumptions         | Soft assumptions with explicit disclosure       | Balance accuracy and user experience     |

---

## 5. Conceptual Data Model (Simplified)

- **UserProfile** (for prototype, no auth): stores basic tax profile data collected via forms  
- **SalarySlipData:** parsed numeric fields from uploaded salary slip  
- **TaxCalculation:** computed incomes, deductions, taxes under old & new regimes  
- **AIInsights:** generated suggestions, explanations, Q&A logs  
- **AssumptionsLog:** recorded assumptions and user acknowledgments  

---

## 6. User Interface Design Principles

- Minimalist and intuitive layout with distinct steps  
- Progressive disclosure of tax sections and suggestions  
- Clear error messaging and input validation  
- Explicit banners for assumptions and disclaimers  
- Accessible UI focusing on clarity for non-experts  

---

## 7. Security Considerations

- Secure file uploads with size/type restrictions  
- Avoid storing sensitive PDFs permanently; store parsed data only if necessary  
- Use HTTPS and secure API endpoints  
- Prepare for potential future authentication and data privacy compliance  
- Sanitize user inputs carefully to prevent injection attacks  

---

## 8. Development Phases / Milestones

### Phase 0 – Groundwork & Guardrails  
- Define scope and tax sections  
- Explicitly exclude Form 16 and authentication  

### Phase 1 – Thin End-to-End Slice  
- Salary slip upload and hybrid parsing  
- Form-based missing data input step  
- Basic deterministic tax computation (old vs new)  
- Static tax summary screen (numbers only)  

### Phase 2 – Advisor Intelligence Layer  
- AI-generated tax-saving suggestions and explanations  
- Section-wise UI breakdowns  
- Prompt design and AI integration hardening  

### Phase 3 – Conversational Q&A & Advisor Depth  
- Post-analysis Q&A with LLM  
- Scenario exploration and hypotheticals  
- Confidence and assumption disclosures in AI answers  

### Phase 4 – UX & Trust Polishing (Optional)  
- Privacy messaging and disclaimers  
- Input validation improvements  
- Better UI/UX refinements  

---

## 9. Potential Challenges and Solutions

| Challenge                                   | Proposed Solution                                  |
|---------------------------------------------|---------------------------------------------------|
| Hallucinations in AI output                  | Rules-first approach; LLM only for explanations   |
| Variability in salary slip formats           | Hybrid parsing with fallback, focus on known templates |
| Missing or ambiguous user data               | Mandatory form step with assumption disclosure    |
| User trust and anxiety                        | Explicit assumptions, transparent UI messaging    |
| Scaling beyond salaried taxpayers            | Modular backend; future support for freelancers   |
| Data security and privacy concerns           | Minimal data retention; secure uploads; HTTPS     |

---

## 10. Future Expansion Possibilities

- Support for freelancers, pensioners, self-employed  
- Mobile-responsive UI or native mobile apps  
- Authentication and user profiles  
- Integration with income tax e-filing portals  
- Advanced scenario planning and tax projections  
- Multi-language support for broader reach  

---

# Summary

You are building a **trusted, accurate, and AI-augmented tax advisor** prototype focused on salaried individuals with a clear, linear user journey. The system balances **deterministic logic for correctness** with **AI-generated insights for clarity and personalization**, all wrapped in a minimalist, accessible web UI.

---

Let me know if you want me to expand any section or include extra details! Would you also like me to draft a **high-level project timeline** or **risk management plan** next?
"""

file_path = '/mnt/data/masterplan.md'
with open(file_path, 'w') as file:
    file.write(masterplan_content)

file_path
