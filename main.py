from extractor import extract_speedmechome_invoice, validate_invoice
import json
import sys
import os

def process_invoice_text(text: str, source_name: str = "invoice") -> None:
    """
    Process invoice text directly
    """
    # Save extracted text for debugging
    with open(f'{source_name}_extracted.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"📄 Extracted text saved to: {source_name}_extracted.txt")
    
    # Extract structured data
    try:
        invoice_data = extract_speedmechome_invoice(text)
        
        # Validate
        if validate_invoice(invoice_data):
            print("✅ Invoice extracted and validated successfully!")
        else:
            print("⚠️  Invoice extracted but validation issues found")
        
        # Print results
        print_results(invoice_data)
        
        # Save as JSON
        output_file = f'{source_name}_data.json'
        save_as_json(invoice_data, output_file)
        
    except Exception as e:
        print(f"❌ Error extracting invoice data: {e}")
        import traceback
        traceback.print_exc()

def print_results(invoice_data):
    """Print extracted results in a readable format"""
    print("\n" + "="*60)
    print("EXTRACTED INVOICE DATA")
    print("="*60)
    print(f"📋 Client: {invoice_data.client_name}")
    print(f"📅 Date: {invoice_data.invoice_date.strftime('%Y-%m-%d')}")
    print(f"🧾 Invoice #: {invoice_data.invoice_number}")
    print(f"🚗 Vehicle: {invoice_data.vehicle_plate} ({invoice_data.vehicle_mileage})")
    print(f"💰 Total: {invoice_data.total_ttc} DT")
    
    print(f"\n🛒 Items ({len(invoice_data.items)}):")
    for item in invoice_data.items:
        print(f"   • {item.description}: {item.quantity} x {item.unit_price} DT = {item.total_ht} DT")
    
    print(f"\n📊 Summary:")
    print(f"   Subtotal HT: {invoice_data.subtotal_ht} DT")
    print(f"   TVA: {invoice_data.total_vat} DT")
    print(f"   Timbre: {invoice_data.fiscal_stamp} DT")
    print(f"   Total TTC: {invoice_data.total_ttc} DT")

def save_as_json(invoice_data, output_file):
    """Save extracted data as JSON"""
    json_data = invoice_data.dict()
    json_data['invoice_date'] = invoice_data.invoice_date.isoformat()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Data saved to: {output_file}")

def main():
    # For now, we'll work with text input since PDF processing has dependencies
    print("SPEEDMECAHOME Invoice Extractor")
    print("=" * 40)
    
    # Check if we have the invoice text file
    if os.path.exists('invoice_text.txt'):
        with open('invoice_text.txt', 'r', encoding='utf-8') as f:
            invoice_text = f.read()
        process_invoice_text(invoice_text, "invoice")
    else:
        print("❌ No invoice text found.")
        print("Please create a file called 'invoice_text.txt' with the invoice content")
        print("or modify the main.py to use PDF processing.")

if __name__ == "__main__":
    main()
# from extractor import extract_speedmechome_invoice, validate_invoice
# from pdf_processor import PDFProcessor
# import json
# import sys
# import os

# def process_invoice_pdf(pdf_path: str, use_ocr: bool = False) -> None:
#     """
#     Process a single PDF invoice
#     """
#     # Initialize PDF processor
#     processor = PDFProcessor()
    
#     # Validate PDF structure first
#     if not processor.validate_pdf_structure(pdf_path):
#         print("❌ This doesn't appear to be a valid SPEEDMECAHOME invoice")
#         return
    
#     # Extract text from PDF
#     invoice_text = processor.extract_text_from_pdf(pdf_path, use_ocr)
    
#     if not invoice_text or len(invoice_text.strip()) < 50:
#         print("❌ Failed to extract sufficient text from PDF")
#         return
    
#     # Save extracted text for debugging
#     base_name = os.path.splitext(pdf_path)[0]
#     with open(f'{base_name}_extracted.txt', 'w', encoding='utf-8') as f:
#         f.write(invoice_text)
#     print(f"📄 Extracted text saved to: {base_name}_extracted.txt")
    
#     # Extract structured data
#     try:
#         invoice_data = extract_speedmechome_invoice(invoice_text)
        
#         # Validate
#         if validate_invoice(invoice_data):
#             print("✅ Invoice extracted and validated successfully!")
#         else:
#             print("⚠️  Invoice extracted but validation issues found")
        
#         # Print results
#         print_results(invoice_data)
        
#         # Save as JSON
#         output_file = f'{base_name}_data.json'
#         save_as_json(invoice_data, output_file)
        
#     except Exception as e:
#         print(f"❌ Error extracting invoice data: {e}")
#         import traceback
#         traceback.print_exc()

# def print_results(invoice_data):
#     """Print extracted results in a readable format"""
#     print("\n" + "="*60)
#     print("EXTRACTED INVOICE DATA")
#     print("="*60)
#     print(f"📋 Client: {invoice_data.client_name}")
#     print(f"📅 Date: {invoice_data.invoice_date.strftime('%Y-%m-%d')}")
#     print(f"🧾 Invoice #: {invoice_data.invoice_number}")
#     print(f"🚗 Vehicle: {invoice_data.vehicle_plate} ({invoice_data.vehicle_mileage})")
#     print(f"💰 Total: {invoice_data.total_ttc} DT")
    
#     print(f"\n🛒 Items ({len(invoice_data.items)}):")
#     for item in invoice_data.items:
#         print(f"   • {item.description}: {item.quantity} x {item.unit_price} DT = {item.total_ht} DT")
    
#     print(f"\n📊 Summary:")
#     print(f"   Subtotal HT: {invoice_data.subtotal_ht} DT")
#     print(f"   TVA: {invoice_data.total_vat} DT")
#     print(f"   Timbre: {invoice_data.fiscal_stamp} DT")
#     print(f"   Total TTC: {invoice_data.total_ttc} DT")

# def save_as_json(invoice_data, output_file):
#     """Save extracted data as JSON"""
#     json_data = invoice_data.dict()
#     json_data['invoice_date'] = invoice_data.invoice_date.isoformat()
    
#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(json_data, f, indent=2, ensure_ascii=False)
    
#     print(f"💾 Data saved to: {output_file}")

# def batch_process_pdfs(folder_path: str):
#     """Process all PDFs in a folder"""
#     pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    
#     if not pdf_files:
#         print("No PDF files found in the specified folder")
#         return
    
#     print(f"Found {len(pdf_files)} PDF files to process")
    
#     for pdf_file in pdf_files:
#         pdf_path = os.path.join(folder_path, pdf_file)
#         print(f"\n{'='*40}")
#         print(f"Processing: {pdf_file}")
#         print('='*40)
#         process_invoice_pdf(pdf_path)

# def main():
#     if len(sys.argv) < 2:
#         print("Usage:")
#         print("  python main.py <pdf_file>              # Process single PDF")
#         print("  python main.py --folder <folder_path>  # Process all PDFs in folder")
#         print("  python main.py --ocr <pdf_file>        # Force OCR processing")
#         return
    
#     if sys.argv[1] == '--folder' and len(sys.argv) > 2:
#         batch_process_pdfs(sys.argv[2])
#     elif sys.argv[1] == '--ocr' and len(sys.argv) > 2:
#         process_invoice_pdf(sys.argv[2], use_ocr=True)
#     else:
#         process_invoice_pdf(sys.argv[1])

# if __name__ == "__main__":
    main()
# from extractor import extract_speedmechome_invoice, validate_invoice
# import json

# def main():
#     # Read the text content (in real scenario, this would come from OCR)
#     with open('invoice.pdf.txt', 'r', encoding='utf-8') as f:
#         invoice_text = f.read()
    
#     # Extract data
#     try:
#         invoice_data = extract_speedmechome_invoice(invoice_text)
        
#         # Validate
#         if validate_invoice(invoice_data):
#             print("✅ Invoice extracted and validated successfully!")
#         else:
#             print("⚠️  Invoice extracted but validation issues found")
        
#         # Print results
#         print("\n" + "="*50)
#         print("EXTRACTED INVOICE DATA")
#         print("="*50)
#         print(f"Client: {invoice_data.client_name}")
#         print(f"Invoice: {invoice_data.invoice_number}")
#         print(f"Date: {invoice_data.invoice_date.strftime('%Y-%m-%d')}")
#         print(f"Vehicle: {invoice_data.vehicle_plate}")
#         print(f"Total: {invoice_data.total_ttc} DT")
        
#         print(f"\nItems ({len(invoice_data.items)}):")
#         for item in invoice_data.items:
#             print(f"  - {item.description}: {item.quantity} x {item.unit_price} = {item.total_ht} DT")
        
#         # Save as JSON
#         with open('extracted_invoice.json', 'w', encoding='utf-8') as f:
#             json_data = invoice_data.dict()
#             json_data['invoice_date'] = invoice_data.invoice_date.isoformat()
#             json.dump(json_data, f, indent=2, ensure_ascii=False)
        
#         print(f"\n📁 Data saved to 'extracted_invoice.json'")
        
#     except Exception as e:
#         print(f"❌ Error extracting invoice: {e}")

# if __name__ == "__main__":
#     main()