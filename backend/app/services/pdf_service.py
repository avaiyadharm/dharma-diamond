import io
from decimal import Decimal
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from fastapi import HTTPException, status

from app.models.invoice_payment import Invoice
from app.models.sale import SalesOrder

def generate_invoice_pdf(db: Session, invoice_id: str) -> io.BytesIO:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CompanyTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e293b")
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#64748b")
    )
    inv_title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#b45309")
    )
    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10
    )
    cell_bold_style = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10
    )

    # Header Table: Company Info (Left) | Invoice Meta (Right)
    header_left = [
        Paragraph("<b>DHARMA DIAMOND</b>", title_style),
        Paragraph("Fine Diamond Jewellery & Certified Solitaires", subtitle_style),
        Paragraph("GSTIN: 27AABCD1234E1Z1 | PAN: AABCD1234E", subtitle_style),
        Paragraph("Tower B, Bharat Diamond Bourse, BKC, Mumbai 400051", subtitle_style),
        Paragraph("Contact: +91 22 2654 8800 | contact@dharmadiamond.com", subtitle_style)
    ]
    header_right = [
        Paragraph("TAX INVOICE", inv_title_style),
        Paragraph(f"<b>Invoice #:</b> {invoice.invoice_number}", subtitle_style),
        Paragraph(f"<b>Date:</b> {invoice.invoice_date.strftime('%d-%b-%Y')}", subtitle_style),
        Paragraph(f"<b>Order Ref:</b> {invoice.sales_order.so_number if invoice.sales_order else '-'}", subtitle_style),
        Paragraph(f"<b>Status:</b> {invoice.status}", subtitle_style)
    ]
    
    header_table = Table(
        [[header_left, header_right]],
        colWidths=[320, 220]
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))

    # Bill-to block
    customer = invoice.customer
    cust_info = [
        Paragraph("<b>BILLED TO:</b>", cell_bold_style),
        Paragraph(f"<b>Name:</b> {customer.name if customer else 'Counter Sale'}", cell_style),
        Paragraph(f"<b>Company:</b> {customer.company_name if customer and customer.company_name else '-'}", cell_style),
        Paragraph(f"<b>GSTIN/PAN:</b> {customer.tax_id if customer and customer.tax_id else 'Unregistered'}", cell_style),
        Paragraph(f"<b>Address:</b> {customer.billing_address if customer and customer.billing_address else '-'}", cell_style),
        Paragraph(f"<b>Phone:</b> {customer.phone if customer and customer.phone else '-'}", cell_style)
    ]
    bill_table = Table([[cust_info]], colWidths=[540])
    bill_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(bill_table)
    story.append(Spacer(1, 15))

    # Items Table
    table_data = [
        [
            Paragraph("<b>#</b>", cell_bold_style),
            Paragraph("<b>SKU / Code</b>", cell_bold_style),
            Paragraph("<b>Item Description</b>", cell_bold_style),
            Paragraph("<b>Qty</b>", cell_bold_style),
            Paragraph("<b>Unit Price (₹)</b>", cell_bold_style),
            Paragraph("<b>Disc (₹)</b>", cell_bold_style),
            Paragraph("<b>Taxable (₹)</b>", cell_bold_style)
        ]
    ]

    so = invoice.sales_order
    items = so.items if so else []
    for idx, it in enumerate(items, 1):
        table_data.append([
            Paragraph(str(idx), cell_style),
            Paragraph(it.sku, cell_style),
            Paragraph(it.description, cell_style),
            Paragraph(str(it.quantity), cell_style),
            Paragraph(f"{it.unit_price:,.2f}", cell_style),
            Paragraph(f"{it.discount:,.2f}", cell_style),
            Paragraph(f"{it.line_total:,.2f}", cell_style)
        ])

    items_table = Table(table_data, colWidths=[25, 90, 205, 35, 65, 55, 65])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 12))

    # Totals breakdown table
    totals_data = [
        [Paragraph("<b>Subtotal:</b>", cell_style), Paragraph(f"₹ {invoice.subtotal:,.2f}", cell_bold_style)],
        [Paragraph("<b>Order Discount:</b>", cell_style), Paragraph(f"₹ {invoice.discount_amount:,.2f}", cell_style)],
        [Paragraph("<b>CGST (1.5%):</b>", cell_style), Paragraph(f"₹ {invoice.cgst_amount:,.2f}", cell_style)],
        [Paragraph("<b>SGST (1.5%):</b>", cell_style), Paragraph(f"₹ {invoice.sgst_amount:,.2f}", cell_style)],
        [Paragraph("<b>Grand Total (INR):</b>", cell_bold_style), Paragraph(f"<b>₹ {invoice.grand_total:,.2f}</b>", cell_bold_style)],
        [Paragraph("<b>Amount Paid:</b>", cell_style), Paragraph(f"₹ {invoice.amount_paid:,.2f}", cell_style)],
        [Paragraph("<b>Balance Due:</b>", cell_bold_style), Paragraph(f"<b>₹ {invoice.balance_due:,.2f}</b>", cell_bold_style)],
    ]
    totals_table = Table(totals_data, colWidths=[120, 110])
    totals_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#fef3c7")),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))

    # Wrap totals aligned to right
    outer_totals = Table(
        [["", totals_table]],
        colWidths=[310, 230]
    )
    outer_totals.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(outer_totals)
    story.append(Spacer(1, 20))

    # Declarations and Signature Box
    footer_text = [
        Paragraph("<b>Terms & Conditions:</b>", cell_bold_style),
        Paragraph("1. All certified diamonds are verified with original lab certificates.", cell_style),
        Paragraph("2. Hallmarked jewellery purity conforms to Bureau of Indian Standards (BIS).", cell_style),
        Paragraph("3. Goods once sold can be exchanged within 7 days in original condition.", cell_style)
    ]
    sign_box = [
        Spacer(1, 20),
        Paragraph("For <b>DHARMA DIAMOND</b>", cell_bold_style),
        Spacer(1, 25),
        Paragraph("Authorized Signatory", cell_style)
    ]
    footer_table = Table(
        [[footer_text, sign_box]],
        colWidths=[350, 190]
    )
    footer_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(footer_table)

    doc.build(story)
    buffer.seek(0)
    return buffer
