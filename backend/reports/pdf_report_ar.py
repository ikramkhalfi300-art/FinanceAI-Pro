import os
from io import BytesIO
import urllib.request
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# رابط مباشر لجلب الخط العربي الاحترافي من خوادم جوجل مباشرة للسيرفر
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"

try:
    with urllib.request.urlopen(FONT_URL) as response:
        font_data = BytesIO(response.read())
    pdfmetrics.registerFont(TTFont('ArabicFont', font_data))
except Exception as e:
    print(f"Error loading remote font: {e}")
    pdfmetrics.registerFont(TTFont('ArabicFont', 'Helvetica'))

def process_arabic(text):
    if not text:
        return ""
    reshaped_text = reshape(str(text))
    bidi_text = get_display(reshaped_text)
    return bidi_text

def generate_pdf(analysis_result: str, output_path: str = "financial_report_ar.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ArabicTitle',
        parent=styles['Heading1'],
        fontName='ArabicFont',
        fontSize=24,
        leading=28,
        alignment=1,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=20
    )
    
    body_style = ParagraphStyle(
        'ArabicBody',
        parent=styles['BodyText'],
        fontName='ArabicFont',
        fontSize=12,
        leading=18,
        alignment=2,
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
            arabic_paragraph = process_arabic(clean_line)
            story.append(Paragraph(arabic_paragraph, body_style))
        else:
            story.append(Spacer(1, 8))
            
    doc.build(story)
    return output_path