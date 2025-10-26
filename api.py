from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import tempfile
import os
import json

# Import your existing modules
from extractor import extract_speedmechome_invoice, validate_invoice
from pdf_processor import PDFProcessor
from models import InvoiceModel

app = FastAPI(
    title="SPEEDMECAHOME Invoice API",
    description="API for extracting and validating SPEEDMECAHOME invoices",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", 'https://fixiny-vercel.vercel.app', 'https://www.fixiny.net', 'https://fixiny.net'],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class ExtractionResponse(BaseModel):
    success: bool
    data: Optional[InvoiceModel] = None
    errors: List[str] = []
    warnings: List[str] = []
    validation_passed: bool = False

class ValidationResult(BaseModel):
    field: str
    status: str  # "valid", "warning", "error"
    message: str
    expected: Optional[Any] = None
    found: Optional[Any] = None

class ValidationResponse(BaseModel):
    overall_valid: bool
    results: List[ValidationResult]
    score: float  # 0-100

@app.get("/")
async def root():
    return {"message": "SPEEDMECAHOME Invoice API", "status": "running"}

@app.post("/extract-invoice", response_model=ExtractionResponse)
async def extract_invoice(file: UploadFile = File(...)):
    """
    Extract data from uploaded invoice PDF
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            return ExtractionResponse(
                success=False,
                errors=["Only PDF files are supported"]
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Process PDF
            processor = PDFProcessor()
            
            # Validate it's a SPEEDMECAHOME invoice
            if not processor.validate_pdf_structure(temp_path):
                return ExtractionResponse(
                    success=False,
                    errors=["The uploaded file doesn't appear to be a valid SPEEDMECAHOME invoice"]
                )
            
            # Extract text
            invoice_text = processor.extract_text_from_pdf(temp_path)
            
            if not invoice_text or len(invoice_text.strip()) < 50:
                return ExtractionResponse(
                    success=False,
                    errors=["Could not extract sufficient text from the PDF"]
                )
            
            # Extract structured data
            invoice_data = extract_speedmechome_invoice(invoice_text)
            
            # Validate the extracted data
            validation_passed = validate_invoice(invoice_data)
            
            return ExtractionResponse(
                success=True,
                data=invoice_data,
                validation_passed=validation_passed,
                warnings=["Some data validation issues found"] if not validation_passed else []
            )
            
        finally:
            # Clean up temp file
            os.unlink(temp_path)
            
    except Exception as e:
        return ExtractionResponse(
            success=False,
            errors=[f"Processing error: {str(e)}"]
        )

@app.post("/validate-invoice", response_model=ValidationResponse)
async def validate_invoice_data(data: InvoiceModel):
    """
    Validate already extracted invoice data
    """
    try:
        validation_results = []
        
        # Check required fields
        required_fields = ['client_name', 'invoice_number', 'vehicle_plate', 'total_ttc']
        for field in required_fields:
            value = getattr(data, field, None)
            if not value:
                validation_results.append(ValidationResult(
                    field=field,
                    status="error",
                    message="This field is required",
                    expected="Non-empty value",
                    found=value
                ))
        
        # Validate financial calculations
        if data.items:
            calculated_subtotal = sum(item.total_ht for item in data.items)
            if abs(calculated_subtotal - data.subtotal_ht) > 0.01:
                validation_results.append(ValidationResult(
                    field="subtotal_ht",
                    status="error",
                    message="Subtotal doesn't match sum of items",
                    expected=calculated_subtotal,
                    found=data.subtotal_ht
                ))
        
        # Validate total
        calculated_total = data.subtotal_ht + data.total_vat + data.fiscal_stamp
        if abs(calculated_total - data.total_ttc) > 0.01:
            validation_results.append(ValidationResult(
                field="total_ttc",
                status="warning",
                message="Total amount calculation mismatch",
                expected=calculated_total,
                found=data.total_ttc
            ))
        
        # Validate VAT
        expected_vat = data.subtotal_ht * 0.19
        if abs(expected_vat - data.total_vat) > 0.01:
            validation_results.append(ValidationResult(
                field="total_vat",
                status="warning",
                message="VAT amount doesn't match 19% of subtotal",
                expected=expected_vat,
                found=data.total_vat
            ))
        
        # Count validations
        errors = [r for r in validation_results if r.status == "error"]
        warnings = [r for r in validation_results if r.status == "warning"]
        
        # Calculate score (0-100)
        total_checks = len(validation_results)
        if total_checks == 0:
            score = 100
        else:
            error_weight = len(errors) * 2
            warning_weight = len(warnings) * 1
            score = max(0, 100 - (error_weight + warning_weight) * 10)
        
        return ValidationResponse(
            overall_valid=len(errors) == 0,
            results=validation_results,
            score=score
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@app.get("/invoice-template")
async def get_invoice_template():
    """
    Get the expected invoice template structure
    """
    return {
        "expected_fields": {
            "supplier_info": [
                "supplier_name", "supplier_address", "supplier_phone", 
                "supplier_vat_code", "supplier_email", "supplier_bank", "supplier_iban"
            ],
            "client_info": [
                "client_name", "client_mf", "client_email", "client_mobile"
            ],
            "invoice_metadata": [
                "invoice_date", "invoice_number", "vehicle_plate", "vehicle_mileage"
            ],
            "financial_data": [
                "subtotal_ht", "total_ht", "total_vat", "fiscal_stamp", "total_ttc"
            ]
        },
        "required_fields": [
            "client_name", "invoice_number", "vehicle_plate", "total_ttc"
        ]
    }

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)