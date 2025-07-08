import sys

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph
from colorama import Fore, Back, Style, init
import questionary
from agents.ben_graham import ben_graham_agent
from agents.bill_ackman import bill_ackman_agent
from agents.fundamentals import fundamentals_agent
from agents.portfolio_manager import portfolio_management_agent
from agents.technicals import technical_analyst_agent
from agents.risk_manager import risk_management_agent
from agents.sentiment import sentiment_agent
from agents.warren_buffett import warren_buffett_agent
from graph.state import AgentState
from agents.valuation import valuation_agent
from utils.display import print_trading_output
from utils.analysts import ANALYST_ORDER, get_analyst_nodes
from utils.progress import progress
from llm.models import LLM_ORDER, get_model_info
from utils.db import get_agent_data, insert_into_sql_server,insert_trade_decision
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tabulate import tabulate
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing_extensions import Callable
from tools.api import (
    get_company_news,
    get_price_data,
    get_prices,
    get_financial_metrics,
    get_insider_trades,
)
from utils.display import print_backtest_results, format_backtest_row
from utils.helper import get_agent_name, agent_mapper, portfolio_summary_computation
import numpy as np
import itertools
import pyodbc
import os

# Load environment variables from .env file
load_dotenv()

init(autoreset=True)

app = Flask(__name__)
CORS(app)

def rows_to_dict_list(cursor):
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

