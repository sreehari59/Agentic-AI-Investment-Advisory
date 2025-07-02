import os
import pyodbc
from dotenv import load_dotenv
import datetime
from agents.analysis_agent import comprehensive_analysis_agent
from agents.reasoning_agent import summarizing_agent
import re
import json
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

   with pyodbc.connect('DRIVER='+db_driver+';SERVER=tcp:'+db_server+';PORT='+db_port+';DATABASE='+db_name+';UID='+db_username+';PWD='+ db_password) as conn:
      with conn.cursor() as cursor:
         cursor.executemany(sql_insert_query, data_to_insert)
         conn.commit()

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

   with pyodbc.connect('DRIVER='+db_driver+';SERVER=tcp:'+db_server+';PORT='+db_port+';DATABASE='+db_name+';UID='+db_username+';PWD='+ db_password) as conn:
               with conn.cursor() as cursor:
                  trade_decision_query = """INSERT INTO trade_decision (group_decision_id, trade_decision_action, trade_decision_quantity,
                        trade_decision_confidence, trade_decision_reasoning)
                        VALUES (?, ?, ?, ?, ?)"""
                  cursor.execute(trade_decision_query,
                              (group_decision_id, trade_decision_action, trade_decision_quantity,
                                 trade_decision_confidence, trade_decision_reasoning))

