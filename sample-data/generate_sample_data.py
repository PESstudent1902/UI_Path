import os
import sys

def create_pdfs():
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
    except ImportError:
        print("[WARNING] reportlab library is not installed. Installing it now to generate sample PDFs...")
        # Since we're running script, let the script try installing it dynamically or guide the user
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

    data_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(data_dir, exist_ok=True)
    
    # ------------------ SAMPLE 1: CLASSIC POLO SHIRT ------------------
    pdf1_path = os.path.join(data_dir, "sample_techpack_1.pdf")
    doc1 = SimpleDocTemplate(pdf1_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    story1 = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=15
    )
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#4B5563'),
        spaceBefore=12,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#374151')
    )
    
    # Title
    story1.append(Paragraph("TECHNICAL SPECIFICATION SHEET - TECH PACK", title_style))
    story1.append(Paragraph("<b>Buyer:</b> Fashion Brand Ltd &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Brand Reference:</b> FB-2026", body_style))
    story1.append(Paragraph("<b>Style Name:</b> Classic Polo Shirt &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Style Number:</b> FB-2026-P001", body_style))
    story1.append(Paragraph("<b>Garment Type:</b> Polo Shirt &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Date Created:</b> 2026-05-20", body_style))
    story1.append(Spacer(1, 10))
    
    # Section 1: Fabric Spec
    story1.append(Paragraph("1. FABRIC SPECIFICATIONS", section_title_style))
    story1.append(Paragraph("<b>Fabric Composition:</b> 100% Cotton Pique", body_style))
    story1.append(Paragraph("<b>Fabric Weight:</b> 200 GSM (grams per square meter)", body_style))
    story1.append(Paragraph("<b>Cuttable Fabric Width:</b> 60 inches cut-to-cut", body_style))
    story1.append(Paragraph("<b>Colorways:</b> White, Navy, Black, Red", body_style))
    story1.append(Paragraph("<b>Size Range:</b> S, M, L, XL", body_style))
    story1.append(Spacer(1, 10))
    
    # Section 2: Measurements Table
    story1.append(Paragraph("2. SIZE SPECIFICATION & MEASUREMENTS TABLE (inches)", section_title_style))
    meas_data = [
        ["Size Component", "S", "M", "L", "XL", "Tol (+/-)"],
        ["Chest Width", "38.0", "40.0", "42.0", "44.0", "0.5"],
        ["Body Length", "27.0", "28.0", "29.0", "30.0", "0.75"],
        ["Sleeve Length", "8.0", "8.5", "9.0", "9.5", "0.25"],
        ["Shoulder Width", "16.0", "17.0", "18.0", "19.0", "0.5"]
    ]
    meas_table = Table(meas_data, colWidths=[150, 60, 60, 60, 60, 80])
    meas_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4B5563')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story1.append(meas_table)
    story1.append(Spacer(1, 10))
    
    # Section 3: Bill of Materials
    story1.append(Paragraph("3. BILL OF MATERIALS (BOM) DETAILS", section_title_style))
    bom_data = [
        ["Item Category / Name", "Unit Type", "Consumption per Piece"],
        ["Main fabric - Cotton Pique", "yards", "1.80"],
        ["Rib fabric - collar/cuffs", "yards", "0.30"],
        ["Interlining - collar", "yards", "0.15"],
        ["Thread - main", "meters", "180.0"],
        ["Buttons - 3 hole", "pieces", "3.00"],
        ["Care label", "pieces", "1.00"],
        ["Size label", "pieces", "1.00"]
    ]
    bom_table = Table(bom_data, colWidths=[200, 100, 150])
    bom_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#6B7280')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story1.append(bom_table)
    story1.append(Spacer(1, 10))
    
    # Section 4: Construction
    story1.append(Paragraph("4. CONSTRUCTION DETAILS", section_title_style))
    story1.append(Paragraph("<b>Seam Type:</b> French seam on side seams, overlock on sleeves to prevent fraying.", body_style))
    story1.append(Paragraph("<b>Stitch Density:</b> 12-14 SPI (Stitches Per Inch) lockstitch", body_style))
    story1.append(Paragraph("<b>Special Processes:</b> Bio-Enzyme wash for soft handfeel. Silicon softener finish.", body_style))
    
    doc1.build(story1)
    print(f"Generated clean tech pack: {pdf1_path}")
    
    # ------------------ SAMPLE 2: MESSY CREWNECK TEE (Missing fields for exception test) ------------------
    pdf2_path = os.path.join(data_dir, "sample_techpack_2.pdf")
    doc2 = SimpleDocTemplate(pdf2_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    story2 = []
    
    story2.append(Paragraph("TECHNICAL SPECIFICATION SHEET - STYLE BRIEF", title_style))
    story2.append(Paragraph("<b>Buyer:</b> Fashion Brand Ltd &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Brand Reference:</b> FB-2026", body_style))
    story2.append(Paragraph("<b>Style Name:</b> Essential Crewneck Tee &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Style Number:</b> FB-2026-T002", body_style))
    story2.append(Paragraph("<b>Garment Type:</b> T-shirt &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Date Created:</b> 2026-05-20", body_style))
    story2.append(Spacer(1, 10))
    
    story2.append(Paragraph("1. GENERAL BRIEF", section_title_style))
    story2.append(Paragraph("<b>Fabric:</b> Poly-Cotton Blend Jersey (65% Polyester, 35% Cotton)", body_style))
    story2.append(Paragraph("<b>Weight / GSM:</b> <font color=\"#DC2626\">GSM details not specified in client worksheet.</font>", body_style))
    story2.append(Paragraph("<b>Width:</b> 58 inches width", body_style))
    story2.append(Paragraph("<b>Colorways:</b> Heather Gray, Charcoal, Olive (Pantone standards pending)", body_style))
    story2.append(Paragraph("<b>Sizes:</b> S, M, L", body_style))
    story2.append(Spacer(1, 10))
    
    # Section 2: Measurements Table
    story2.append(Paragraph("2. SPEC MEASUREMENTS TABLE (inches)", section_title_style))
    meas_data2 = [
        ["Size", "S", "M", "L"],
        ["Chest Width", "36.0", "38.0", "40.0"],
        ["Body Length", "26.0", "27.0", "28.0"],
        ["Sleeve Length", "7.5", "8.0", "8.5"],
        ["Shoulder", "15.5", "16.5", "17.5"]
    ]
    meas_table2 = Table(meas_data2, colWidths=[150, 80, 80, 80])
    meas_table2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#6B7280')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story2.append(meas_table2)
    story2.append(Spacer(1, 10))
    
    # Section 3: Bill of Materials (Incomplete)
    story2.append(Paragraph("3. BILL OF MATERIALS", section_title_style))
    bom_data2 = [
        ["Item Category / Name", "Unit Type", "Consumption per Piece"],
        ["Main fabric - Poly Cotton Blend", "yards", "1.40"],
        ["Thread - main", "meters", "120.0"],
        ["Care label", "pieces", "1.00"]
    ]
    bom_table2 = Table(bom_data2, colWidths=[200, 100, 150])
    bom_table2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#9CA3AF')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story2.append(bom_table2)
    story2.append(Spacer(1, 10))
    
    # Section 4: Construction
    story2.append(Paragraph("4. ASSEMBLY METHODS", section_title_style))
    story2.append(Paragraph("<b>Seam Type:</b> Overlock stitch on main panels. Single needle topstitch neck rib.", body_style))
    story2.append(Paragraph("<b>Stitch Density:</b> 10-12 SPI", body_style))
    story2.append(Paragraph("<b>Special Treatments:</b> None specified.", body_style))
    
    doc2.build(story2)
    print(f"Generated messy tech pack: {pdf2_path}")

if __name__ == "__main__":
    create_pdfs()