class Backtester:
    def __init__(
        self,
        agent: Callable,
        tickers: list[str],
        start_date: str,
        end_date: str,
        initial_capital: float,
        model_name: str = "gpt-4o",
        model_provider: str = "OpenAI",
        selected_analysts: list[str] = [],
        initial_margin_requirement: float = 0.0,
    ):
        """
        :param agent: The trading agent (Callable).
        :param tickers: List of tickers to backtest.
        :param start_date: Start date string (YYYY-MM-DD).
        :param end_date: End date string (YYYY-MM-DD).
        :param initial_capital: Starting portfolio cash.
        :param model_name: Which LLM model name to use (gpt-4, etc).
        :param model_provider: Which LLM provider (OpenAI, etc).
        :param selected_analysts: List of analyst names or IDs to incorporate.
        :param initial_margin_requirement: The margin ratio (e.g. 0.5 = 50%).
        """
        self.agent = agent
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.model_name = model_name
        self.model_provider = model_provider
        self.selected_analysts = selected_analysts

        # Store the margin ratio (e.g. 0.5 means 50% margin required).
        self.margin_ratio = initial_margin_requirement

        # Initialize portfolio with support for long/short positions
        self.portfolio_values = []
        self.portfolio = {
            "cash": initial_capital,
            "margin_used": 0.0,  # total margin usage across all short positions
            "positions": {
                ticker: {
                    "long": 0,               # Number of shares held long
                    "short": 0,              # Number of shares held short
                    "long_cost_basis": 0.0,  # Average cost basis per share (long)
                    "short_cost_basis": 0.0, # Average cost basis per share (short)
                    "short_margin_used": 0.0 # Dollars of margin used for this ticker's short
                } for ticker in tickers
            },
            "realized_gains": {
                ticker: {
                    "long": 0.0,   # Realized gains from long positions
                    "short": 0.0,  # Realized gains from short positions
                } for ticker in tickers
            }
        }

    def execute_trade(self, ticker: str, action: str, quantity: float, current_price: float):
        """
        Execute trades with support for both long and short positions.
        `quantity` is the number of shares the agent wants to buy/sell/short/cover.
        We will only trade integer shares to keep it simple.
        """
        if quantity <= 0:
            return 0

        quantity = int(quantity)  # force integer shares
        position = self.portfolio["positions"][ticker]

        if action == "buy":
            cost = quantity * current_price
            if cost <= self.portfolio["cash"]:
                # Weighted average cost basis for the new total
                old_shares = position["long"]
                old_cost_basis = position["long_cost_basis"]
                new_shares = quantity
                total_shares = old_shares + new_shares

                if total_shares > 0:
                    total_old_cost = old_cost_basis * old_shares
                    total_new_cost = cost
                    position["long_cost_basis"] = (total_old_cost + total_new_cost) / total_shares

                position["long"] += quantity
                self.portfolio["cash"] -= cost
                return quantity
            else:
                # Calculate maximum affordable quantity
                max_quantity = int(self.portfolio["cash"] / current_price)
                if max_quantity > 0:
                    cost = max_quantity * current_price
                    old_shares = position["long"]
                    old_cost_basis = position["long_cost_basis"]
                    total_shares = old_shares + max_quantity

                    if total_shares > 0:
                        total_old_cost = old_cost_basis * old_shares
                        total_new_cost = cost
                        position["long_cost_basis"] = (total_old_cost + total_new_cost) / total_shares

                    position["long"] += max_quantity
                    self.portfolio["cash"] -= cost
                    return max_quantity
                return 0

        elif action == "sell":
            # You can only sell as many as you own
            quantity = min(quantity, position["long"])
            if quantity > 0:
                # Realized gain/loss using average cost basis
                avg_cost_per_share = position["long_cost_basis"] if position["long"] > 0 else 0
                realized_gain = (current_price - avg_cost_per_share) * quantity
                self.portfolio["realized_gains"][ticker]["long"] += realized_gain

                position["long"] -= quantity
                self.portfolio["cash"] += quantity * current_price

                if position["long"] == 0:
                    position["long_cost_basis"] = 0.0

                return quantity

        elif action == "short":
            """
            Typical short sale flow:
              1) Receive proceeds = current_price * quantity
              2) Post margin_required = proceeds * margin_ratio
              3) Net effect on cash = +proceeds - margin_required
            """
            proceeds = current_price * quantity
            margin_required = proceeds * self.margin_ratio
            if margin_required <= self.portfolio["cash"]:
                # Weighted average short cost basis
                old_short_shares = position["short"]
                old_cost_basis = position["short_cost_basis"]
                new_shares = quantity
                total_shares = old_short_shares + new_shares

                if total_shares > 0:
                    total_old_cost = old_cost_basis * old_short_shares
                    total_new_cost = current_price * new_shares
                    position["short_cost_basis"] = (total_old_cost + total_new_cost) / total_shares

                position["short"] += quantity

                # Update margin usage
                position["short_margin_used"] += margin_required
                self.portfolio["margin_used"] += margin_required

                # Increase cash by proceeds, then subtract the required margin
                self.portfolio["cash"] += proceeds
                self.portfolio["cash"] -= margin_required
                return quantity
            else:
                # Calculate maximum shortable quantity
                if self.margin_ratio > 0:
                    max_quantity = int(self.portfolio["cash"] / (current_price * self.margin_ratio))
                else:
                    max_quantity = 0

                if max_quantity > 0:
                    proceeds = current_price * max_quantity
                    margin_required = proceeds * self.margin_ratio

                    old_short_shares = position["short"]
                    old_cost_basis = position["short_cost_basis"]
                    total_shares = old_short_shares + max_quantity

                    if total_shares > 0:
                        total_old_cost = old_cost_basis * old_short_shares
                        total_new_cost = current_price * max_quantity
                        position["short_cost_basis"] = (total_old_cost + total_new_cost) / total_shares

                    position["short"] += max_quantity
                    position["short_margin_used"] += margin_required
                    self.portfolio["margin_used"] += margin_required

                    self.portfolio["cash"] += proceeds
                    self.portfolio["cash"] -= margin_required
                    return max_quantity
                return 0

        elif action == "cover":
            """
            When covering shares:
              1) Pay cover cost = current_price * quantity
              2) Release a proportional share of the margin
              3) Net effect on cash = -cover_cost + released_margin
            """
            quantity = min(quantity, position["short"])
            if quantity > 0:
                cover_cost = quantity * current_price
                avg_short_price = position["short_cost_basis"] if position["short"] > 0 else 0
                realized_gain = (avg_short_price - current_price) * quantity

                if position["short"] > 0:
                    portion = quantity / position["short"]
                else:
                    portion = 1.0

                margin_to_release = portion * position["short_margin_used"]

                position["short"] -= quantity
                position["short_margin_used"] -= margin_to_release
                self.portfolio["margin_used"] -= margin_to_release

                # Pay the cost to cover, but get back the released margin
                self.portfolio["cash"] += margin_to_release
                self.portfolio["cash"] -= cover_cost

                self.portfolio["realized_gains"][ticker]["short"] += realized_gain

                if position["short"] == 0:
                    position["short_cost_basis"] = 0.0
                    position["short_margin_used"] = 0.0

                return quantity

        return 0

    def calculate_portfolio_value(self, current_prices):
        """
        Calculate total portfolio value, including:
          - cash
          - market value of long positions
          - unrealized gains/losses for short positions
        """
        total_value = self.portfolio["cash"]

        for ticker in self.tickers:
            position = self.portfolio["positions"][ticker]
            price = current_prices[ticker]

            # Long position value
            long_value = position["long"] * price
            total_value += long_value

            # Short position unrealized PnL = short_shares * (short_cost_basis - current_price)
            if position["short"] > 0:
                total_value += position["short"] * (position["short_cost_basis"] - price)

        return total_value

    def prefetch_data(self):
        """Pre-fetch all data needed for the backtest period."""
        print("\nPre-fetching data for the entire backtest period...")

        # Convert end_date string to datetime, fetch up to 1 year before
        end_date_dt = datetime.strptime(self.end_date, "%Y-%m-%d")
        start_date_dt = end_date_dt - relativedelta(years=1)
        start_date_str = start_date_dt.strftime("%Y-%m-%d")

        for ticker in self.tickers:
            # Fetch price data for the entire period, plus 1 year
            get_prices(ticker, start_date_str, self.end_date)

            # Fetch financial metrics
            get_financial_metrics(ticker, self.end_date, limit=10)

            # Fetch insider trades
            get_insider_trades(ticker, self.end_date, start_date=self.start_date, limit=1000)

            # Fetch company news
            get_company_news(ticker, self.end_date, start_date=self.start_date, limit=1000)

        print("Data pre-fetch complete.")

    def parse_agent_response(self, agent_output):
        """Parse JSON output from the agent (fallback to 'hold' if invalid)."""
        import json

        try:
            decision = json.loads(agent_output)
            return decision
        except Exception:
            print(f"Error parsing action: {agent_output}")
            return {"action": "hold", "quantity": 0}

    def run_backtest(self):
        # Pre-fetch all data at the start
        self.prefetch_data()

        dates = pd.date_range(self.start_date, self.end_date, freq="B")
        table_rows = []
        new_table_rows = []
        performance_metrics = {
            'sharpe_ratio': None,
            'sortino_ratio': None,
            'max_drawdown': None,
            'long_short_ratio': None,
            'gross_exposure': None,
            'net_exposure': None
        }

        print("\nStarting backtest...")

        # Initialize portfolio values list with initial capital
        if len(dates) > 0:
            self.portfolio_values = [{"Date": dates[0], "Portfolio Value": self.initial_capital}]
        else:
            self.portfolio_values = []

        for current_date in dates:
            lookback_start = (current_date - timedelta(days=30)).strftime("%Y-%m-%d")
            current_date_str = current_date.strftime("%Y-%m-%d")
            previous_date_str = (current_date - timedelta(days=1)).strftime("%Y-%m-%d")

            # Skip if there's no prior day to look back (i.e., first date in the range)
            if lookback_start == current_date_str:
                continue

            # Get current prices for all tickers
            try:
                current_prices = {
                    ticker: get_price_data(ticker, previous_date_str, current_date_str).iloc[-1]["close"]
                    for ticker in self.tickers
                }
            except Exception:
                # If data is missing or there's an API error, skip this day
                print(f"Error fetching prices between {previous_date_str} and {current_date_str}")
                continue

            # ---------------------------------------------------------------
            # 1) Execute the agent's trades
            # ---------------------------------------------------------------
            output = self.agent(
                tickers=self.tickers,
                start_date=lookback_start,
                end_date=current_date_str,
                portfolio=self.portfolio,
                model_name=self.model_name,
                model_provider=self.model_provider,
                selected_analysts=self.selected_analysts,
            )
            decisions = output["decisions"]
            analyst_signals = output["analyst_signals"]

            # Execute trades for each ticker
            executed_trades = {}
            for ticker in self.tickers:
                decision = decisions.get(ticker, {"action": "hold", "quantity": 0})
                action, quantity = decision.get("action", "hold"), decision.get("quantity", 0)

                executed_quantity = self.execute_trade(ticker, action, quantity, current_prices[ticker])
                executed_trades[ticker] = executed_quantity

            # ---------------------------------------------------------------
            # 2) Now that trades have executed trades, recalculate the final
            #    portfolio value for this day.
            # ---------------------------------------------------------------
            total_value = self.calculate_portfolio_value(current_prices)

            # Also compute long/short exposures for final post‐trade state
            long_exposure = sum(
                self.portfolio["positions"][t]["long"] * current_prices[t]
                for t in self.tickers
            )
            short_exposure = sum(
                self.portfolio["positions"][t]["short"] * current_prices[t]
                for t in self.tickers
            )

            # Calculate gross and net exposures
            gross_exposure = long_exposure + short_exposure
            net_exposure = long_exposure - short_exposure
            long_short_ratio = (
                long_exposure / short_exposure if short_exposure > 1e-9 else float('inf')
            )

            # Track each day's portfolio value in self.portfolio_values
            self.portfolio_values.append({
                "Date": current_date,
                "Portfolio Value": total_value,
                "Long Exposure": long_exposure,
                "Short Exposure": short_exposure,
                "Gross Exposure": gross_exposure,
                "Net Exposure": net_exposure,
                "Long/Short Ratio": long_short_ratio
            })

            # ---------------------------------------------------------------
            # 3) Build the table rows to display
            # ---------------------------------------------------------------
            date_rows = []
            new_date_rows = []
            # For each ticker, record signals/trades
            for ticker in self.tickers:
                ticker_signals = {}
                for agent_name, signals in analyst_signals.items():
                    if ticker in signals:
                        ticker_signals[agent_name] = signals[ticker]

                bullish_count = len([s for s in ticker_signals.values() if s.get("signal", "").lower() == "bullish"])
                bearish_count = len([s for s in ticker_signals.values() if s.get("signal", "").lower() == "bearish"])
                neutral_count = len([s for s in ticker_signals.values() if s.get("signal", "").lower() == "neutral"])

                # Calculate net position value
                pos = self.portfolio["positions"][ticker]
                long_val = pos["long"] * current_prices[ticker]
                short_val = pos["short"] * current_prices[ticker]
                net_position_value = long_val - short_val

                # Get the action and quantity from the decisions
                action = decisions.get(ticker, {}).get("action", "hold")
                quantity = executed_trades.get(ticker, 0)
                
                # Append the agent action to the table rows
                date_rows.append(
                    format_backtest_row(
                        date=current_date_str,
                        ticker=ticker,
                        action=action,
                        quantity=quantity,
                        price=current_prices[ticker],
                        shares_owned=pos["long"] - pos["short"],  # net shares
                        position_value=net_position_value,
                        bullish_count=bullish_count,
                        bearish_count=bearish_count,
                        neutral_count=neutral_count,
                    )
                )
                # print(current_prices)
                # print(current_prices[ticker])
                # initial_price = current_prices[ticker][0]
                # price_return = (current_prices[ticker] - initial_price)/initial_price
                # buy_hold = self.initial_capital * (1 + price_return)

                new_date_rows.append(
                    (
                        current_date_str,
                        ticker,
                        action,
                        quantity,
                        current_prices[ticker],
                        pos["long"] - pos["short"],  # net shares
                        net_position_value,
                        bullish_count,
                        bearish_count,
                        neutral_count
                    )
                )
            # ---------------------------------------------------------------
            # 4) Calculate performance summary metrics
            # ---------------------------------------------------------------
            total_realized_gains = sum(
                self.portfolio["realized_gains"][t]["long"] +
                self.portfolio["realized_gains"][t]["short"]
                for t in self.tickers
            )

            # Calculate cumulative return vs. initial capital
            portfolio_return = ((total_value + total_realized_gains) / self.initial_capital - 1) * 100

            # Add summary row for this day
            date_rows.append(
                format_backtest_row(
                    date=current_date_str,
                    ticker="",
                    action="",
                    quantity=0,
                    price=0,
                    shares_owned=0,
                    position_value=0,
                    bullish_count=0,
                    bearish_count=0,
                    neutral_count=0,
                    is_summary=True,
                    total_value=total_value,
                    return_pct=portfolio_return,
                    cash_balance=self.portfolio["cash"],
                    total_position_value=total_value - self.portfolio["cash"],
                    sharpe_ratio=performance_metrics["sharpe_ratio"],
                    sortino_ratio=performance_metrics["sortino_ratio"],
                    max_drawdown=performance_metrics["max_drawdown"],
                ),
            )


            table_rows.extend(date_rows)
            new_table_rows.extend(new_date_rows)
            # print("date_rows length",len(date_rows))
            # print("new_date_rows length",len(new_date_rows))
            print_backtest_results(table_rows)

            # Update performance metrics if we have enough data
            if len(self.portfolio_values) > 3:
                self._update_performance_metrics(performance_metrics) 

        return performance_metrics, table_rows, new_table_rows

    def _update_performance_metrics(self, performance_metrics):
        """Helper method to update performance metrics using daily returns."""
        values_df = pd.DataFrame(self.portfolio_values).set_index("Date")
        values_df["Daily Return"] = values_df["Portfolio Value"].pct_change()
        clean_returns = values_df["Daily Return"].dropna()

        if len(clean_returns) < 2:
            return  # not enough data points

        # Assumes 252 trading days/year
        daily_risk_free_rate = 0.0434 / 252
        excess_returns = clean_returns - daily_risk_free_rate
        mean_excess_return = excess_returns.mean()
        std_excess_return = excess_returns.std()

        # Sharpe ratio
        if std_excess_return > 1e-12:
            performance_metrics["sharpe_ratio"] = np.sqrt(252) * (mean_excess_return / std_excess_return)
        else:
            performance_metrics["sharpe_ratio"] = 0.0

        # Sortino ratio
        negative_returns = excess_returns[excess_returns < 0]
        if len(negative_returns) > 0:
            downside_std = negative_returns.std()
            if downside_std > 1e-12:
                performance_metrics["sortino_ratio"] = np.sqrt(252) * (mean_excess_return / downside_std)
            else:
                performance_metrics["sortino_ratio"] = float('inf') if mean_excess_return > 0 else 0
        else:
            performance_metrics["sortino_ratio"] = float('inf') if mean_excess_return > 0 else 0

        # Maximum drawdown
        rolling_max = values_df["Portfolio Value"].cummax()
        drawdown = (values_df["Portfolio Value"] - rolling_max) / rolling_max
        performance_metrics["max_drawdown"] = drawdown.min() * 100

    def analyze_performance(self):
        """Creates a performance DataFrame, prints summary stats, and plots equity curve."""
        if not self.portfolio_values:
            print("No portfolio data found. Please run the backtest first.")
            return pd.DataFrame()

        performance_df = pd.DataFrame(self.portfolio_values).set_index("Date")
        if performance_df.empty:
            print("No valid performance data to analyze.")
            return performance_df

        final_portfolio_value = performance_df["Portfolio Value"].iloc[-1]
        total_realized_gains = sum(
            self.portfolio["realized_gains"][ticker]["long"] for ticker in self.tickers
        )
        total_return = ((final_portfolio_value - self.initial_capital) / self.initial_capital) * 100
        
        print(f"\n{Fore.WHITE}{Style.BRIGHT}PORTFOLIO PERFORMANCE SUMMARY:{Style.RESET_ALL}")
        print(f"Total Return: {Fore.GREEN if total_return >= 0 else Fore.RED}{total_return:.2f}%{Style.RESET_ALL}")
        print(f"Total Realized Gains/Losses: {Fore.GREEN if total_realized_gains >= 0 else Fore.RED}${total_realized_gains:,.2f}{Style.RESET_ALL}")

        # Compute daily returns
        performance_df["Daily Return"] = performance_df["Portfolio Value"].pct_change().fillna(0)
        daily_rf = 0.0434 / 252  # daily risk-free rate
        mean_daily_return = performance_df["Daily Return"].mean()
        std_daily_return = performance_df["Daily Return"].std()

        # Annualized Sharpe Ratio
        if std_daily_return != 0:
            annualized_sharpe = np.sqrt(252) * ((mean_daily_return - daily_rf) / std_daily_return)
        else:
            annualized_sharpe = 0
        print(f"\nSharpe Ratio: {Fore.YELLOW}{annualized_sharpe:.2f}{Style.RESET_ALL}")

        # Max Drawdown
        rolling_max = performance_df["Portfolio Value"].cummax()
        drawdown = (performance_df["Portfolio Value"] - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        max_drawdown_date = drawdown.idxmin()
        if pd.notnull(max_drawdown_date):
            print(f"Maximum Drawdown: {Fore.RED}{max_drawdown * 100:.2f}%{Style.RESET_ALL} (on {max_drawdown_date.strftime('%Y-%m-%d')})")
        else:
            print(f"Maximum Drawdown: {Fore.RED}0.00%{Style.RESET_ALL}")
        
        # Win Rate
        winning_days = len(performance_df[performance_df["Daily Return"] > 0])
        total_days = max(len(performance_df) - 1, 1)
        win_rate = (winning_days / total_days) * 100
        print(f"Win Rate: {Fore.GREEN}{win_rate:.2f}%{Style.RESET_ALL}")

        # Average Win/Loss Ratio
        positive_returns = performance_df[performance_df["Daily Return"] > 0]["Daily Return"]
        negative_returns = performance_df[performance_df["Daily Return"] < 0]["Daily Return"]
        avg_win = positive_returns.mean() if not positive_returns.empty else 0
        avg_loss = abs(negative_returns.mean()) if not negative_returns.empty else 0
        if avg_loss != 0:
            win_loss_ratio = avg_win / avg_loss
        else:
            win_loss_ratio = float('inf') if avg_win > 0 else 0
        print(f"Win/Loss Ratio: {Fore.GREEN}{win_loss_ratio:.2f}{Style.RESET_ALL}")
        
        # Maximum Consecutive Wins / Losses
        returns_binary = (performance_df["Daily Return"] > 0).astype(int)
        if len(returns_binary) > 0:
            max_consecutive_wins = max((len(list(g)) for k, g in itertools.groupby(returns_binary) if k == 1), default=0)
            max_consecutive_losses = max((len(list(g)) for k, g in itertools.groupby(returns_binary) if k == 0), default=0)
        else:
            max_consecutive_wins = 0
            max_consecutive_losses = 0

        print(f"Max Consecutive Wins: {Fore.GREEN}{max_consecutive_wins}{Style.RESET_ALL}")
        print(f"Max Consecutive Losses: {Fore.RED}{max_consecutive_losses}{Style.RESET_ALL}")

        portfolio_summary = (
            str(total_return),
            str(total_realized_gains),
            str(annualized_sharpe),
            str(max_drawdown),
            str(win_rate),
            str(win_loss_ratio),
            max_consecutive_wins,
            max_consecutive_losses
        )

        return performance_df, portfolio_summary


def parse_hedge_fund_response(response):
    """Parses a JSON string and returns a dictionary."""
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}\nResponse: {repr(response)}")
        return None
    except TypeError as e:
        print(f"Invalid response type (expected string, got {type(response).__name__}): {e}")
        return None
    except Exception as e:
        print(f"Unexpected error while parsing response: {e}\nResponse: {repr(response)}")
        return None



