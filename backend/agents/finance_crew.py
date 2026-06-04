from crewai import Agent, Task, Crew, LLM
import asyncio
import concurrent.futures

def run_finance_analysis(data: str, currency: str, language: str, api_key: str) -> str:
    
    lang_instructions = {
        "ar": "Respond in Arabic only / أجب بالعربي فقط",
        "en": "Respond in English only",
        "fr": "Répondez en français uniquement"
    }
    lang_instruction = lang_instructions.get(language, lang_instructions["en"])

    claude_llm = LLM(
        model="claude-sonnet-4-5",
        api_key=api_key
    )

    def _run_crew():
        analyst = Agent(
            role="Senior Financial Analyst",
            goal=f"Analyze financial data accurately. {lang_instruction}",
            backstory="Expert financial analyst with 15 years experience.",
            llm=claude_llm,
            verbose=False
        )

        advisor = Agent(
            role="Financial Advisor",
            goal=f"Provide actionable recommendations. {lang_instruction}",
            backstory="Strategic financial advisor specializing in optimization.",
            llm=claude_llm,
            verbose=False
        )

        task1 = Task(
            description=f"""Analyze this financial data in {currency}:
            {data}
            Calculate revenues, expenses, net profit, profit margin, pending payments.
            {lang_instruction}""",
            expected_output=f"Detailed financial analysis in {currency}",
            agent=analyst
        )

        task2 = Task(
            description=f"""Provide:
            1. Top 3 risks
            2. Top 3 recommendations  
            3. Cash flow assessment
            4. Financial health score 1-10
            {lang_instruction}""",
            expected_output=f"Strategic recommendations in {language}",
            agent=advisor
        )

        crew = Crew(
            agents=[analyst, advisor],
            tasks=[task1, task2],
            verbose=False
        )
        return str(crew.kickoff())

    # تشغيل في thread منفصل لتجنب تعارض event loop
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(_run_crew)
        result = future.result(timeout=300)
    
    return result