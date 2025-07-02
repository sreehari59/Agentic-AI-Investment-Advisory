from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv() 

def summarizing_agent(comprehensive_analysis: str, agent_name: str, ticker: str) -> str:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY') ) 
    prompt = f"""
        You are a summarizing agent. The input below is a comprehensive analysis of {ticker} stock by {agent_name}
        Your task is to produce a clear, concise summary that captures the key takeaways. Include:
        1. A brief summary of the overall investment outlook (bullish, bearish, or neutral).
        2. The most significant strengths and weaknesses from the analysis.
        3. A one-sentence bottom-line recommendation or sentiment based on the overall analysis.
        Keep the tone professional, neutral, and suited for a portfolio manager or investor briefing.

         Instructions:
        -     Retrun a json response with the following format:
            {{
                "llm_reasoning": "one clear sentence summarizing"
            }}
        -    Do not include any additional text or explanation.

        Here is the comprehensive analysis to summarize:
        {comprehensive_analysis}
        """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return completion.choices[0].message.content