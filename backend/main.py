from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import os, sys
from dotenv import load_dotenv

load_dotenv()
latest_analysis = ""

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.parsers.csv_parser import parse_csv_excel
from backend.parsers.pdf_parser import parse_pdf
from backend.parsers.image_parser import parse_image
from backend.agents.finance_crew import run_finance_analysis
from backend.reports.pdf_report import generate_pdf
from backend.reports.pdf_report_ar import generate_pdf as generate_pdf_ar

app = FastAPI(title="FinanceAI Pro")

app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

API_KEY = os.getenv("ANTHROPIC_API_KEY")

cache = {}

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    currency: str = Form(default="USD"),
    language: str = Form(default="en")
):
    try:
        content = await file.read()
        filename = file.filename.lower()

        # اختيار المحلل المناسب
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

        if not parsed.get('success'):
            return JSONResponse({"error": parsed.get('error')}, status_code=400)

        # تشغيل الـ Agents
        analysis = run_finance_analysis(data_text, currency, language, API_KEY)

        global latest_analysis
        latest_analysis = analysis

        return {"analysis": analysis}
        
        cache["last"] = {
            "analysis": analysis,
            "currency": currency,
            "language": language
        }

        return JSONResponse({
            "success": True,
            "file_type": parsed.get('type'),
            "analysis": analysis,
            "currency": currency,
            "language": language
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/download-pdf")
async def download_pdf():
    if "last" not in cache:
        return JSONResponse({"error": "No report available"}, status_code=404)
    
    d = cache["last"]
    if d["Language"] == "ar":
        pdf = generate_pdf_ar(d["analysis"])
    else:
        pdf = generate_pdf(d["analysis"], d["currency"], d["Language"])

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=FinanceAI_Report.pdf"}
    )