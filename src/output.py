
# poetry run python src/main.py --ticker MSFT
result1 = {
    'decisions': {
            'MSFT': {
                'action': 'short',
                'quantity': 41,
                'confidence': 85.0, 
                'reasoning': 'The analysis indicates a bearish signal for MSFT with high confidence (85.0%). Considering I have no current long or short positions on MSFT, and I have sufficient margin to initiate a short position, I will proceed to short the maximum allowed shares (41).'
                }
            }, 
    'analyst_signals': {
        'ben_graham_agent': {
            'MSFT': {
                'signal': 'bearish', 
                'confidence': 85.0, 
                'reasoning': 'MSFT shows a lack of margin of safety, with a current price significantly above the Graham Number, indicating overvaluation. While financial strength indicators like a solid current ratio exist, high debt levels and stagnant EPS growth provide further concern. Hence, a bearish outlook is warranted.'
                }
            }, 
        'risk_management_agent': {
            'MSFT': {
                'remaining_position_limit': 20000.0, 
                'current_price': 479.78, 
                'reasoning': {
                    'portfolio_value': 100000.0, 
                    'current_position': 0.0, 
                    'position_limit': 20000.0, 
                    'remaining_limit': 20000.0, 
                    'available_cash': 100000.0
                    }
                }
            }
        }
    }

