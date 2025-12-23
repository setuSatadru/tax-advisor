"""
Hybrid PDF Parser for Salary Slips
Phase 1: Text extraction + Rules-based identification
"""

import pdfplumber
import re
from typing import Dict, Optional, List, Tuple
from app.models.salary_slip import SalarySlipData
from app.config import SALARY_SLIP_FIELDS


class SalarySlipParser:
    """Hybrid parser for salary slip PDFs"""
    
    def __init__(self):
        self.field_patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Initialize regex patterns for field extraction"""
        patterns = {
            "basic_salary": [
                re.compile(r'basic\s*salary', re.IGNORECASE),
                re.compile(r'basic', re.IGNORECASE),
                re.compile(r'base\s*salary', re.IGNORECASE),
            ],
            "dearness_allowance": [
                re.compile(r'dearness\s*allowance', re.IGNORECASE),
                re.compile(r'd\.?a\.?', re.IGNORECASE),
            ],
            "hra": [
                re.compile(r'house\s*rent\s*allowance', re.IGNORECASE),
                re.compile(r'h\.?r\.?a\.?', re.IGNORECASE),
                re.compile(r'rent\s*allowance', re.IGNORECASE),
            ],
            "conveyance_allowance": [
                re.compile(r'conveyance\s*allowance', re.IGNORECASE),
                re.compile(r'conveyance', re.IGNORECASE),
            ],
            "transport_allowance": [
                re.compile(r'transport\s*allowance', re.IGNORECASE),
                re.compile(r't\.?a\.?', re.IGNORECASE),
            ],
            "special_allowance": [
                re.compile(r'special\s*allowance', re.IGNORECASE),
                re.compile(r's\.?a\.?', re.IGNORECASE),
            ],
            "medical_allowance": [
                re.compile(r'medical\s*allowance', re.IGNORECASE),
                re.compile(r'medical', re.IGNORECASE),
            ],
            "lta": [
                re.compile(r'leave\s*travel\s*allowance', re.IGNORECASE),
                re.compile(r'l\.?t\.?a\.?', re.IGNORECASE),
            ],
            "bonus": [
                re.compile(r'bonus', re.IGNORECASE),
                re.compile(r'incentive', re.IGNORECASE),
            ],
            "gross_salary": [
                re.compile(r'gross\s*salary', re.IGNORECASE),
                re.compile(r'gross', re.IGNORECASE),
                re.compile(r'total\s*earnings', re.IGNORECASE),
            ],
            "pf_employee": [
                re.compile(r'pf\s*\(?\s*employee\s*\)?', re.IGNORECASE),
                re.compile(r'employee\s*pf', re.IGNORECASE),
                re.compile(r'epf', re.IGNORECASE),
            ],
            "pf_employer": [
                re.compile(r'pf\s*\(?\s*employer\s*\)?', re.IGNORECASE),
                re.compile(r'employer\s*pf', re.IGNORECASE),
            ],
            "professional_tax": [
                re.compile(r'professional\s*tax', re.IGNORECASE),
                re.compile(r'prof\s*tax', re.IGNORECASE),
                # More specific pattern for table format: "Professional Tax" or "Prof Tax"
                re.compile(r'\d+\s*\|\s*professional\s*tax', re.IGNORECASE),
                re.compile(r'\d+\s*\|\s*prof\s*tax', re.IGNORECASE),
            ],
            "income_tax": [
                re.compile(r'income\s*tax', re.IGNORECASE),
                re.compile(r'tds', re.IGNORECASE),
                re.compile(r'tax\s*deducted', re.IGNORECASE),
            ],
            "net_salary": [
                re.compile(r'net\s*salary', re.IGNORECASE),
                re.compile(r'net\s*pay', re.IGNORECASE),
                re.compile(r'take\s*home', re.IGNORECASE),
            ],
        }
        return patterns
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract all text from PDF"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
        return text
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for better pattern matching"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere
        text = re.sub(r'[^\w\s:.,()/-]', '', text)
        return text.strip()
    
    def extract_amount(self, text: str, field_name: str) -> Optional[float]:
        """Extract amount for a given field using patterns"""
        if field_name not in self.field_patterns:
            return None
        
        patterns = self.field_patterns[field_name]
        normalized_text = self.normalize_text(text)
        
        for pattern in patterns:
            # Find the field name in text
            matches = pattern.finditer(normalized_text)
            for match in matches:
                # Look for amount after the field name (within 100 chars)
                start_pos = match.end()
                context = normalized_text[start_pos:start_pos + 100]
                
                # Try to find amount patterns - order matters, try most specific first
                # Pattern 1: Numbers with commas (e.g., "90,000" or "1,50,000.00")
                # This pattern requires at least one comma group, so it won't match plain "90000"
                comma_pattern = re.compile(r'[:]?\s*(\d{1,3}(?:,\d{2,3})+(?:\.\d{2})?)')
                comma_match = comma_pattern.search(context)
                if comma_match:
                    try:
                        amount_str = comma_match.group(1).replace(',', '')
                        amount = float(amount_str)
                        if 0 <= amount <= 10000000:
                            return amount
                    except (ValueError, AttributeError):
                        pass
                
                # Special handling for professional_tax - it's typically a small amount (200-2500)
                # So we should check for shorter numbers first
                if field_name == "professional_tax":
                    # For professional tax, check for shorter numbers first (typically 200-2500)
                    short_number_pattern = re.compile(r'[:]?\s*(\d{1,4}(?:\.\d{2})?)')
                    short_match = short_number_pattern.search(context)
                    if short_match:
                        try:
                            amount_str = short_match.group(1).replace(',', '')
                            amount = float(amount_str)
                            # Professional tax is typically between 0 and 5000
                            if 0 <= amount <= 5000:
                                return amount
                        except (ValueError, AttributeError):
                            pass
                
                # Pattern 2: Long numbers without commas (e.g., "90000" or "90000.00")
                # This matches 4+ digits to avoid matching short numbers like "1" or "2" from field labels
                long_number_pattern = re.compile(r'[:]?\s*(\d{4,}(?:\.\d{2})?)')
                long_match = long_number_pattern.search(context)
                if long_match:
                    try:
                        amount_str = long_match.group(1).replace(',', '')
                        amount = float(amount_str)
                        if 0 <= amount <= 10000000:
                            return amount
                    except (ValueError, AttributeError):
                        pass
                
                # Pattern 3: Any number sequence (fallback for shorter valid numbers like "200" for Professional Tax)
                # Skip this for professional_tax since we already handled it above
                if field_name != "professional_tax":
                    any_number_pattern = re.compile(r'[:]?\s*(\d+(?:\.\d{2})?)')
                    any_match = any_number_pattern.search(context)
                    if any_match:
                        try:
                            amount_str = any_match.group(1).replace(',', '')
                            amount = float(amount_str)
                            if 0 <= amount <= 10000000:
                                return amount
                        except (ValueError, AttributeError):
                            pass
        
        return None
    
    def calculate_derived_fields(self, data: Dict[str, float]) -> Dict[str, float]:
        """Calculate derived fields if missing"""
        assumptions = []
        
        # Calculate gross salary if missing
        if data.get("gross_salary", 0) == 0:
            gross = (
                data.get("basic_salary", 0) +
                data.get("dearness_allowance", 0) +
                data.get("hra", 0) +
                data.get("conveyance_allowance", 0) +
                data.get("transport_allowance", 0) +
                data.get("special_allowance", 0) +
                data.get("medical_allowance", 0) +
                data.get("lta", 0) +
                data.get("bonus", 0) +
                data.get("other_allowances", 0)
            )
            if gross > 0:
                data["gross_salary"] = gross
                assumptions.append("Gross salary calculated from components")
        
        # Calculate net salary if missing
        if data.get("net_salary", 0) == 0 and data.get("gross_salary", 0) > 0:
            net = (
                data.get("gross_salary", 0) -
                data.get("pf_employee", 0) -
                data.get("professional_tax", 0) -
                data.get("income_tax", 0) -
                data.get("other_deductions", 0)
            )
            if net > 0:
                data["net_salary"] = net
                assumptions.append("Net salary calculated from gross minus deductions")
        
        return data, assumptions
    
    def parse(self, file_path: str) -> Tuple[SalarySlipData, List[str]]:
        """
        Main parsing method
        Returns: (SalarySlipData, list of missing fields)
        """
        # Extract text
        text = self.extract_text_from_pdf(file_path)
        if not text:
            raise ValueError("No text could be extracted from PDF")
        
        # Extract amounts for each field
        extracted_data = {}
        missing_fields = []
        assumptions = []
        
        for field_name in SALARY_SLIP_FIELDS.keys():
            amount = self.extract_amount(text, field_name)
            if amount is not None:
                extracted_data[field_name] = amount
            else:
                missing_fields.append(field_name)
        
        # Calculate derived fields
        extracted_data, derived_assumptions = self.calculate_derived_fields(extracted_data)
        assumptions.extend(derived_assumptions)
        
        # Build SalarySlipData object
        salary_data = SalarySlipData(**extracted_data)
        salary_data.missing_fields = missing_fields
        salary_data.assumptions_made = assumptions
        
        # Calculate parsing confidence
        total_fields = len(SALARY_SLIP_FIELDS)
        found_fields = total_fields - len(missing_fields)
        confidence = (found_fields / total_fields) * 100 if total_fields > 0 else 0
        salary_data.parsing_confidence = {
            "overall_confidence": round(confidence, 2),
            "fields_found": found_fields,
            "fields_total": total_fields
        }
        
        return salary_data, missing_fields

