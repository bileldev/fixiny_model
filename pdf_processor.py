import pytesseract
from pdf2image import convert_from_path
import fitz
import tempfile
import os
from typing import Optional

class PDFProcessor:
    def __init__(self, tesseract_cmd: Optional[str] = None):
        # In production, tesseract should be in system PATH
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            # Try to use system tesseract
            try:
                pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
            except:
                # Fallback to whatever is in PATH
                pass
    
    def pdf_to_text_with_fitz(self, pdf_path: str) -> str:
        """Extract text directly from PDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            return text
        except Exception as e:
            print(f"Error with direct text extraction: {e}")
            return ""
    
    def pdf_to_text_with_ocr(self, pdf_path: str) -> str:
        """Extract text using OCR"""
        try:
            # Use lower DPI in production to reduce memory usage
            images = convert_from_path(pdf_path, dpi=200)
            all_text = ""
            for image in images:
                text = pytesseract.image_to_string(image, lang='fra+eng')
                all_text += text + "\n"
            return all_text
        except Exception as e:
            print(f"Error with OCR extraction: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str, use_ocr: bool = False) -> str:
        """Main method to extract text from PDF"""
        print(f"Processing PDF: {pdf_path}")
        
        # First try direct extraction (faster and uses less memory)
        if not use_ocr:
            text = self.pdf_to_text_with_fitz(pdf_path)
            if text and len(text.strip()) > 100:
                print("✓ Successfully extracted text directly from PDF")
                return text
            else:
                print("⚠ Direct extraction failed or got little text, falling back to OCR...")
        
        # Fall back to OCR
        print("Using OCR for text extraction...")
        return self.pdf_to_text_with_ocr(pdf_path)
    
    def validate_pdf_structure(self, pdf_path: str) -> bool:
        """Basic validation that this is a SPEEDMECAHOME invoice"""
        try:
            text = self.extract_text_from_pdf(pdf_path)
            
            required_markers = [
                "SPEEDMECAHOME",
                "NET À PAYER",
                "TVA",
                "DT"
            ]
            
            markers_found = sum(1 for marker in required_markers if marker in text)
            confidence = markers_found / len(required_markers)
            
            print(f"PDF validation confidence: {confidence:.1%}")
            return confidence >= 0.7
            
        except Exception as e:
            print(f"Error validating PDF: {e}")
            return False
# import pytesseract
# from pdf2image import convert_from_path
# import fitz  # PyMuPDF
# import tempfile
# import os
# from typing import Optional

# class PDFProcessor:
#     def __init__(self, tesseract_cmd: Optional[str] = None):
#         if tesseract_cmd:
#             pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
#     def pdf_to_text_with_fitz(self, pdf_path: str) -> str:
#         """Extract text directly from PDF"""
#         try:
#             doc = fitz.open(pdf_path)
#             text = ""
#             for page in doc:
#                 text += page.get_text() + "\n"
#             doc.close()
#             return text
#         except Exception as e:
#             print(f"Error with direct text extraction: {e}")
#             return ""
    
#     def pdf_to_text_with_ocr(self, pdf_path: str) -> str:
#         """Extract text using OCR"""
#         try:
#             images = convert_from_path(pdf_path, dpi=300)
#             all_text = ""
#             for image in images:
#                 text = pytesseract.image_to_string(image, lang='fra+eng')
#                 all_text += text + "\n"
#             return all_text
#         except Exception as e:
#             print(f"Error with OCR extraction: {e}")
#             return ""
    
#     def extract_text_from_pdf(self, pdf_path: str, use_ocr: bool = False) -> str:
#         """Main method to extract text from PDF"""
#         # First try direct extraction
#         if not use_ocr:
#             text = self.pdf_to_text_with_fitz(pdf_path)
#             if text and len(text.strip()) > 100:
#                 return text
        
#         # Fall back to OCR
#         return self.pdf_to_text_with_ocr(pdf_path)
    
#     def validate_pdf_structure(self, pdf_path: str) -> bool:
#         """Basic validation that this is a SPEEDMECAHOME invoice"""
#         try:
#             text = self.extract_text_from_pdf(pdf_path)
            
#             # Check for key markers
#             required_markers = [
#                 "SPEEDMECAHOME",
#                 "NET À PAYER",
#                 "TVA",
#                 "DT"
#             ]
            
#             markers_found = sum(1 for marker in required_markers if marker in text)
#             confidence = markers_found / len(required_markers)
            
#             return confidence >= 0.7
            
#         except Exception as e:
#             print(f"Error validating PDF: {e}")
#             return False
# # import pytesseract
# # from pdf2image import convert_from_path
# # import fitz  # PyMuPDF
# # import tempfile
# # import os
# # from typing import Optional

# # class PDFProcessor:
# #     def __init__(self, tesseract_cmd: Optional[str] = None):
# #         if tesseract_cmd:
# #             pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
# #     def pdf_to_text_with_fitz(self, pdf_path: str) -> str:
# #         """
# #         Extract text directly from PDF using PyMuPDF (fastest method for text-based PDFs)
# #         """
# #         try:
# #             doc = fitz.open(pdf_path)
# #             text = ""
# #             for page in doc:
# #                 text += page.get_text() + "\n"
# #             doc.close()
# #             return text
# #         except Exception as e:
# #             print(f"Error with direct text extraction: {e}")
# #             return ""
    
