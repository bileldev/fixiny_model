from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class InvoiceItem(BaseModel):
    item_number: str
    description: str
    quantity: float
    unit_price: float
    vat_rate: float
    total_ht: float

class VATBreakdown(BaseModel):
    rate: float
    base: float
    amount: float

class InvoiceModel(BaseModel):
    # Header Information
    supplier_name: str
    supplier_address: str
    supplier_phone: str
    supplier_vat_code: str
    supplier_email: str
    supplier_bank: str
    supplier_iban: str
    
    # Client Information
    client_name: str
    client_mf: str
    client_email: str
    client_mobile: str
    
    # Invoice Metadata
    invoice_date: datetime
    invoice_number: str
    vehicle_plate: str
    vehicle_mileage: str
    
    # Line Items
    items: List[InvoiceItem]
    
    # Financial Summary
    subtotal_ht: float
    vat_breakdown: List[VATBreakdown]
    total_ht: float
    total_vat: float
    fiscal_stamp: float
    total_ttc: float
    amount_in_words: str