from extractor import extract_speedmechome_invoice
import re

def debug_extraction():
    with open('invoice_text.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("=== DEBUG INFORMATION ===")
    
    # Check if key patterns are found
    patterns_to_check = {
        'SOUS-TOTAL HT': r'SOUS-TOTAL HT.*?([\d,]+\.?\d*)\s*DT',
        'TOTAL HT': r'TOTAL HT.*?([\d,]+\.?\d*)\s*DT',
        'TOTAL TVA': r'TOTAL TVA.*?([\d,]+\.?\d*)\s*DT',
        'NET À PAYER': r'NET À PAYER.*?([\d,]+\.?\d*)\s*DT',
        'VAT Table': r'19\s*%\s*([\d,]+\.?\d*)\s*DT\s*([\d,]+\.?\d*)\s*DT'
    }
    
    for pattern_name, pattern in patterns_to_check.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            print(f"✅ Found {pattern_name}: {match.group()}")
        else:
            print(f"❌ Missing {pattern_name}")
    
    print("\n=== EXTRACTION ATTEMPT ===")
    try:
        invoice_data = extract_speedmechome_invoice(text)
        print("✅ Extraction successful!")
        print(f"Client: {invoice_data.client_name}")
        print(f"Subtotal HT: {invoice_data.subtotal_ht}")
        print(f"Total TTC: {invoice_data.total_ttc}")
        print(f"Items found: {len(invoice_data.items)}")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_extraction()