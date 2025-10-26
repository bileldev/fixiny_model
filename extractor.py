import re
from datetime import datetime
from models import InvoiceModel, InvoiceItem, VATBreakdown

def extract_speedmechome_invoice(text: str) -> InvoiceModel:
    lines = text.split('\n')
    
    # Initialize with empty values that will be filled by extraction
    data = {
        'supplier_name': 'SPEEDMECAHOME',
        'supplier_address': 'Route X20, 2091 jardin d\'el menzah 2',
        'supplier_phone': '+21629097633',
        'supplier_vat_code': '1755825 N A M 000',
        'supplier_email': 'contact.fixiny@gmail.com',
        'supplier_bank': 'Banque Baraka-Al Baraka Bank',
        'supplier_iban': 'TN59 3201 8788 1161 5185 2185',
        'vat_breakdown': [],
        'items': []
    }
    
    # Extract all fields systematically
    extract_client_info(lines, data)
    extract_invoice_metadata(lines, data)
    extract_vehicle_info(lines, data)
    extract_line_items(text, data)
    extract_financial_data(text, data)
    
    # Validate and set defaults for any missing required fields
    ensure_required_fields(data)
    
    return InvoiceModel(**data)

def extract_client_info(lines: list, data: dict):
    """Extract client information from the invoice"""
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Client name - after CLIENT header
        if 'CLIENT' in line and i + 1 < len(lines):
            data['client_name'] = lines[i + 1].strip()
        
        # MF code - look for MF pattern
        if 'MF' in line and any(char.isdigit() for char in line):
            data['client_mf'] = line.strip()
        
        # Email - look for email pattern
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line)
        if email_match and 'client_email' not in data:
            data['client_email'] = email_match.group(0)
        
        # Mobile - look for phone number pattern
        mobile_match = re.search(r'(\+?\d{2,}[\s\d-]+)', line)
        if mobile_match and ('Mobile' in line or 'Tél' in line):
            data['client_mobile'] = mobile_match.group(0).strip()

def extract_invoice_metadata(lines: list, data: dict):
    """Extract invoice metadata"""
    for line in lines:
        line = line.strip()
        
        # Date extraction
        date_match = re.search(r'Date\s+(\d{2}-\d{2}-\d{4})', line)
        if date_match:
            try:
                data['invoice_date'] = datetime.strptime(date_match.group(1), '%d-%m-%Y')
            except ValueError:
                pass
        
        # Invoice number
        bl_match = re.search(r'BL-\d+', line)
        if bl_match:
            data['invoice_number'] = bl_match.group(0)

def extract_vehicle_info(lines: list, data: dict):
    """Extract vehicle information"""
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Vehicle plate - look for pattern like "201 TU 9392"
        plate_match = re.search(r'(\d{1,4}\s*[A-Z]{1,3}\s*\d{1,4})', line)
        if plate_match and len(line) < 20:  # Simple length heuristic
            data['vehicle_plate'] = plate_match.group(0).strip()
            
            # Vehicle mileage - typically appears after the plate
            # Look in current line and next few lines
            mileage_found = False
            
            # Check current line
            mileage_match = re.search(r'(\d+)\s*KM', line)
            if mileage_match:
                data['vehicle_mileage'] = mileage_match.group(1) + ' KM'
                mileage_found = True
            
            # Check next 3 lines if not found
            if not mileage_found:
                for j in range(i+1, min(i+4, len(lines))):
                    mileage_match = re.search(r'(\d+)\s*KM', lines[j])
                    if mileage_match:
                        data['vehicle_mileage'] = mileage_match.group(1) + ' KM'
                        mileage_found = True
                        break

def extract_line_items(text: str, data: dict):
    """Extract line items from the invoice"""
    items = []
    lines = text.split('\n')
    
    # Find the items table section
    in_items_section = False
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Start of items table
        if 'Description' in line and 'Quantité' in line and 'PU HT' in line:
            in_items_section = True
            continue
        
        # End of items section
        if in_items_section and ('SOUS-TOTAL' in line or 'TVA' in line or 'TOTAL' in line):
            break
        
        # Parse item lines
        if in_items_section and re.match(r'^\d+\s+', line):
            item = parse_item_line(line)
            if item:
                items.append(item)
    
    data['items'] = items