##### Run the Hedge Fund #####
def run_hedge_fund(
    tickers: list[str],
    start_date: str,
    end_date: str,
    portfolio: dict,
    show_reasoning: bool = False,
    selected_analysts: list[str] = [],
    model_name: str = "gpt-4o",
    model_provider: str = "OpenAI",
):
    # Start progress tracking
    progress.start()

    try:
        # Create a new workflow if analysts are customized
        if selected_analysts:
            workflow = create_workflow(selected_analysts)
            agent = workflow.compile()
        else:
            agent = app

        final_state = agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content="Make trading decisions based on the provided data.",
                    )
                ],
                "data": {
                    "tickers": tickers,
                    "portfolio": portfolio,
                    "start_date": start_date,
                    "end_date": end_date,
                    "analyst_signals": {},
                },
                "metadata": {
                    "show_reasoning": show_reasoning,
                    "model_name": model_name,
                    "model_provider": model_provider,
                },
            },
        )

        return {
            "decisions": parse_hedge_fund_response(final_state["messages"][-1].content),
            "analyst_signals": final_state["data"]["analyst_signals"],
        }
    finally:
        # Stop progress tracking
        progress.stop()


def start(state: AgentState):
    """Initialize the workflow with the input message."""
    return state


def create_workflow(selected_analysts=None):
    """Create the workflow with selected analysts."""
    workflow = StateGraph(AgentState)
    workflow.add_node("start_node", start)

    # Get analyst nodes from the configuration
    analyst_nodes = get_analyst_nodes()

    # Default to all analysts if none selected
    if selected_analysts is None:
        selected_analysts = list(analyst_nodes.keys())
    # Add selected analyst nodes
    for analyst_key in selected_analysts:
        node_name, node_func = analyst_nodes[analyst_key]
        workflow.add_node(node_name, node_func)
        workflow.add_edge("start_node", node_name)

    # Always add risk and portfolio management
    workflow.add_node("risk_management_agent", risk_management_agent)
    workflow.add_node("portfolio_management_agent", portfolio_management_agent)

    # Connect selected analysts to risk management
    for analyst_key in selected_analysts:
        node_name = analyst_nodes[analyst_key][0]
        workflow.add_edge(node_name, "risk_management_agent")

    workflow.add_edge("risk_management_agent", "portfolio_management_agent")
    workflow.add_edge("portfolio_management_agent", END)

    workflow.set_entry_point("start_node")
    return workflow