# #     def pdf_to_text_with_ocr(self, pdf_path: str) -> str:
# #         """
# #         Extract text using OCR (for scanned PDFs or images)
# #         """
# #         try:
# #             # Convert PDF to images
# #             images = convert_from_path(pdf_path, dpi=300)
            
# #             all_text = ""
# #             for i, image in enumerate(images):
# #                 # Preprocess image for better OCR
# #                 # You can add image processing here if needed
                
# #                 # Perform OCR
# #                 text = pytesseract.image_to_string(image, lang='fra+eng')  # French + English
# #                 all_text += f"=== Page {i+1} ===\n{text}\n\n"
            
# #             return all_text
# #         except Exception as e:
# #             print(f"Error with OCR extraction: {e}")
# #             return ""
    
# #     def extract_text_from_pdf(self, pdf_path: str, use_ocr: bool = False) -> str:
# #         """
# #         Main method to extract text from PDF
# #         """
# #         print(f"Processing PDF: {pdf_path}")
        
# #         # First try direct text extraction (faster)
# #         if not use_ocr:
# #             text = self.pdf_to_text_with_fitz(pdf_path)
# #             if text and len(text.strip()) > 100:  # If we got substantial text
# #                 print("✓ Successfully extracted text directly from PDF")
# #                 return text
# #             else:
# #                 print("⚠ Direct extraction failed or got little text, falling back to OCR...")
        
# #         # Fall back to OCR
# #         print("Using OCR for text extraction...")
# #         return self.pdf_to_text_with_ocr(pdf_path)
    
# #     def validate_pdf_structure(self, pdf_path: str) -> bool:
# #         """
# #         Basic validation that this is a SPEEDMECAHOME invoice
# #         """
# #         try:
# #             text = self.extract_text_from_pdf(pdf_path)
            
# #             # Check for key markers of SPEEDMECAHOME invoices
# #             required_markers = [
# #                 "SPEEDMECAHOME",
# #                 "NET À PAYER",
# #                 "TVA",
# #                 "DT"
# #             ]
            
# #             markers_found = sum(1 for marker in required_markers if marker in text)
# #             confidence = markers_found / len(required_markers)
            
# #             print(f"PDF validation confidence: {confidence:.1%}")
# #             return confidence >= 0.7  # At least 70% of markers found
            
# #         except Exception as e:
# #             print(f"Error validating PDF: {e}")
# #             return False
# # # import pytesseract
# # # from pdf2image import convert_from_path
# # # import tempfile
# # # import os

# # # def pdf_to_text(pdf_path):
# # #     """Convert PDF to text using OCR"""
# # #     try:
# # #         # Convert PDF to images
# # #         images = convert_from_path(pdf_path)
        
# # #         all_text = ""
# # #         for image in images:
# # #             text = pytesseract.image_to_string(image, lang='fra')  # French language
# # #             all_text += text + "\n"
        
# # #         return all_text
# # #     except Exception as e:
# # #         print(f"Error processing PDF: {e}")
# # #         return None

# # # # Then modify main.py to use:
# # # # invoice_text = pdf_to_text('invoice.pdf')