def parse_item_line(line: str):
    """Parse a single item line with multiple strategies"""
    try:
        # Clean the line
        line = re.sub(r'\s+', ' ', line.strip())
        
        # Strategy 1: Split by multiple spaces and look for patterns
        parts = [p.strip() for p in line.split('  ') if p.strip()]
        
        if len(parts) >= 5:
            # Try to identify which part is which based on patterns
            description = ''
            quantity = 1.0
            unit_price = 0.0
            total_ht = 0.0
            
            for part in parts:
                # Look for quantity (usually a single digit)
                if re.match(r'^\d+$', part) and len(part) < 3:
                    quantity = float(part)
                # Look for prices (contain digits and commas)
                elif re.match(r'[\d,]+\.?\d*\s*DT', part) or re.match(r'^\d+[,.]\d+$', part):
                    price_value = float(part.replace(',', '.').replace(' DT', ''))
                    # First price encountered is usually unit price
                    if unit_price == 0.0:
                        unit_price = price_value
                    else:
                        total_ht = price_value
                # Description is everything else that's not a number or price
                elif not re.match(r'^\d+[,.]?\d*$', part) and not re.match(r'^\d+\s*%$', part):
                    description += ' ' + part
            
            if description and unit_price > 0:
                return InvoiceItem(
                    item_number=str(len(description)),  # Simple item number
                    description=description.strip(),
                    quantity=quantity,
                    unit_price=unit_price,
                    vat_rate=0.19,
                    total_ht=total_ht if total_ht > 0 else unit_price * quantity
                )
                
    except (ValueError, IndexError) as e:
        print(f"Error parsing item line: {line} - {e}")
    
    return None

def extract_financial_data(text: str, data: dict):
    """Extract financial totals and VAT information"""
    # Extract amounts with multiple pattern attempts
    patterns = {
        'subtotal_ht': [
            r'SOUS-TOTAL HT\s*:?\s*([\d,]+\.?\d*)\s*DT',
            r'SOUS-TOTAL HT.*?([\d,]+\.?\d*)',
            r'SOUS-TOTAL.*?([\d,]+\.?\d*)\s*DT'
        ],
        'total_ht': [
            r'TOTAL HT\s+([\d,]+\.?\d*)\s*DT',
            r'TOTAL HT.*?([\d,]+\.?\d*)'
        ],
        'total_vat': [
            r'TOTAL TVA\s+([\d,]+\.?\d*)\s*DT',
            r'TVA.*?([\d,]+\.?\d*)\s*DT'
        ],
        'fiscal_stamp': [
            r'Timbre fiscal\s+([\d,]+\.?\d*)\s*DT',
            r'Timbre.*?([\d,]+\.?\d*)\s*DT'
        ],
        'total_ttc': [
            r'NET À PAYER.*?([\d,]+\.?\d*)\s*DT',
            r'NET À PAYER\s+([\d,]+\.?\d*)\s*DT',
            r'TOTAL.*?([\d,]+\.?\d*)\s*DT'
        ]
    }
    
    for field, field_patterns in patterns.items():
        for pattern in field_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                try:
                    data[field] = float(match.group(1).replace(',', '.'))
                    break
                except ValueError:
                    continue
    
    # Extract VAT breakdown
    vat_match = re.search(r'(\d+)\s*%\s*([\d,]+\.?\d*)\s*DT\s*([\d,]+\.?\d*)\s*DT', text)
    if vat_match:
        try:
            rate = float(vat_match.group(1)) / 100
            base = float(vat_match.group(2).replace(',', '.'))
            amount = float(vat_match.group(3).replace(',', '.'))
            data['vat_breakdown'] = [VATBreakdown(rate=rate, base=base, amount=amount)]
        except ValueError:
            pass
    
    # Extract amount in words
    amount_match = re.search(r'Arrêtée la présente facture.*?\n(.*?)(?:\n|$)', text, re.DOTALL)
    if amount_match:
        data['amount_in_words'] = amount_match.group(1).strip()

def ensure_required_fields(data: dict):
    """Ensure all required fields have values"""
    # Set defaults for missing required fields
    defaults = {
        'client_name': 'Client Non Spécifié',
        'client_mf': 'MF NON SPECIFIE',
        'client_email': 'email@example.com',
        'client_mobile': '+21600000000',
        'invoice_date': datetime.now(),
        'invoice_number': 'BL-000000',
        'vehicle_plate': '000 TU 0000',
        'vehicle_mileage': '0 KM',
        'subtotal_ht': 0.0,
        'total_ht': 0.0,
        'total_vat': 0.0,
        'fiscal_stamp': 0.0,
        'total_ttc': 0.0,
        'amount_in_words': 'Montant non spécifié'
    }
    
    for field, default_value in defaults.items():
        if field not in data or data[field] is None:
            data[field] = default_value
    
    # Ensure VAT breakdown exists
    if not data['vat_breakdown']:
        data['vat_breakdown'] = [
            VATBreakdown(rate=0.19, base=data['subtotal_ht'], amount=data['total_vat'])
        ]
    
    # Calculate missing financial fields
    if data['total_ttc'] == 0 and data['subtotal_ht'] > 0:
        data['total_vat'] = data['subtotal_ht'] * 0.19
        data['fiscal_stamp'] = 1.0  # Default stamp
        data['total_ttc'] = data['subtotal_ht'] + data['total_vat'] + data['fiscal_stamp']

def validate_invoice(data: InvoiceModel) -> bool:
    """Validate the extracted invoice data"""
    try:
        # Basic validation - check if we have the essential data
        if not data.client_name or data.client_name == 'Client Non Spécifié':
            return False
        
        if not data.vehicle_plate or data.vehicle_plate == '000 TU 0000':
            return False
        
        if data.total_ttc == 0:
            return False
        
        return True
        
    except Exception as e:
        print(f"Validation error: {e}")
        return False