@app.route('/ai_hedge_fund_back_test_realtime', methods=['POST'])
def ai_hedge_fund_back_test_real_time():
    data = request.get_json()
    tickers = data.get('tickers')
    selected_analysts = get_agent_name(data.get('analysts'))    
    model_choice = data.get('model_choice', 'gpt-4o-mini')
    user_start_date = data.get('start_date', '2024-01-01')
    user_end_date = data.get('end_date', '2024-09-01')

    user_inital_capital = 100000
    user_margin_requirement = 0.0
    model_info = get_model_info(model_choice)
    if model_info:
        model_provider = model_info.provider.value

    # Create and run the backtester
    backtester = Backtester(
        agent=run_hedge_fund,
        tickers=tickers,
        start_date=user_start_date,
        end_date=user_end_date,
        initial_capital=user_inital_capital,
        model_name=model_choice,
        model_provider=model_provider,
        selected_analysts=selected_analysts,
        initial_margin_requirement=user_margin_requirement,
    )

    performance_metrics, table_data, new_table_rows = backtester.run_backtest()
    performance_df, portfolio_summary = backtester.analyze_performance()

    cash = user_inital_capital
    inital_cash = user_inital_capital
    cash_list = []

    prefix = "PID_" 
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    portfolio_reference_id = prefix + timestamp


    df = pd.DataFrame(new_table_rows, columns =['Date', 'Ticker', 'Action', 'Quantity', 'Price', 'Shares', 'Position Value',
                                    'Bullish', 'Bearish', 'Neutral'])

    df['Portfolio_id'] = portfolio_reference_id
    for row in df.itertuples():
        action = row.Action.lower()
        qty = row.Quantity
        price = row.Price
        if action == 'buy':
            cash -= qty * price
        elif action == 'sell':
            cash += qty * price
        elif action == 'short':
            cash += qty * price
        elif action == 'cover':
            cash -= qty * price
        cash_list.append(cash)

    df['Cash'] = cash_list
    df['Portfolio Value'] = df['Cash'] + df['Position Value']
    df['Return total P&L'] = df['Portfolio Value'] - inital_cash
    df['Return %'] = (df['Return total P&L'] / inital_cash) * 100

    non_zero_shares = df.loc[df['Shares'] != 0, 'Price']
    if not non_zero_shares.empty:
        initial_price = non_zero_shares.iloc[0]
        shares_bh = inital_cash / initial_price
        df["Buy and Hold Value"] = shares_bh * df['Price']

    else:
        initial_price = None
        df["Buy and Hold Value"] = 0
    
    updated_data = list(df.itertuples(index=False, name=None))

    backtest_dict = df.to_dict(orient='records')
    back_test_plot_data = {"Date": df['Date'].tolist(),
                      "Portfolio Value": df['Portfolio Value'].tolist(),
                      "buy_hold_value": df['Buy and Hold Value'].tolist()}
    try:
        backtest_data_query = """INSERT INTO backtest (trade_date, ticker, trade_action, quantity, 
                                    price, shares, position_value, bullish,
                                    bearish, neutral, portfolio_id, cash, portfolio_value, return_total_PL,
                                    return_percentage, buy_hold_value)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        # insert_into_sql_server(backtest_data_query , updated_data)


        updated_portfolio_summary = [portfolio_summary + (portfolio_reference_id,)]
        portfolio_summary_data_query = """INSERT INTO backtest_portfolio_summary (total_return, total_realized_gains, sharpe_ratio, 
                                    max_drawdown, win_rate, win_loss_ratio, max_consecutive_wins, 
                                    max_consecutive_losses, portfolio_id)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        # insert_into_sql_server(portfolio_summary_data_query , updated_portfolio_summary)

    except Exception as e:
        print(f"Error inserting data into SQL Server: {e}")

    backtest_result = {
        "backtest_data": backtest_dict,
        "portfolio_summary": {
            "total_return": portfolio_summary[0],
            "total_realized_gains": portfolio_summary[1],
            "sharpe_ratio": portfolio_summary[2],
            "max_drawdown": portfolio_summary[3],
            "win_rate": portfolio_summary[4],
            "win_loss_ratio": portfolio_summary[5],
            "max_consecutive_wins": portfolio_summary[6],
            "max_consecutive_losses": portfolio_summary[7]
        },
        "back_test_plot": back_test_plot_data
    }
    return  jsonify(backtest_result), 200

