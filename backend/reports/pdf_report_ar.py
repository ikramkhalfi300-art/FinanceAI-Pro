import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# إذا كانت دالتك تستخدم مكتبة bidi أو arabic_reshaper لتنسيق الكلمات العربية
try:
    from arabic_reshaper import reshape
    from bidi.algorithm import get_display
    def process_arabic(text):
        return get_display(reshape(text))
except ImportError:
    def process_arabic(text):
        return text

def generate_pdf_ar(analysis_result: str):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    # استخدام خط Helvetica كبديل آمن يمنع انهيار السيرفر مؤقتاً لحين رفع ملفات الخطوط العربية
    title_style = ParagraphStyle(
        'ArabicTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        alignment=2, # محاذاة لليمين
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=15
    )
    
    body_style = ParagraphStyle(
        'ArabicBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=12,
        leading=18,
        alignment=2, # محاذاة لليمين
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=10
    )
    
    story = []
    
    title_text = "التقرير والتحليل المالي الذكي"
    story.append(Paragraph(process_arabic(title_text), title_style))
    story.append(Spacer(1, 15))
    
    lines = analysis_result.split('\n')
    for line in lines:
        clean_line = line.strip()
        if clean_line:
            story.append(Paragraph(process_arabic(clean_line), body_style))
        else:
            story.append(Spacer(1, 8))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()