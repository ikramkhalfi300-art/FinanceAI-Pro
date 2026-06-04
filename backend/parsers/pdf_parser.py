import pdfplumber
import io

def parse_pdf(file_content: bytes, filename: str) -> dict:
    try:
        text = ""
        tables = []

        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
                page_tables = page.extract_tables()
                for table in page_tables:
                    if table:
                        tables.append(table)

        return {
            "success": True,
            "source": filename,
            "type": "pdf",
            "text": text,
            "tables": tables
        }
    except Exception as e:
        return {"success": False, "error": str(e)}