import os
import sys
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# حل مشكلة المسارات نهائياً: إضافة المجلد الحالي ومجلد backend إلى مسارات بايثون
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, "backend"))

# استدعاء الدوال بمساراتها الصريحة والمباشرة المضمونة على السيرفر
from backend.parsers.csv_parser import parse_csv_excel
from backend.parsers.image_parser import parse_image
from backend.parsers.pdf_parser import parse_pdf
from backend.agents.finance_crew import run_finance_analysis
from backend.reports.pdf_report_ar import generate_pdf_ar
from backend.reports.pdf_report import generate_pdf

# تحميل متغيرات البيئة
load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not API_KEY:
    print("ERROR : ANTHROPIC_API_KEY is not found !")

app = FastAPI()

# إعداد الـ CORS للمتصفح
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ذاكرة مؤقتة (Cache) لحفظ آخر تقرير تم إنشاؤه بنجاح
cache = {}

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return HTMLResponse(content=f"<h3>Error loading index.html: {str(e)}</h3>", status_code=500)

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    currency: str = Form(default="USD"),
    Language: str = Form(default="en")
):
    try:
        content = await file.read()
        filename = file.filename.lower()
        
        # إعطاء قيم ابتدائية متينة لمنع أي خطأ غير متوقع
        data_text = ""
        parsed = {"success": False, "error": "Unknown file format"}
        
        # 1. التحقق من نوع الملف وتشغيل المعالج المناسب
        if filename.endswith(('.csv', '.xlsx', '.xls')):
            parsed = parse_csv_excel(content, filename)
            data_text = parsed.get('data_text', str(parsed.get('records', '')))
            
        elif filename.endswith('.pdf'):
            parsed = parse_pdf(content, filename)
            data_text = parsed.get('data_text', str(parsed.get('records', '')))
            
        elif filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
            parsed = parse_image(content, filename, API_KEY)
            data_text = parsed.get('data_text', str(parsed.get('records', '')))
        else:
            return JSONResponse({"error": "Unsupported file type"}, status_code=400)
            
        # التأكد من نجاح معالجة الملف واستخراج النصوص
        if not parsed.get('success'):
            return JSONResponse({"error": parsed.get('error', 'Failed to parse file')}, status_code=400)
            
        # 2. تشغيل الـ Agents لتوليد التحليل المالي بناءً على النصوص المستخرجة
        language_lower = Language.lower().strip()
        analysis = run_finance_analysis(data_text, currency, Language, API_KEY)
        
        # 3. حفظ النتيجة والمعلومات الحالية في الكاش بأمان لأجل دالة التحميل
        cache["last"] = {
            "analysis": analysis,
            "currency": currency,
            "Language": language_lower
        }
        
        return JSONResponse({
            "success": True,
            "analysis": analysis,
            "currency": currency,
            "Language": language_lower
        })
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error occurred: {error_detail}")
        return JSONResponse({"error": str(e),"detail":error_detail}, status_code=500)

@app.get("/download-pdf")
async def download_pdf():
    # التحقق من وجود بيانات في الكاش
    if "last" not in cache:
        return JSONResponse({"error": "No report available"}, status_code=404)
        
    d = cache["last"]
    
    lang = d.get("Language") or d.get("language") or "en"
    analysis_text = d.get("analysis", "")
    currency_type = d.get("currency", "USD")
    
    # التوجيه الذكي للمكتبة المناسبة بناءً على اللغة المختارة لضمان عدم الانهيار
    if lang == "ar":
        pdf = generate_pdf_ar(analysis_text)
    else:
        pdf = generate_pdf(analysis_text, currency_type, lang)
        
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=FinanceAI_Report.pdf"}
    )