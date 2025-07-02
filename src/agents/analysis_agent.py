from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv() 

def comprehensive_analysis_agent(initial_analysis: str, agent_name: str, ticker: str, signals) -> str:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY') ) 
    prompt = f"""
       You are a financial analyst. Below is structured data from {agent_name} for the stock {ticker}
       Based on the data, provide a comprehensive analysis of the data and give a detailed explanation on the data 
       coming under each of the headings/signals: {signals}

        Instructions:
        -    Retrun a json response with the following format:
            {{
                "comprehensive_analysis": "Only give the comprehensive analysis"
            }}
        -    Do not include any additional text or explanation.

        data:
        {initial_analysis}
        """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return completion.choices[0].message.content