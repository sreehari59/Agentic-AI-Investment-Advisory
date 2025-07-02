import os
import pyodbc
from dotenv import load_dotenv
import datetime
import re
import json
from agents.analysis_agent import comprehensive_analysis_agent
from agents.reasoning_agent import summarizing_agent
load_dotenv() 

def extract_json(text):
    # Use regex to extract JSON block from mixed content
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
      json_str = match.group(0)
      try:
         data = json.loads(json_str)
         return data
      except json.JSONDecodeError as e:
         print("JSON parsing failed:", e)
    else:
      print("No JSON found in input.")
      return text

def insert_into_sql_server(sql_insert_query , data_to_insert):
    """
    Insert data into SQL Server table.
    
    :param sql_insert_query: SQL insert query string with placeholders for data.
    :param data_to_insert: Data to be inserted into the SQL Server table.
    """
    db_server = os.getenv('DB_SERVER')
    db_name = os.getenv('DB_NAME')
    db_username = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT')
    db_driver = os.getenv('DRIVER')

    try:
        with pyodbc.connect('DRIVER='+db_driver+';SERVER=tcp:'+db_server+';PORT='+db_port+';DATABASE='+db_name+';UID='+db_username+';PWD='+ db_password) as conn:
            with conn.cursor() as cursor:
                cursor.executemany(sql_insert_query, data_to_insert)
                conn.commit()
        print("Data inserted succesfully")
    
    except Exception as e:
        print("Error while inserting data into SQL Server:", e)

def insert_trade_decision(result, ticker, group_decision_id):
    
    trade_decision_confidence = result["decisions"][ticker]["confidence"]
    trade_decision_quantity = result["decisions"][ticker]["quantity"]
    trade_decision_action = result["decisions"][ticker]["action"]
    trade_decision_reasoning = result["decisions"][ticker]["reasoning"]


    db_server = os.getenv('DB_SERVER')
    db_name = os.getenv('DB_NAME')
    db_username = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT')
    db_driver = os.getenv('DRIVER')
        
    try:
        with pyodbc.connect('DRIVER='+db_driver+';SERVER=tcp:'+db_server+';PORT='+db_port+';DATABASE='+db_name+';UID='+db_username+';PWD='+ db_password) as conn:
                with conn.cursor() as cursor:
                    trade_decision_query = """INSERT INTO trade_decision (group_decision_id, trade_decision_action, trade_decision_quantity,
                            trade_decision_confidence, trade_decision_reasoning)
                            VALUES (?, ?, ?, ?, ?)"""
                    cursor.execute(trade_decision_query,
                                (group_decision_id, trade_decision_action, trade_decision_quantity,
                                    trade_decision_confidence, trade_decision_reasoning))
        print("Data inserted succesfully")
    
    except Exception as e:
        print("Error while inserting data into SQL Server:", e)

def insert_agent_trade_data(result, agent_name, ticker, llm_name):
    
    agent_mapper = {
         "ben_graham" : "ben_graham_agent",
         "bill_ackman": "bill_ackman_agent",
         "cathie_wood": "cathie_wood_agent",
         "charlie_munger": "charlie_munger_agent",
         "warren_buffett": "warren_buffett_agent",
         "technical_analyst": "technical_analyst_agent",
         "fundamentals_analyst": "fundamentals_agent",
         "sentiment_analyst": "sentiment_agent",
         "valuation_analyst": "valuation_agent"
   }
    analyst_name = agent_mapper.get(agent_name)
    signal = result["analyst_signals"][analyst_name][ticker]["signal"]
    analyst_confidence = result["analyst_signals"][analyst_name][ticker]["confidence"]
    llm_reasoning = result["analyst_signals"][analyst_name][ticker]["reasoning"]
    trade_decision_confidence = result["decisions"][ticker]["confidence"]
    trade_decision_quantity = result["decisions"][ticker]["quantity"]
    trade_decision_action = result["decisions"][ticker]["action"]

    db_server = os.getenv('DB_SERVER')
    db_name = os.getenv('DB_NAME')
    db_username = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT')
    db_driver = os.getenv('DRIVER')
    try:
        with pyodbc.connect('DRIVER='+db_driver+';SERVER=tcp:'+db_server+';PORT='+db_port+';DATABASE='+db_name+';UID='+db_username+';PWD='+ db_password) as conn:
                    with conn.cursor() as cursor:
                        insert_trade_data = """INSERT INTO AgentTradeInfo (ticker, analyst_name, signal, analyst_confidence, 
                                            trade_decision_action, trade_decision_quantity, trade_decision_confidence, 
                                            llm_reasoning, llm_name, execution_date)
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                        cursor.execute(insert_trade_data,
                                    (ticker, analyst_name, signal, analyst_confidence, trade_decision_action,
                                        trade_decision_quantity, trade_decision_confidence, llm_reasoning, 
                                        llm_name, datetime.datetime.now()))
                        
        print("Data inserted succesfully")
    
    except Exception as e:
        print("Error while inserting data into SQL Server:", e)

def get_agent_data(result, agent_name, ticker, group_decision_id, llm_name="gpt-4o"):
   agent_mapper = {
         "ben_graham" : "ben_graham_agent",
         "bill_ackman": "bill_ackman_agent",
         "cathie_wood": "cathie_wood_agent",
         "charlie_munger": "charlie_munger_agent",
         "warren_buffett": "warren_buffett_agent",
         "technical_analyst": "technical_analyst_agent",
         "fundamentals_analyst": "fundamentals_agent",
         "sentiment_analyst": "sentiment_agent",
         "valuation_analyst": "valuation_agent"
   }
   analyst_name = agent_mapper.get(agent_name)
   if "technical_analyst_agent" in analyst_name:
      # Is the reasoning or signal by the ai hedge fund agent
      agent_signals = str(result["analyst_signals"][analyst_name][ticker]["strategy_signals"])
      different_signals = ", ".join(result["analyst_signals"][analyst_name][ticker]["strategy_signals"].keys())
      # Agent to do a comprehensive ana
      agent_reasoning =  extract_json(comprehensive_analysis_agent(agent_signals, analyst_name, ticker, different_signals))
      agent_reasoning = agent_reasoning.get("comprehensive_analysis")
      summarized_reponse = summarizing_agent(agent_reasoning, analyst_name, ticker)

   elif ("fundamentals_agent" in analyst_name) or ("valuation_agent" in analyst_name):
      agent_signals = str(result["analyst_signals"][analyst_name][ticker]["reasoning"])
      different_signals = ", ".join(result["analyst_signals"][analyst_name][ticker]["reasoning"].keys())
      # Agent to do a comprehensive ana
      agent_reasoning =  extract_json(comprehensive_analysis_agent(agent_signals, analyst_name, ticker, different_signals))
      agent_reasoning = agent_reasoning.get("comprehensive_analysis")
      summarized_reponse = summarizing_agent(agent_reasoning, analyst_name, ticker)

   else:
      agent_reasoning = result["analyst_signals"][analyst_name][ticker]["reasoning"] 
      summarized_reponse = summarizing_agent(agent_reasoning, analyst_name, ticker)

   
   signal = result["analyst_signals"][analyst_name][ticker]["signal"]
   analyst_confidence = result["analyst_signals"][analyst_name][ticker]["confidence"]
   
   analysis_summary = extract_json(summarized_reponse)
   print(analysis_summary)
   agent_signals = ""
   return (ticker, analyst_name, signal, analyst_confidence, llm_name,
               datetime.datetime.now(), group_decision_id, agent_signals,
               agent_reasoning, analysis_summary.get("llm_reasoning"))