# poetry run python src/app.py --ticker MSFT,AAPL
result2 = {
   "decisions":{
      "MSFT":{
         "action":"short",
         "quantity":41,
         "confidence":75.0,
         "reasoning":"Strong bearish signal with high confidence; opening a short position aligns with market sentiment."
      },
      "AAPL":{
         "action":"short",
         "quantity":101,
         "confidence":75.0,
         "reasoning":"Strong bearish signal with high confidence; opening a short position aligns with market sentiment."
      }
   },
   "analyst_signals":{
      "ben_graham_agent":{
         "MSFT":{
            "signal":"bearish",
            "confidence":75.0,
            "reasoning":"While MSFT shows solid current assets and a decent dividend history, its lack of EPS growth, high debt ratio, and a significant negative margin of safety based on the Graham Number indicate it is overvalued. Thus, it's prudent to avoid purchasing at current price levels."
         },
         "AAPL":{
            "signal":"bearish",
            "confidence":75.0,
            "reasoning":"AAPL is showing significant weaknesses in both valuation and financial strength. The margin of safety is severely negative at -89.16% based on the Graham Number, indicating that the stock is overvalued. Additionally, the current ratio of 1.11 suggests weaker liquidity and the debt ratio of 0.59 is somewhat high. With flat EPS growth and indicators pointing towards caution in terms of intrinsic value and safety, a bearish stance is warranted."
         }
      },
      "risk_management_agent":{
         "MSFT":{
            "remaining_position_limit":20000.0,
            "current_price":480.53,
            "reasoning":{
               "portfolio_value":100000.0,
               "current_position":0.0,
               "position_limit":20000.0,
               "remaining_limit":20000.0,
               "available_cash":100000.0
            }
         },
         "AAPL":{
            "remaining_position_limit":20000.0,
            "current_price":197.68,
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

# poetry run python src/app.py --ticker MSFT --show-reasoning
result3 = {
   "decisions":{
      "MSFT":{
         "action":"short",
         "quantity":41,
         "confidence":65.0,
         "reasoning":"The analysis indicates a bearish signal for MSFT with 65% confidence. Given that I currently have no positions in MSFT and there are no cash restrictions, I will short the maximum allowed shares to capitalize on the anticipated price decline."
      }
   },
   "analyst_signals":{
      "ben_graham_agent":{
         "MSFT":{
            "signal":"bearish",
            "confidence":65.0,
            "reasoning":"MSFT's valuation shows a significant lack of margin of safety with a Graham Number indicating the stock is highly overvalued at current prices. While the company has a solid current ratio and a stable dividend history, the overall earnings do not exhibit growth, and high debt levels could be a concern."
         }
      },
      "risk_management_agent":{
         "MSFT":{
            "remaining_position_limit":20000.0,
            "current_price":479.47,
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

# poetry run python src/app.py --ticker MSFT --start-date 2024-01-01 --end-date 2024-03-01

result4 = {
   "decisions":{
      "MSFT":{
         "action":"short",
         "quantity":48,
         "confidence":75.0,
         "reasoning":"The signal is bearish with high confidence (75%). I will short the maximum allowed shares since I currently have no positions in MSFT and the margin requirements are met."
      }
   },
   "analyst_signals":{
      "ben_graham_agent":{
         "MSFT":{
            "signal":"bearish",
            "confidence":75.0,
            "reasoning":"While MSFT shows solid financial strength with a favorable current ratio and low debt ratio, the lack of earnings growth and a very low margin of safety against the Graham Number indicate a high risk of overvaluation. The stock's price significantly exceeds its intrinsic value, suggesting potential downside risk."
         }
      },
      "risk_management_agent":{
         "MSFT":{
            "remaining_position_limit":20000.0,
            "current_price":415.5,
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


# 
result5= {
   "decisions":{
      "MSFT":{
         "action":"hold",
         "quantity":0,
         "confidence":0.0,
         "reasoning":"All agents provided a neutral signal with moderate confidence. No compelling reason to make a move."
      },
      "AAPL":{
         "action":"short",
         "quantity":100,
         "confidence":55.0,
         "reasoning":"Cathie Wood agent signaled a bearish outlook with a confidence of 55.0, while the other agents were neutral. Considering the combined cash and margin availability, taking a short position as a potential hedge or profit opportunity aligned with the bearish signal."
      }
   },
   "analyst_signals":{
      "bill_ackman_agent":{
         "MSFT":{
            "signal":"neutral",
            "confidence":40.0,
            "reasoning":"Microsoft (MSFT) exhibits strong indicators of business quality, including high operating margins and a substantial ROE of 36%, suggesting a potential competitive moat. However, the balance sheet analysis indicates a debt-to-equity ratio of 1.0 or higher, which merits caution from a financial discipline perspective. Additionally, the intrinsic value analysis shows a significant overvaluation with a negative margin of safety of -76.93%, indicating that the stock is trading far above its calculated intrinsic value. Given the premium at which Microsoft is currently trading compared to its intrinsic value, it is prudent to maintain a neutral stance as it does not align with the principle of buying at a discount. Consider observing for market corrections or potential strategic changes in management before making a more decisive move."
         },
         "AAPL":{
            "signal":"neutral",
            "confidence":50.0,
            "reasoning":"Apple exhibits strong qualitative features such as a high ROE of 137.9% and consistent historical free cash flows, which can indicate a durable competitive advantage (moat). However, its high debt-to-equity ratio raises concerns about financial leverage and does not signify strong financial discipline. The current market capitalization significantly exceeds the intrinsic value estimation, resulting in a negative margin of safety of -64.11%. Given these factors, although Apple is a high-quality business, the current valuation does not provide an adequate margin of safety for investment under Bill Ackman's principles."
         }
      },
      "ben_graham_agent":{
         "MSFT":{
            "signal":"neutral",
            "confidence":55.0,
            "reasoning":"MSFT exhibits strong financial stability with an impressive current ratio of 2.47 and a consistent dividend record, which is favorable under Graham's principles. However, the EPS stability did not reflect growth over time, and the valuation reflects a significant premium over the intrinsic value, as indicated by the negative margin of safety calculated using the Graham Number. The lack of margin of safety is a critical concern under Graham's principles, preventing a bullish recommendation. Thus, the position remains neutral with a moderate level of confidence in the company's financial strength and earnings stability, but caution is advised due to valuation concerns."
         },
         "AAPL":{
            "signal":"neutral",
            "confidence":50.0,
            "reasoning":"AAPL displays stable earnings with positive EPS over all periods, which aligns with Graham's emphasis on earnings stability. However, its current ratio of 1.11 indicates weaker liquidity, and a slightly high debt ratio at 0.59 could be a concern. Although AAPL pays dividends consistently, the valuation does not provide a margin of safety, as the price per share far exceeds the Graham Number, indicating the stock is not undervalued by Graham's standards. Without a margin of safety, a conservative Graham-style approach would not advocate buying. Therefore, a neutral stance is warranted."
         }
      },
      "cathie_wood_agent":{
         "MSFT":{
            "signal":"neutral",
            "confidence":60.0,
            "reasoning":"Microsoft shows a strong commitment to innovation with increasing R&D intensity and a solid operating margin, which aligns with Cathie Wood's focus on reinvestment for growth. However, its high market cap indicates it may be overvalued, with a significant negative margin of safety, suggesting limited immediate upside potential. The company's technological advancements position it well for disruptive innovation, aligning with long-term investment goals, but the current valuation implies a cautious approach."
         },
         "AAPL":{
            "signal":"bearish",
            "confidence":55.0,
            "reasoning":"Apple exhibits positive operating leverage and a good capacity to fund innovation through consistent positive free cash flow and a strong focus on reinvestment over dividends. However, its R&D investment remains moderate at 6.8% of revenue, which is below the typical threshold for significant disruptive innovation potential. Additionally, Apple's market cap exceeds its calculated intrinsic value by 22.43%, indicating a lack of margin of safety and suggesting the stock may be overvalued. Despite having a robust brand and operational efficiency, the current financial metrics and investment in R&D do not align with the disruptive growth potential necessary for a bullish outlook based on Cathie Wood's investment principles. Therefore, the investment signal for AAPL is bearish with moderate confidence."
         }
      },
      "risk_management_agent":{
         "MSFT":{
            "remaining_position_limit":20000.0,
            "current_price":479.91,
            "reasoning":{
               "portfolio_value":100000.0,
               "current_position":0.0,
               "position_limit":20000.0,
               "remaining_limit":20000.0,
               "available_cash":100000.0
            }
         },
         "AAPL":{
            "remaining_position_limit":20000.0,
            "current_price":198.1,
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

# poetry run python src/main.py --ticker AAPL,MSFT and choosing all available agents
result6= {
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

# poetry run python src/main.py --ticker AAPL --show-reasoning and chose all the agents
result7 = {
   "decisions":{
      "AAPL":{
         "action":"hold",
         "quantity":0,
         "confidence":0.0,
         "reasoning":"Mixed signals with a dominant bearish sentiment. No long position to initiate and insufficient bullish signals."
      },
      "MSFT":{
         "action":"hold",
         "quantity":0,
         "confidence":0.0,
         "reasoning":"Despite bullish sentiment from some agents, the majority signals/leads towards bearish outlook with no current positions to leverage."
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
                     "volume_momentum":0.004380630492591517
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
                     "z_score":1.0737766336559589,
                     "price_vs_bb":0.7383020826704817,
                     "rsi_14":71.74285714285713,
                     "rsi_28":68.23821339950373
                  }
               },
               "momentum":{
                  "signal":"neutral",
                  "confidence":50,
                  "metrics":{
                     "momentum_1m":0.05362047578527995,
                     "momentum_3m":"nan",
                     "momentum_6m":"nan",
                     "volume_momentum":0.0014730768253271576
                  }
               },
               "volatility":{
                  "signal":"neutral",
                  "confidence":50,
                  "metrics":{
                     "historical_volatility":0.12136970963438438,
                     "volatility_regime":"nan",
                     "volatility_z_score":"nan",
                     "atr_ratio":0.01103932844958433
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
      "cathie_wood_agent":{
         "AAPL":{
            "signal":"bearish",
            "confidence":65.0,
            "reasoning":"While AAPL showcases strong positive operating leverage and consistent free cash flow, the high market valuation compared to its intrinsic value indicates a lack of margin of safety. The leadership in innovation and R&D investment is notable, but the current valuation suggests downside risk, leading to a bearish signal."
         },
         "MSFT":{
            "signal":"neutral",
            "confidence":65.0,
            "reasoning":"Microsoft exhibits strong innovation potential with a healthy operating margin of 38.9% and a robust R&D investment representing 13.5% of revenue. This indicates a commitment to disruptive technologies and a solid financial footing for future growth. However, the negative margin of safety (-40.64%) suggests that the stock is overvalued at current market levels, which tempers the overall investment case, leading to a neutral outlook."
         }
      },
      "bill_ackman_agent":{
         "AAPL":{
            "signal":"bearish",
            "confidence":80.0,
            "reasoning":"While AAPL demonstrates a high return on equity (ROE) which suggests a potential moat, the overall financial health is concerning. The balance sheet shows a high debt-to-equity ratio with substantial debt levels and a lack of share buybacks. The valuation analysis highlights a significant negative margin of safety, indicating that AAPL is currently overvalued relative to its intrinsic value. Given these factors, the investment outlook is bearish despite some aspects of quality."
         },
         "MSFT":{
            "signal":"bearish",
            "confidence":80.0,
            "reasoning":"Both MSFT and AAPL show poor growth potential and significant negative margins of safety compared to their calculated intrinsic values, underscoring substantial overvaluation. High debt-to-equity ratios raise concerns regarding financial health. The limited free cash flow generation and lack of shareholder value improvements signal that both companies may face challenges in delivering future growth, warranting a bearish outlook."
         }
      },
      "charlie_munger_agent":{
         "AAPL":{
            "signal":"neutral",
            "confidence":65.0,
            "reasoning":"Apple exhibits strong predictability with consistent revenue growth and positive cash flows. Its competitive advantages are solid, indicated by high ROIC and pricing power. However, the valuation appears expensive, with a significant premium over reasonable value and a low FCF yield. The management team has a shareholder-friendly approach but carries a high debt level. Given these factors, I recommend a neutral stance, highlighting quality but cautioning against current valuation levels."
         },
         "MSFT":{
            "signal":"neutral",
            "confidence":65.0,
            "reasoning":"Microsoft (MSFT) displays strong fundamentals with excellent ROIC and predictable cash flows, but with high capital requirements and low FCF yield indicating overvaluation. While management shows good integrity and capital allocation, the significant premium to reasonable value suggests caution. The combination of these factors leads to a neutral stance on the investment at this time."
         }
      },
      "warren_buffett_agent":{
         "AAPL":{
            "signal":"bearish",
            "confidence":75.0,
            "reasoning":"AAPL has a significant negative margin of safety (-41.2%), indicating that the stock is overvalued compared to its intrinsic value. Additionally, the company's high debt-to-equity ratio (4.0) raises concerns about its financial strength. Furthermore, inconsistent earnings growth (total earnings growth of -3.1% over the past 5 periods) is not aligned with a long-term investment perspective. Therefore, based on Buffett's principles, this investment does not meet the necessary criteria."
         },
         "MSFT":{
            "signal":"bearish",
            "confidence":10.0,
            "reasoning":"Microsoft (MSFT) displays a margin of safety of only 1.34%, which is below the required threshold of 30% for investment. Although the company shows strong fundamentals with consistent earnings growth and a respectable return on equity, the current market valuation does not provide a sufficient margin of safety to justify an investment. A thin margin coupled with high price multiples indicates potential overvaluation, making it a risky buy under Buffett's investment principles."
         }
      },
      "ben_graham_agent":{
         "AAPL":{
            "signal":"bearish",
            "confidence":70.0,
            "reasoning":"AAPL shows weak valuation metrics with a Graham Number indicating significant margin of safety concerns (-88.53%). Additionally, the current ratio suggests weaker liquidity and while dividend history is positive, overall earnings stability is lacking as EPS has not grown over time. This combination raises red flags under Graham's investment principles."
         },
         "MSFT":{
            "signal":"neutral",
            "confidence":65.0,
            "reasoning":"While MSFT has solid earnings stability and a strong current ratio indicating good liquidity, the company exhibits a significant lack of margin of safety as the price is far above its Graham Number. Coupled with a somewhat high debt ratio and stagnant EPS growth, the investment is currently neutral."
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