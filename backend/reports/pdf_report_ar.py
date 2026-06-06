import io
import os
import urllib.request
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

try:
    from arabic_reshaper import reshape
    from bidi.algorithm import get_display
    def process_arabic(text):
        reshaped = reshape(text)
        return get_display(reshaped)
except ImportError:
    def process_arabic(text):
        return text


def register_arabic_font():
    """تحميل وتسجيل خط عربي — يُحمّل مرة واحدة فقط"""
    font_name = "Amiri"
    font_path = "/tmp/Amiri-Regular.ttf"

    # تحميل الخط إذا لم يكن موجوداً
    if not os.path.exists(font_path):
        url = "https://github.com/aliftype/amiri/releases/download/1.000/Amiri-1.000.zip"
        zip_path = "/tmp/amiri.zip"
        try:
            urllib.request.urlretrieve(
                "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf",
                font_path
            )
        except Exception:
            # بديل ثانٍ
            try:
                urllib.request.urlretrieve(
                    "https://fonts.gstatic.com/s/amiri/v27/J7aRnpd8CGxBHqUpvrIw74NL.ttf",
                    font_path
                )
            except Exception:
                return None  # فشل التحميل

    # تسجيل الخط في ReportLab
    try:
        pdfmetrics.registerFont(TTFont(font_name, font_path))
        return font_name
    except Exception:
        return None


def generate_pdf_ar(analysis_result: str):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # محاولة تسجيل الخط العربي
    arabic_font = register_arabic_font()

    # إذا فشل تحميل الخط، استخدم Helvetica كاحتياط
    font_name = arabic_font if arabic_font else "Helvetica"
    font_name_bold = arabic_font if arabic_font else "Helvetica-Bold"

    title_style = ParagraphStyle(
        'ArabicTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=20,
        leading=30,
        alignment=2,  # يمين
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=20,
        spaceBefore=10,
    )

    heading_style = ParagraphStyle(
        'ArabicHeading',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=14,
        leading=22,
        alignment=2,
        textColor=colors.HexColor("#2B6CB0"),
        spaceAfter=10,
        spaceBefore=15,
    )

    body_style = ParagraphStyle(
        'ArabicBody',
        parent=styles['BodyText'],
        fontName=font_name,
        fontSize=11,
        leading=20,
        alignment=2,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=8,
    )

    story = []

    # العنوان الرئيسي
    story.append(Paragraph(process_arabic("التقرير المالي الذكي"), title_style))
    story.append(Spacer(1, 20))

    # معالجة السطور
    lines = analysis_result.split('\n')
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            story.append(Spacer(1, 8))
            continue

        # تمييز العناوين (تبدأ بـ # أو رقم أو **)
        if clean_line.startswith('#') or clean_line.startswith('**') or (len(clean_line) < 60 and clean_line.endswith(':')):
            clean_line = clean_line.replace('#', '').replace('**', '').strip()
            story.append(Paragraph(process_arabic(clean_line), heading_style))
        else:
            clean_line = clean_line.replace('**', '').strip()
            story.append(Paragraph(process_arabic(clean_line), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()