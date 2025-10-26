# from models import InvoiceModel, InvoiceItem, VATBreakdown
# from datetime import datetime

# def manual_extract_invoice():
#     """Manual extraction for the specific invoice format"""
    
#     data = {
#         'supplier_name': 'SPEEDMECAHOME',
#         'supplier_address': 'Route X20, 2091 jardin d\'el menzah 2',
#         'supplier_phone': '+21629097633',
#         'supplier_vat_code': '1755825 N A M 000',
#         'supplier_email': 'contact.fixiny@gmail.com',
#         'supplier_bank': 'Banque Baraka-Al Baraka Bank',
#         'supplier_iban': 'TN59 3201 8788 1161 5185 2185',
        
#         'client_name': 'NEXT STEP',
#         'client_mf': 'MF 1251519 F A M 000',
#         'client_email': 'M.kasmi@nextstep-it.com',
#         'client_mobile': '+21698772860',
        
#         'invoice_date': datetime(2024, 8, 10),
#         'invoice_number': 'BL-000226',
#         'vehicle_plate': '201 TU 9392',
#         'vehicle_mileage': '210105 KM',
        
#         'items': [
#             InvoiceItem(
#                 item_number='1',
#                 description='vidange',
#                 quantity=1.0,
#                 unit_price=18.000,
#                 vat_rate=0.19,
#                 total_ht=18.000
#             ),
#             InvoiceItem(
#                 item_number='2',
#                 description='FILTRE HUILE',
#                 quantity=1.0,
#                 unit_price=12.440,
#                 vat_rate=0.19,
#                 total_ht=12.440
#             ),
#             InvoiceItem(
#                 item_number='3',
#                 description='FILTRE A AIR',
#                 quantity=1.0,
#                 unit_price=21.160,
#                 vat_rate=0.19,
#                 total_ht=21.160
#             )
#         ],
        
#         'subtotal_ht': 51.600,
#         'vat_breakdown': [
#             VATBreakdown(rate=0.19, base=51.600, amount=9.804)
#         ],
#         'total_ht': 51.600,
#         'total_vat': 9.804,
#         'fiscal_stamp': 1.000,
#         'total_ttc': 62.404,
#         'amount_in_words': 'soixante-deux dinars quatre cent quatre millimes'
#     }
    
#     return InvoiceModel(**data)

# if __name__ == "__main__":
#     invoice = manual_extract_invoice()
#     print("✅ Manual extraction successful!")
#     print(f"Client: {invoice.client_name}")
#     print(f"Vehicle: {invoice.vehicle_plate} - {invoice.vehicle_mileage}")
#     print(f"Total: {invoice.total_ttc} DT")
#     print(f"Items: {len(invoice.items)}")