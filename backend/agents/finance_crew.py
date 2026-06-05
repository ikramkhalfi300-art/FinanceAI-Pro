import anthropic
import os

def run_finance_analysis(data: str, currency: str, language: str, api_key: str) -> str:
    
    lang_instructions = {
        "ar": "أجب بالعربي فقط",
        "en": "Respond in English only",
        "fr": "Répondez en français uniquement"
    }
    lang_instruction = lang_instructions.get(language, lang_instructions["en"])

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are an expert financial analyst. Analyze this financial data.
Currency: {currency}
Language instruction: {lang_instruction}

DATA:
{data}

Provide a comprehensive analysis including:
1. Revenue & Expense Summary
2. Net Profit/Loss
3. Top 3 Financial Risks
4. Top 3 Recommendations
5. Cash Flow Assessment
6. Financial Health Score (1-10)

{lang_instruction}"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text