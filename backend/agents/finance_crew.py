import anthropic
import os

def run_finance_analysis(data: str, currency: str, language: str, api_key: str) -> str:
    
    language = language.lower().strip()

    print(f"CREW DEBUG >>> language = '{language}'", flush=True)
    
    prompts = {
        "ar": f"""أنت محلل مالي خبير. حلل هذه البيانات المالية بالعربي فقط.
العملة: {currency}

البيانات:
{data}

قدم تحليلاً شاملاً يتضمن:
1. ملخص الإيرادات والمصاريف
2. صافي الربح أو الخسارة
3. أكبر 3 مخاطر مالية
4. أفضل 3 توصيات
5. تقييم التدفق النقدي
6. تقييم الصحة المالية من 1 إلى 10

تذكر: أجب بالعربي فقط""",

        "fr": f"""Vous êtes un analyste financier expert. Analysez ces données financières en français uniquement.
Devise: {currency}

Données:
{data}

Fournissez une analyse complète incluant:
1. Résumé des revenus et dépenses
2. Bénéfice/perte net
3. Top 3 risques financiers
4. Top 3 recommandations
5. Évaluation des flux de trésorerie
6. Score de santé financière (1-10)

Répondez en français uniquement""",

        "en": f"""You are an expert financial analyst. Analyze this financial data in English only.
Currency: {currency}

Data:
{data}

Provide a comprehensive analysis including:
1. Revenue & Expense Summary
2. Net Profit/Loss
3. Top 3 Financial Risks
4. Top 3 Recommendations
5. Cash Flow Assessment
6. Financial Health Score (1-10)

Respond in English only"""
    }

    prompt = prompts.get(language, prompts["en"])

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text