result = {
   "decisions":{
      "AAPL":{
         "action":"hold",
         "quantity":0,
         "confidence":0.0,
         "reasoning":"Multiple agents indicate bearish signals with high confidence (e.g., valuation agent 71%, sentiment agent 56%). No long position to take, and bearish sentiment outweighs the single bullish signal."
      },
      "MSFT":{
         "action":"hold",
         "quantity":0,
         "confidence":0.0,
         "reasoning":"Mixed signals with bearish dominance (valuation agent 66%, short signals from agents like Bill Ackman and Ben Graham) despite some bullish sentiment. No long position to take, so holding is recommended."
      }
   },
   "analyst_signals":{
      "fundamentals_agent":{
         "AAPL":{
            "signal":"bullish",
            "confidence":50.0,
            "reasoning":{
               "profitability_signal":{
                  "signal":"bullish",
                  "details":"ROE: 151.30%, Net Margin: 24.30%, Op Margin: 31.72%"
               },
               "growth_signal":{
                  "signal":"bearish",
                  "details":"Revenue Growth: 1.16%, Earnings Growth: 1.19%"
               },
               "financial_health_signal":{
                  "signal":"neutral",
                  "details":"Current Ratio: 0.82, D/E: 3.96"
               },
               "price_ratios_signal":{
                  "signal":"bullish",
                  "details":"P/E: 33.64, P/B: 49.01, P/S: 8.18"
               }
            }
         },
         "MSFT":{
            "signal":"neutral",
            "confidence":50.0,
            "reasoning":{
               "profitability_signal":{
                  "signal":"bullish",
                  "details":"ROE: 32.70%, Net Margin: 35.80%, Op Margin: 44.71%"
               },
               "growth_signal":{
                  "signal":"bearish",
                  "details":"Revenue Growth: 3.14%, Earnings Growth: 4.19%"
               },
               "financial_health_signal":{
                  "signal":"bearish",
                  "details":"Current Ratio: 1.37, D/E: 0.75"
               },
               "price_ratios_signal":{
                  "signal":"bullish",
                  "details":"P/E: 28.88, P/B: 8.67, P/S: 10.34"
               }
            }
         }
      },
      "technical_analyst_agent":{
         "AAPL":{
            "signal":"neutral",
            "confidence":15,
            "strategy_signals":{
               "trend_following":{
                  "signal":"bearish",
                  "confidence":26,
                  "metrics":{
                     "adx":25.65029889996752,
                     "trend_strength":0.2565029889996752
                  }
               },
               "mean_reversion":{
                  "signal":"neutral",
                  "confidence":50,
                  "metrics":{
                     "z_score":-0.25646865897646837,
                     "price_vs_bb":0.589975228141504,
                     "rsi_14":48.61159929701231,
                     "rsi_28":41.11830276878821
                  }
               },
               "momentum":{
                  "signal":"neutral",
                  "confidence":50,
                  "metrics":{
                     "momentum_1m":-0.004034512357634523,
                     "momentum_3m":"nan",
                     "momentum_6m":"nan",
                     "volume_momentum":0.004434545817653653
                  }
               },
               "volatility":{
                  "signal":"neutral",
                  "confidence":50,
                  "metrics":{
                     "historical_volatility":0.21402026599876497,
                     "volatility_regime":"nan",
                     "volatility_z_score":"nan",
                     "atr_ratio":0.019180585478928015
                  }
               },
               "statistical_arbitrage":{
                  "signal":"neutral",
                  "confidence":50,
                  "metrics":{
                     "hurst_exponent":4.686994974318529e-16,
                     "skewness":"nan",
                     "kurtosis":"nan"
                  }
               }
            }
         },
         "MSFT":{
            "signal":"bullish",
            "confidence":29,
            "strategy_signals":{
               "trend_following":{
                  "signal":"bullish",
                  "confidence":61,
                  "metrics":{
                     "adx":60.50395597038253,
                     "trend_strength":0.6050395597038253
                  }
               },
               "mean_reversion":{
                  "signal":"neutral",
                  "confidence":50,
                  "metrics":{
                     "z_score":1.0763224323248788,
                     "price_vs_bb":0.7408664761340384,
                     "rsi_14":71.94842406876795,
                     "rsi_28":68.32744867268212
                  }
               },
               "momentum":{
                  "signal":"neutral",
                  "confidence":50,
                  "metrics":{
                     "momentum_1m":0.05382994373668337,
                     "momentum_3m":"nan",
                     "momentum_6m":"nan",
                     "volume_momentum":0.0014897577061413305
                  }
               },
               "volatility":{
                  "signal":"neutral",
                  "confidence":50,
                  "metrics":{
                     "historical_volatility":0.12130677166461937,
                     "volatility_regime":"nan",
                     "volatility_z_score":"nan",
                     "atr_ratio":0.01103701553113861
                  }
               },
               "statistical_arbitrage":{
                  "signal":"neutral",
                  "confidence":50,
                  "metrics":{
                     "hurst_exponent":4.686994974318529e-16,
                     "skewness":"nan",
                     "kurtosis":"nan"
                  }
               }
            }
         }
      },
      "valuation_agent":{
         "AAPL":{
            "signal":"bearish",
            "confidence":71.0,
            "reasoning":{
               "dcf_analysis":{
                  "signal":"bearish",
                  "details":"Intrinsic Value: $1,324,874,739,493.04, Market Cap: $3,273,309,706,700.00, Gap: -59.5%"
               },
               "owner_earnings_analysis":{
                  "signal":"bearish",
                  "details":"Owner Earnings Value: $543,653,179,215.43, Market Cap: $3,273,309,706,700.00, Gap: -83.4%"
               }
            }
         },
         "MSFT":{
            "signal":"bearish",
            "confidence":66.0,
            "reasoning":{
               "dcf_analysis":{
                  "signal":"bearish",
                  "details":"Intrinsic Value: $1,030,484,848,830.36, Market Cap: $2,790,642,591,197.00, Gap: -63.1%"
               },
               "owner_earnings_analysis":{
                  "signal":"bearish",
                  "details":"Owner Earnings Value: $873,164,819,340.93, Market Cap: $2,790,642,591,197.00, Gap: -68.7%"
               }
            }
         }
      },
      "sentiment_agent":{
         "AAPL":{
            "signal":"bearish",
            "confidence":56.00000000000001,
            "reasoning":"Weighted Bullish signals: 140.9, Weighted Bearish signals: 208.8"
         },
         "MSFT":{
            "signal":"bullish",
            "confidence":71.0,
            "reasoning":"Weighted Bullish signals: 263.4, Weighted Bearish signals: 82.1"
         }
      },
      "bill_ackman_agent":{
         "AAPL":{
            "signal":"bearish",
            "confidence":40.0,
            "reasoning":"While Apple (AAPL) demonstrates strong operating margins and exceptional ROE indicative of a competitive moat, the lack of significant revenue growth and concerning balance sheet metrics such as a high debt-to-equity ratio raise red flags. Additionally, the substantial market cap compared to the calculated intrinsic value implies a severe negative margin of safety, suggesting overvaluation. With major risk factors present and a neutral overall signal, a bearish stance is warranted."
         },
         "MSFT":{
            "signal":"bearish",
            "confidence":70.0,
            "reasoning":"Despite MSFT exhibiting strong operating margins and positive free cash flow, the lack of significant revenue growth and the troubling balance sheet with a high debt-to-equity ratio raise concerns. Additionally, with a large negative margin of safety (-72.53%), the stock is significantly overvalued compared to its intrinsic value, leading to a bearish outlook."
         }
      },
      "cathie_wood_agent":{
         "AAPL":{
            "signal":"bearish",
            "confidence":65.0,
            "reasoning":"Despite positive operating leverage and a healthy focus on reinvestment, AAPL currently lacks an adequate margin of safety as its market capitalization exceeds its calculated intrinsic value by 17.92%. The company's growth potential is hindered by a bearish valuation analysis, which diminishes the attractiveness of investing in a mature tech company. Therefore, I recommend a bearish stance on this stock."
         },
         "MSFT":{
            "signal":"neutral",
            "confidence":60.0,
            "reasoning":"MSFT exhibits a moderate potential for innovation with solid R&D investments (13.5% of revenue) and a healthy operating margin (38.9%). However, the substantial negative margin of safety (-40.64%) indicates that the stock is currently overvalued compared to its intrinsic value. While there are positive elements, such as a strong focus on reinvestment and increasing R&D intensity, the overvaluation concerns balance out the positives, leading to a neutral signal."
         }
      },
      "warren_buffett_agent":{
         "AAPL":{
            "signal":"bearish",
            "confidence":75.0,
            "reasoning":"AAPL has a negative margin of safety of -41.2%, indicating that the stock is currently overvalued compared to its intrinsic value. Additionally, there is a high debt-to-equity ratio of 4.0, further raising concerns about financial strength. Earnings growth patterns are inconsistent, with a total earnings decline of -3.1% over the past five periods. Given these factors, it is advisable to avoid or sell this investment."
         },
         "MSFT":{
            "signal":"bearish",
            "confidence":20.0,
            "reasoning":"While MSFT demonstrates strong earnings growth and financial strength, the current margin of safety is less than 30%, indicating the stock is overvalued at its current price. Furthermore, the current liquidity position is not ideal with a current ratio of 1.4, and the significant debt to equity ratio of 0.7 could be risky in a downturn. Selling or avoiding this investment aligns with maintaining a margin of safety and prudent investment principles."
         }
      },
      "charlie_munger_agent":{
         "AAPL":{
            "signal":"neutral",
            "confidence":65.0,
            "reasoning":"AAPL demonstrates excellent predictability in revenue and operations, alongside a strong competitive advantage with high ROIC and good pricing power. However, the high valuation, with a significant premium to its reasonable value and low FCF yield of 3.0%, presents a concern for potential overvaluation. The management analysis reveals a solid cash conversion but also a high debt level which might be a risk factor. The combination of these elements leads to a neutral investment signal, indicating that while AAPL is a robust business, it is trading at a price that does not provide a sufficient margin of safety."
         },
         "MSFT":{
            "signal":"neutral",
            "confidence":60.0,
            "reasoning":"Microsoft (MSFT) displays solid quality characteristics, particularly in terms of its excellent ROIC and predictable revenue growth. However, its valuation is concerning, with a low FCF yield of 2.2% and a 67.7% premium to its reasonable value. While the business has strong management and a competitive moat, the expensive valuation and the need for a qualitative assessment of recent news sentiment prevent a bullish stance. Long-term investors should remain cautious and monitor for a more favorable entry point."
         }
      },
      "ben_graham_agent":{
         "AAPL":{
            "signal":"bearish",
            "confidence":75.0,
            "reasoning":"Despite stable EPS, the lack of growth and a weak current ratio indicate potential liquidity issues. The debt ratio suggests higher leverage, and the significant negative margin of safety relative to the Graham Number raises concerns about valuation, leading to a bearish stance."
         },
         "MSFT":{
            "signal":"bearish",
            "confidence":75.0,
            "reasoning":"While MSFT demonstrates strong financial strength with a solid current ratio and a decent history of paying dividends, the lack of earnings growth and a significant negative margin of safety based on the Graham Number indicate that it is trading well above its intrinsic value. This leads to a bearish outlook as it does not align with Graham's principle of buying below intrinsic value."
         }
      },
      "risk_management_agent":{
         "AAPL":{
            "remaining_position_limit":20000.0,
            "current_price":201.0,
            "reasoning":{
               "portfolio_value":100000.0,
               "current_position":0.0,
               "position_limit":20000.0,
               "remaining_limit":20000.0,
               "available_cash":100000.0
            }
         },
         "MSFT":{
            "remaining_position_limit":20000.0,
            "current_price":477.4,
            "reasoning":{
               "portfolio_value":100000.0,
               "current_position":0.0,
               "position_limit":20000.0,
               "remaining_limit":20000.0,
               "available_cash":100000.0
            }
         }
      }
   }
}


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


tickers = ["AAPL","MSFT"]
selected_analysts = ["cathie_wood","valuation_analyst", "sentiment_analyst", "technical_analyst", "fundamentals_analyst"]
# selected_analysts = ["cathie_wood", "technical_analyst", "fundamentals_analyst"]
model_choice = "gpt-4o-mini"


prefix = "GD_" 
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
group_decision_id = prefix + timestamp
for ticker_val in tickers:
   final_output = []
   for analyst in selected_analysts:
      final_output.append(get_agent_data(result, analyst, ticker_val, group_decision_id, model_choice))
   
   agent_data_query = """INSERT INTO AgentTradeInfo (ticker, analyst_name, signal, analyst_confidence, 
                        llm_name, execution_date, group_decision_id, agent_signals, agent_reasoning,
                        analysis_summary)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
   insert_into_sql_server(agent_data_query , final_output)
   insert_trade_decision(result, ticker_val, group_decision_id)

   break


