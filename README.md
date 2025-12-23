# Tax Advisor - GenAI-Based Tax Advisor for Salaried Individuals

A prototype web application that assists salaried individual taxpayers by automating salary slip analysis, gathering additional tax-relevant information, and providing personalized tax-saving insights with Old vs New regime comparison.

## 🎯 Project Status

**Phase 0 & 1 - Completed** ✅
- Phase 0: Scope definition and tax sections
- Phase 1: End-to-end slice with upload, parsing, form, and tax calculation

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows OS (tested on Windows 10/11)

### Setup Instructions

1. **Activate Virtual Environment**
   ```powershell
   cd C:\SETU_Original\vibeCoding_NexTurn\tax-advisor-app
   .\venv\Scripts\Activate.ps1
   ```

2. **Install Dependencies** (if not already installed)
   ```powershell
   pip install -r requirements.txt
   ```

3. **Create Environment File** (Optional - for future Gemini API integration)
   ```powershell
   # Copy .env.example to .env and add your Gemini API key
   # For Phase 1, API key is not required
   ```

4. **Run the Application**
   ```powershell
   python -m uvicorn app.main:app --reload
   ```

5. **Access the Application**
   - Open your browser and navigate to: `http://127.0.0.1:8000`
   - Or visit: `http://localhost:8000`

## 📋 Features (Phase 0 & 1)

### ✅ Implemented Features

1. **Salary Slip Upload & Hybrid Parsing**
   - Upload PDF salary slips
   - Automatic text extraction using pdfplumber
   - Rules-based field identification (Basic, HRA, Allowances, Deductions)
   - Graceful handling of missing or ambiguous fields

2. **User Input Form**
   - Confirm extracted salary slip data
   - Enter missing information manually
   - Provide additional tax-relevant details:
     - Age (for senior citizen benefits)
     - Rent paid (for HRA exemption)
     - City type (Metro/Non-Metro)
     - Tax deductions (80C, 80D, 80G, 80TTA, 24(b))

3. **Tax Computation Engine**
   - Deterministic calculation for Old Regime
   - Deterministic calculation for New Regime
   - Automatic comparison and recommendation
   - Supports key deductions:
     - Section 80C (max ₹1,50,000)
     - Section 80D (Health Insurance)
     - Section 80G (Donations)
     - Section 80TTA (Savings Interest)
     - Section 24(b) (Home Loan Interest)
     - HRA Exemption (calculated based on rent, salary, city)

4. **Tax Summary Screen**
   - Side-by-side comparison of Old vs New regime
   - Detailed breakdown of deductions and taxes
   - Clear recommendation with savings amount
   - Effective tax rate calculation

### ❌ Excluded Features (Phase 0)

- Form 16 processing
- User authentication and login
- Freelancer/Pensioner income
- Capital gains
- Other income sources beyond salary

## 📁 Project Structure

```
tax-advisor-app/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and tax sections (Phase 0)
│   ├── models/
│   │   ├── __init__.py
│   │   └── salary_slip.py      # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_parser.py       # Hybrid PDF parser (Phase 1)
│   │   └── tax_calculator.py   # Tax computation engine (Phase 1)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── upload.py           # Upload and parsing routes
│   │   └── tax.py               # Tax calculation routes
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html          # Home page
│   │   ├── upload.html         # Upload page
│   │   ├── form.html           # Data confirmation form
│   │   └── summary.html        # Tax summary screen
│   └── static/
│       └── css/
│           └── style.css       # Minimalist UI styles
├── uploads/                     # Temporary PDF storage
├── venv/                        # Virtual environment
├── requirements.txt             # Python dependencies
├── masterplan.md                # Project masterplan
└── README.md                    # This file
```

## 🧪 Testing the Application

1. **Start the server** (as shown above)

2. **Upload a Salary Slip**
   - Click "Get Started - Upload Salary Slip"
   - Upload a PDF salary slip (test files available: `sukeshBakshi-salarySlip.pdf`, `rajeevMenon-salarySlip.pdf`)

3. **Review and Complete Form**
   - Review extracted data
   - Fill in missing fields
   - Provide additional tax information

4. **View Tax Summary**
   - See Old vs New regime comparison
   - Get personalized recommendation

## 🔧 Technical Stack

- **Backend**: Python 3.8+, FastAPI
- **PDF Parsing**: pdfplumber
- **Frontend**: Server-rendered HTML (Jinja2 templates)
- **Styling**: Custom CSS (minimalist design)
- **Data Validation**: Pydantic

## 📝 Notes

- **Security**: Uploaded PDFs are deleted immediately after parsing (not stored permanently)
- **Assumptions**: The system makes soft assumptions and displays them transparently
- **Accuracy**: Tax calculations follow Indian Income Tax rules for FY 2024-25
- **Limitations**: Currently supports only salaried individuals with standard salary slip formats

## 🚧 Future Phases

- **Phase 2**: AI-powered tax-saving suggestions and explanations
- **Phase 3**: Conversational Q&A with LLM
- **Phase 4**: UX polishing and trust enhancements

## 📄 License

This is a prototype project for educational/demonstration purposes.

---

**Built with ❤️ following the masterplan specifications**

