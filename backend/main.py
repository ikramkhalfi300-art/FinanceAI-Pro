import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# التعديل الذهبي: الاستدعاء المباشر المتوافق مع بيئة تشغيل السيرفر
try:
    from backend.parsers import parse_csv_excel, parse_pdf, parse_image
    from backend.agents import run_finance_analysis
    from backend.reports.pdf_report_ar import generate_pdf_ar
    from backend.reports.pdf_report import generate_pdf
except ImportError:
    from parsers import parse_csv_excel, parse_pdf, parse_image
    from agents import run_finance_analysis
    from reports.pdf_report_ar import generate_pdf_ar
    from reports.pdf_report import generate_pdf

# تحميل متغيرات البيئة
load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")

app = FastAPI()

# إعداد الـ CORS للمتصفح
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ذاكرة مؤقتة (Cache) لحفظ آخر تقرير تم إنشاؤه
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
        
        # 1. اختيار المحلل المناسب بناءً على نوع الملف
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
            
        # التأكد من نجاح معالجة الملف
        if not parsed.get('success'):
            return JSONResponse({"error": parsed.get('error')}, status_code=400)
            
        # 2. تشغيل الـ Agents لتوليد التحليل المالي
        analysis = run_finance_analysis(data_text, currency, Language, API_KEY)
        
        # 3. حفظ النتيجة والمعلومات الحالية في الكاش بأمان لأجل دالة التحميل
        cache["last"] = {
            "analysis": analysis,
            "currency": currency,
            "Language": Language
        }
        
        return {"analysis": analysis}
        
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/download-pdf")
async def download_pdf():
    if "last" not in cache:
        return JSONResponse({"error": "No report available"}, status_code=404)
        
    d = cache["last"]
    
    # جلب البيانات بأمان لتفادي أي خطأ في حالة الأحرف
    lang = d.get("Language") or d.get("language") or "en"
    analysis_text = d.get("analysis", "")
    currency_type = d.get("currency", "USD")
    
    # التوجيه الذكي بناءً على اللغة المختارة
    if lang == "ar":
        pdf = generate_pdf_ar(analysis_text)
    else:
        pdf = generate_pdf(analysis_text, currency_type, lang)
        
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=FinanceAI_Report.pdf"}
    )