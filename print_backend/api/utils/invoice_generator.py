from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_RIGHT, TA_LEFT , TA_CENTER
from datetime import datetime
import os
from datetime import timedelta
from io import BytesIO


# Create the invoice PDF
def create_invoice(invoice_items : list):
    # File name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    buffer = BytesIO()
    
    # Create document with letter size
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(name='InvoiceTitle', 
                             fontSize=24, 
                             leading=30,
                             textColor=colors.HexColor("#2c3e50"),
                             alignment=TA_LEFT))
    
    styles.add(ParagraphStyle(name='SectionHeader', 
                             fontSize=12, 
                             leading=15,
                             textColor=colors.HexColor("#2c3e50"),
                             alignment=TA_LEFT))
    
    styles.add(ParagraphStyle(name='RightAlign', 
                             fontSize=10, 
                             leading=12,
                             textColor=colors.HexColor("#7f8c8d"),
                             alignment=TA_RIGHT))
    
    styles.add(ParagraphStyle(name='LeftAlign', 
                             fontSize=10, 
                             leading=12,
                             textColor=colors.HexColor("#7f8c8d"),
                             alignment=TA_LEFT))
    
    # Add logo (replace with your own logo path)
    logo_path = "logo.png"  # Replace with your logo file
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2*inch, height=0.5*inch)
        elements.append(logo)
        elements.append(Spacer(1, 0.25*inch))
    
    # Invoice title and number
    invoice_info = [
        [Paragraph("<b>INVOICE</b>", styles['InvoiceTitle']), 
         Paragraph(f"<b>Invoice #</b> INV-2023-001<br/>"
                  f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>"
                  f"<b>Due Date:</b> {(datetime.now() + timedelta(days=30)).strftime('%B %d, %Y')}", 
                  styles['RightAlign'])]
    ]
    
    invoice_table = Table(invoice_info, colWidths=[doc.width*0.6, doc.width*0.4])
    invoice_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # From/To addresses
    from_address = [
        [Paragraph("<b>FROM</b>", styles['SectionHeader'])],
        [Paragraph("Your Company Name<br/>"
                   "123 Business Street<br/>"
                   "City, State 12345<br/>"
                   "Phone: (123) 456-7890<br/>"
                   "Email: billing@yourcompany.com", styles['LeftAlign'])]
    ]
    
    to_address = [
        [Paragraph("<b>BILL TO</b>", styles['SectionHeader'])],
        [Paragraph("Client Company Name<br/>"
                   "456 Client Avenue<br/>"
                   "City, State 67890<br/>"
                   "Phone: (987) 654-3210<br/>"
                   "Email: accounts@client.com", styles['LeftAlign'])]
    ]
    
    addresses = Table([[Table(from_address), Table(to_address)]], colWidths=[doc.width*0.5, doc.width*0.5])
    addresses.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(addresses)
    elements.append(Spacer(1, 0.5*inch))
    
    # Items table
    items = [["Description", "Quantity", "Unit Price", "Amount"]]
    
    # Sample items - in a real app these would come from your data
    for item in invoice_items:
        amount = item["quantity"] * item["unit_price"]
        items.append([
            Paragraph(item["description"], styles['LeftAlign']),
            Paragraph(str(item["quantity"]), styles['RightAlign']),
            Paragraph(f"${item['unit_price']:,.2f}", styles['RightAlign']),
            Paragraph(f"${amount:,.2f}", styles['RightAlign'])
        ])
    
    # Calculate subtotal
    subtotal = sum(item["quantity"] * item["unit_price"] for item in invoice_items)
    tax = subtotal * 0.10  # 10% tax
    total = subtotal + tax
    
    # Add subtotal, tax, and total rows
    items.extend([
        ["", "", Paragraph("<b>Subtotal</b>", styles['RightAlign']), 
         Paragraph(f"<b>${subtotal:,.2f}</b>", styles['RightAlign'])],
        ["", "", Paragraph("<b>Tax (10%)</b>", styles['RightAlign']), 
         Paragraph(f"<b>${tax:,.2f}</b>", styles['RightAlign'])],
        ["", "", Paragraph("<b>Total</b>", styles['RightAlign']), 
         Paragraph(f"<b>${total:,.2f}</b>", styles['RightAlign'])],
    ])
    
    items_table = Table(items, colWidths=[doc.width*0.5, doc.width*0.1, doc.width*0.2, doc.width*0.2])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor("#f8f9fa")),
        ('LINEABOVE', (0, -3), (-1, -3), 1, colors.HexColor("#e9ecef")),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor("#2c3e50")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Payment terms
    elements.append(Paragraph("<b>Payment Terms</b>", styles['SectionHeader']))
    elements.append(Paragraph("Payment is due within 30 days. Please make checks payable to Your Company Name and include the invoice number on your check.", styles['LeftAlign']))
    elements.append(Spacer(1, 0.25*inch))
    
    elements.append(Paragraph("<b>Thank you for your business!</b>", styles['SectionHeader']))
    
    # Footer
    footer = Paragraph("Your Company Name | 123 Business Street | City, State 12345 | billing@yourcompany.com | (123) 456-7890", 
                      ParagraphStyle(name='Footer', 
                                    fontSize=8, 
                                    textColor=colors.HexColor("#95a5a6"),
                                    alignment=TA_CENTER))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(footer)
    
    # Build the PDF
    doc.build(elements)
    print(f"Invoice created")
    return buffer

