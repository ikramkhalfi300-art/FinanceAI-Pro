import anthropic
import base64
import json
import os 
from dotenv import load_dotenv

load_dotenv()

INVOICE_PROMPT = """You are an expert invoice parser. 
Extract all financial data from this invoice image and return ONLY valid JSON:

{
  "vendor": "company name or null",
  "date": "YYYY-MM-DD or null",
  "invoice_number": "string or null",
  "items": [
    {
      "description": "string",
      "quantity": number,
      "unit_price": number,
      "total": number
    }
  ],
  "subtotal": number or null,
  "tax": number or null,
  "total_amount": number or null,
  "currency": "string or null",
  "status": "paid or unpaid or null"
}

Rules:
- Return ONLY the JSON object, no explanation
- All amounts must be numbers not strings
- If field not found use null
- Date format must be YYYY-MM-DD"""

def parse_image(file_content: bytes, filename: str, api_key: str) -> dict:
    try:
        ext = filename.lower().split('.')[-1]
        media_types = {
            'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'png': 'image/png', 'gif': 'image/gif',
            'webp': 'image/webp'
        }
        media_type = media_types.get(ext, 'image/jpeg')
        
        image_b64 = base64.standard_b64encode(file_content).decode('utf-8')

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return {"success": False, "error": "API_Key is missing ! Please chek your .env file."}
        
        client = anthropic.Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64
                        }
                    },
                    {
                        "type": "text",
                        "text": INVOICE_PROMPT
                    }
                ]
            }]
        )
        
        result_text = response.content[0].text.strip()
        result_text = result_text.replace('```json', '').replace('```', '').strip()
        invoice_data = json.loads(result_text)
        
        return {
            "success": True,
            "source": filename,
            "type": "image",
            "invoice": invoice_data
        }
    except Exception as e:
        return {"success": False, "error": str(e)}