@app.route('/ai_hedge_fund', methods=['POST'])
def ai_hedge_fund():
    data = request.get_json()
    tickers = data.get('tickers')
    selected_analysts = get_agent_name(data.get('analysts'))  
    print("ticker_name:", tickers)
    model_choice = data.get('model_choice', 'gpt-4o-mini')
    timestamp_today = str(datetime.now().strftime("%Y-%m-%d"))
    timestamp_yesterday = str((datetime.now() - pd.Timedelta(days=1)).strftime("%Y-%m-%d"))
    timestamp_day_before_yesterday = str((datetime.now() - pd.Timedelta(days=2)).strftime("%Y-%m-%d"))
    model_choice = "gpt-4o-mini"

    print("tickers:", tickers)
    print("selected_analysts:", selected_analysts)
    print("model_choice:", model_choice)
    model_info = get_model_info(model_choice)
    if model_info:
        model_provider = model_info.provider.value

    # Create the workflow with selected analysts
    workflow = create_workflow(selected_analysts)
    app = workflow.compile()

    # Initialize portfolio with cash amount and stock positions
    portfolio = {
        "cash": 100000.0,  # Initial cash amount
        "margin_requirement": 0.0,  # Initial margin requirement
        "positions": {
            ticker: {
                "long": 0,  # Number of shares held long
                "short": 0,  # Number of shares held short
                "long_cost_basis": 0.0,  # Average cost basis for long positions
                "short_cost_basis": 0.0,  # Average price at which shares were sold short
            } for ticker in tickers
        },
        "realized_gains": {
            ticker: {
                "long": 0.0,  # Realized gains from long positions
                "short": 0.0,  # Realized gains from short positions
            } for ticker in tickers
        }
    }

    # Run the hedge fund
    result = run_hedge_fund(
        tickers=tickers,
        start_date=timestamp_yesterday,
        end_date=timestamp_today,
        portfolio=portfolio,
        show_reasoning=False,
        selected_analysts=selected_analysts,
        model_name=model_choice,
        model_provider=model_provider,
    )

    print("tickers:", tickers)
    print("selected_analysts:", selected_analysts)
    print("model_choice:", model_choice)


    prefix = "GD_" 
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    group_decision_id = prefix + timestamp
    trade_decision = {}
    for ticker_val in tickers:
        final_output = []
        updated_final_output = []
        for analyst in selected_analysts:
            final_output.append(get_agent_data(result, analyst, ticker_val, group_decision_id, model_choice))
        
        agent_data_query = """INSERT INTO AgentTradeInfo (ticker, analyst_name, signal, analyst_confidence, 
                                llm_name, execution_date, group_decision_id, agent_signals, agent_reasoning,
                                analysis_summary)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        # insert_into_sql_server(agent_data_query , final_output)
        # insert_trade_decision(result, ticker_val, group_decision_id)

        trade_decision_confidence = int(result["decisions"][ticker_val]["confidence"])
        trade_decision_quantity = result["decisions"][ticker_val]["quantity"]
        trade_decision_action = result["decisions"][ticker_val]["action"]
        trade_decision_reasoning = result["decisions"][ticker_val]["reasoning"]

        for index in range(len(final_output)):
            updated_final_output.append({
                "ticker" : final_output[index][0],
                "analyst_name" : agent_mapper(final_output[index][1]),
                "signal" : final_output[index][2],
                "analyst_confidence" :final_output[index][3],
                "llm_name" : final_output[index][4],
                "execution_date" : final_output[index][5],
                "group_decision_id" : final_output[index][6],
                "agent_signals" : final_output[index][7],
                "agent_reasoning" : final_output[index][8],
                "analysis_summary" : final_output[index][9]
            })
        trade_decision[ticker_val] = {
            "confidence": trade_decision_confidence,
            "quantity": trade_decision_quantity,
            "action": trade_decision_action,
            "reasoning": trade_decision_reasoning,
            "agent_advice": updated_final_output
        }

    print("trade_decision:", trade_decision)
    
    return jsonify(trade_decision), 200

@app.route('/get_ai_agents', methods=['GET'])
def get_ai_agents():
    db_server = os.getenv('DB_SERVER')
    db_name = os.getenv('DB_NAME')
    db_username = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT')
    db_driver = os.getenv('DRIVER')
    agent_details = {}
    try:
        with pyodbc.connect('DRIVER='+db_driver+';SERVER=tcp:'+db_server+';PORT='+db_port+';DATABASE='+db_name+';UID='+db_username+';PWD='+ db_password) as conn:
            with conn.cursor() as cursor:
                agent_summary_query = "SELECT * FROM InvestmentAgents;"
                cursor.execute(agent_summary_query)
                agent_details["investment_agent_summary"] = rows_to_dict_list(cursor)


                agent_performance_query = """select total_return as performance, sharpe_ratio, win_rate, 
                                            agent_name from agent_performance"""
                cursor.execute(agent_performance_query)
                agent_details["investment_agent_performance"] = rows_to_dict_list(cursor)

                agent_total_trades = """SELECT 
                                        a.agent_name,
                                        COUNT(b.trade_action) AS total_trades
                                    FROM 
                                        (SELECT DISTINCT agent_name FROM agent_backtest) a
                                    LEFT JOIN 
                                        agent_backtest b
                                        ON a.agent_name = b.agent_name AND LOWER(b.trade_action) <> 'hold'
                                    GROUP BY a.agent_name;"""
                cursor.execute(agent_total_trades)
                agent_details["agent_total_trades"] = rows_to_dict_list(cursor)

    except Exception as e:
        print("Error while reading data from SQL Server:", e)
        return {"error": str(e)}, 500
    
    return  jsonify(agent_details), 200

@app.route('/agent_strategy', methods=['POST'])
def agent_strategy():
    data = request.get_json()
    analyst_name = get_agent_name(data.get('analysts'))[0]
    print(analyst_name)
    db_server = os.getenv('DB_SERVER')
    db_name = os.getenv('DB_NAME')
    db_username = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT')
    db_driver = os.getenv('DRIVER')
    agent_data={}
    try:
        with pyodbc.connect('DRIVER='+db_driver+';SERVER=tcp:'+db_server+';PORT='+db_port+';DATABASE='+db_name+';UID='+db_username+';PWD='+ db_password) as conn:
            with conn.cursor() as cursor:
                agent_performance_query = """select trade_date, portfolio_value, buy_hold_value from agent_backtest 
                                            where agent_name = ?;"""
                cursor.execute(agent_performance_query, (analyst_name,))
                agent_data["agent_performance"] = rows_to_dict_list(cursor)


                agent_signal_query = """select sum(bullish) as bullish_signal,
                                        sum(bearish) as bearish_signal, sum(neutral) as neutral_signal 
                                        from agent_backtest where agent_name = ?;"""
                
                cursor.execute(agent_signal_query, (analyst_name,))
                agent_data["agent_signals"] = rows_to_dict_list(cursor)

                portfolio_value_start_date_query = """
                                                    select top 1 portfolio_value, trade_date from agent_backtest 
                                                    where agent_name = ? order by trade_date asc"""
                cursor.execute(portfolio_value_start_date_query, (analyst_name,))
                result = cursor.fetchone()
                portfolio_value_start_date = result[0] if result else 0

                portfolio_value_end_date_query = """
                                                    select top 1 portfolio_value, trade_date from agent_backtest 
                                                    where agent_name = ? order by trade_date desc"""
                cursor.execute(portfolio_value_end_date_query, (analyst_name,))
                result = cursor.fetchone()
                portfolio_value_end_date = result[0] if result else 0

                if float(portfolio_value_start_date) == 0:
                    benchmark_return = 0.0
                else:
                    benchmark_return = round(((float(portfolio_value_end_date) - float(portfolio_value_start_date)) / float(portfolio_value_start_date)),2)

                agent_performace_metrics_query = """select total_return, total_realized_gains, sharpe_ratio,
                                                    max_drawdown, win_rate from agent_performance 
                                                    where agent_name = ?;"""
                cursor.execute(agent_performace_metrics_query, (analyst_name,))
                agent_data["agent_performance_metric"] = rows_to_dict_list(cursor)
                agent_data["agent_performance_metric"][0]["benchmark_return"] = benchmark_return

        print(agent_data["agent_performance_metric"])
    except Exception as e:
        print("Error while reading data from SQL Server:", e)
        return {"error": str(e)}, 500
    
    return jsonify(agent_data), 200


@app.route('/ai_hedge_fund_back_test', methods=['POST'])
def ai_hedge_fund_back_test():
    data = request.get_json()
    tickers = data.get('tickers')
    selected_analysts = get_agent_name(data.get('analysts'))[0]    
    model_choice = data.get('model_choice', 'gpt-4o-mini')
    user_start_date = data.get('start_date', '2024-01-01')
    user_end_date = data.get('end_date', '2024-09-01')
    new_columns=["Agent", "Date", "Ticker", "Action", "Quantity", "Price", "Shares",
                "Position Value", "Bullish", "Bearish", "Neutral",
                "Cash", "Portfolio Value", "Return total P&L",
                "Return %", "Buy and Hold Value"]

    db_server = os.getenv('DB_SERVER')
    db_name = os.getenv('DB_NAME')
    db_username = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT')
    db_driver = os.getenv('DRIVER')
    try:
        with pyodbc.connect('DRIVER='+db_driver+';SERVER=tcp:'+db_server+';PORT='+db_port+';DATABASE='+db_name+';UID='+db_username+';PWD='+ db_password) as conn:
            with conn.cursor() as cursor:
                back_test_query = """select * from agent_backtest 
                                        where agent_name = ? 
                                        and (trade_date >= ?  and trade_date <= ?);"""
                cursor.execute(back_test_query, (selected_analysts, user_start_date, user_end_date))
                back_test_data = rows_to_dict_list(cursor)

                # Executing with new version of manual computation of portfolio summary
                # portfolio_summary_query = """select * from agent_performance 
                #                         where agent_name = ?;"""
                
                # cursor.execute(portfolio_summary_query, (selected_analysts,))
                # portfolio_summary = rows_to_dict_list(cursor)

    except Exception as e:
        print("Error while reading data from SQL Server:", e)
        return {"error": str(e)}, 500

    df = pd.DataFrame(back_test_data)
    df.columns = new_columns
    backtest_dict = df.to_dict(orient='records')

    print(df.head())
    print(df.columns)

    back_test_plot_data = {"Date": df['Date'].tolist(),
                      "portfolio_value": df['Portfolio Value'].tolist(),
                      "buy_hold_value": df['Buy and Hold Value'].tolist()}

    backtest_result = {
        "backtest_data": backtest_dict,
        "portfolio_summary": portfolio_summary_computation(df, user_start_date, user_end_date),
        "back_test_plot": back_test_plot_data
    }
    return  jsonify(backtest_result), 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")