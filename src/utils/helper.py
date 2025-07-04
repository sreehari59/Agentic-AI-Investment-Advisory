import pandas as pd
import numpy as np


def get_agent_name(agent_list):
    agent_mapper = {
         "Ben Graham" :  "ben_graham",
         "Bill Ackman" :  "bill_ackman",
         "Cathie Wood" :   "cathie_wood",
         "Charlie Munger" :  "charlie_munger",
         "Warren Buffett" :  "warren_buffett",
         "Technical Analyst" :  "technical_analyst",
         "Fundamentals Analyst" :  "fundamentals_analyst",
         "Sentiment Analyst" :  "sentiment_analyst",
         "Valuation Analyst" :  "valuation_analyst"
    }
    return [agent_mapper.get(agent) for agent in agent_list if agent in agent_mapper]


def agent_mapper(agent_name):
    agent_mapper = {
         "ben_graham_agent" : "Ben Graham",
         "bill_ackman_agent": "Bill Ackman",
         "cathie_wood_agent": "Cathie Wood",
         "charlie_munger_agent": "Charlie Munger",
         "warren_buffett_agent": "Warren Buffett",
         "technical_analyst_agent": "Technical Analyst",
         "fundamentals_agent": "Fundamentals Analyst",
         "sentiment_agent": "Sentiment Analyst",
         "valuation_agent": "Valuation Analyst"
    }
    return agent_mapper.get(agent_name, None)

def portfolio_summary_computation(df, start_date, end_date):
     # Make sure Date column is datetime
     df['Date'] = pd.to_datetime(df['Date'])

     # ----------- Filter the period ----------------------
     df_period = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()
     df_period = df_period.sort_values('Date').reset_index(drop=True)

     # Compute daily % changes
     df_period['Portfolio Daily % Change'] = df_period['Portfolio Value'].pct_change().fillna(0) * 100
     df_period['Buy and Hold Daily % Change'] = df_period['Buy and Hold Value'].pct_change().fillna(0) * 100

     # ----------- Calculate core metrics ------------------
     total_return = df_period['Portfolio Daily % Change'].iloc[1:].sum() 
     benchmark_return = df_period['Buy and Hold Daily % Change'].iloc[1:].sum()
     total_realized_gain = df_period['Portfolio Value'].iloc[-1] - df_period['Portfolio Value'].iloc[0]

     # ----------- Sharpe ratio (daily, rf=0) -------------
     daily_returns = df_period['Portfolio Daily % Change'].iloc[1:] / 100
     sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252) if daily_returns.std() != 0 else np.nan
     # ----------- Max drawdown ---------------------------
     cumulative_max = df_period['Portfolio Value'].cummax()
     drawdown_series = (df_period['Portfolio Value'] - cumulative_max) / cumulative_max
     max_drawdown = drawdown_series.min() * 100
     # ----------- Win rate and win/loss ratio ------------
     wins = (df_period['Portfolio Daily % Change'].iloc[1:] > 0).sum()
     losses = (df_period['Portfolio Daily % Change'].iloc[1:] < 0).sum()
     win_rate = wins / (len(df_period) - 1) * 100
     win_loss_ratio = wins / losses if losses != 0 else float('inf')
     # ----------- Max consecutive wins/losses ------------
     streaks = df_period['Portfolio Daily % Change'].iloc[1:].apply(lambda x: 1 if x > 0 else -1 if x < 0 else 0)
     max_consecutive_wins = max(
     map(len, ''.join(['W' if x == 1 else 'L' if x == -1 else 'N' for x in streaks]).split('L')),
     default=0
     )
     max_consecutive_losses = max(
     map(len, ''.join(['L' if x == -1 else 'W' if x == 1 else 'N' for x in streaks]).split('W')),
     default=0
     )
     # ----------- Output the results ---------------------
     metrics = {
          'total_return': round(total_return, 2),
          'benchmark_return': round(benchmark_return, 2),
          'total_realized_gains': round(total_realized_gain, 2),
          'sharpe_ratio': round(sharpe_ratio, 2),
          'max_drawdown': round(max_drawdown, 2),
          'win_rate': round(win_rate, 2),
          'win_loss_ratio': round(win_loss_ratio, 2),
          'max_consecutive_wins': max_consecutive_wins,
          'max_consecutive_losses': max_consecutive_losses,
     }
     return metrics