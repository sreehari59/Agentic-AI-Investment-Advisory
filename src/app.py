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

import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tabulate import tabulate
from utils.visualize import save_graph_as_png
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

init(autoreset=True)

app = Flask(__name__)
CORS(app)


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


@app.route('/ai_hedge_fund', methods=['POST'])
def ai_hedge_fund():
    data = request.get_json()
    ticker_name = data.get('tickers')
    analyst = data.get('analysts')
    tickers = [ticker_name]
    # selected_analysts = ["cathie_wood","valuation_analyst", "sentiment_analyst", "technical_analyst", "fundamentals_analyst"]
    selected_analysts = [analyst]
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
        start_date="2025-06-23",
        end_date="2025-06-24",
        portfolio=portfolio,
        show_reasoning=False,
        selected_analysts=selected_analysts,
        model_name=model_choice,
        model_provider=model_provider,
    )
    # print_trading_output(result)

    print("tickers:", tickers)
    print("selected_analysts:", selected_analysts)
    print("model_choice:", model_choice)


    prefix = "GD_" 
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
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

    return  {"message": "Data inserted succesfully"}, 200

@app.route('/ai_hedge_fund_back_test', methods=['POST'])
def ai_hedge_fund_back_test():
    data = request.get_json()
    ticker_name = data.get('tickers')
    analyst = data.get('analysts')
    tickers = [ticker_name]
    # selected_analysts = ["cathie_wood","valuation_analyst", "sentiment_analyst", "technical_analyst", "fundamentals_analyst"]
    selected_analysts = [analyst]
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
        start_date="2025-06-23",
        end_date="2025-06-24",
        portfolio=portfolio,
        show_reasoning=False,
        selected_analysts=selected_analysts,
        model_name=model_choice,
        model_provider=model_provider,
    )
    # print_trading_output(result)

    print("tickers:", tickers)
    print("selected_analysts:", selected_analysts)
    print("model_choice:", model_choice)


    prefix = "GD_" 
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
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

    return  {"message": "Data inserted succesfully"}, 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")