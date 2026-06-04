import pandas as pd
import io

def parse_csv_excel(file_content: bytes, filename: str) -> dict:
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_content))
        else:
            df = pd.read_excel(io.BytesIO(file_content))

        df.columns = [c.strip().lower() for c in df.columns]
        total_rows = len(df)

        # تلخيص البيانات بدل إرسالها كلها
        summary_text = f"Total rows: {total_rows}\nColumns: {list(df.columns)}\n\n"

        # إذا فيه عمود amount أو total احسب الإحصائيات
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        if numeric_cols:
            summary_text += "NUMERIC SUMMARY:\n"
            summary_text += df[numeric_cols].describe().to_string()
            summary_text += "\n\n"

        # أضف أول 20 صف فقط كأمثلة
        summary_text += "SAMPLE DATA (first 20 rows):\n"
        summary_text += df.head(20).to_string(index=False)

        return {
            "success": True,
            "source": filename,
            "type": "structured",
            "records": df.head(20).to_dict(orient='records'),
            "data_text": summary_text,
            "summary": {
                "total_rows": total_rows,
                "columns": list(df.columns)
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}