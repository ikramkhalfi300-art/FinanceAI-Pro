import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf(analysis_result: str, currency: str = "USD", language: str = "en"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    # استخدام خط Helvetica الافتراضي والمتاح دائماً على سيرفرات Linux
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=20
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=10
    )
    
    story = []
    
    # عنوان التقرير
    title_text = "Financial Analysis & Insights Report" if language == "en" else "Rapport d'Analyse Financière"
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 15))
    
    # تقسيم النص إلى أسطر وفقرات
    lines = analysis_result.split('\n')
    for line in lines:
        clean_line = line.strip()
        if clean_line:
            story.append(Paragraph(clean_line, body_style))
        else:
            story.append(Spacer(1, 8))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()