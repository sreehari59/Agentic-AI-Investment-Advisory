-- Create table

CREATE TABLE AgentTradeInfo(
    analyst_name NVARCHAR(100),
    ticker NVARCHAR(100),
    signal NVARCHAR(100),
    analyst_confidence NVARCHAR(100),
    trade_decision_action NVARCHAR(100),
    trade_decision_quantity NVARCHAR(100),
    trade_decision_confidence NVARCHAR(100),
    llm_reasoning NVARCHAR(MAX),
    llm_name NVARCHAR(100),
    execution_date DATE
);

-- Insert data into TradeSignals
INSERT INTO TradeSignals (
    analyst_name,
    signal,
    analyst_confidence,
    trade_decision_action,
    trade_decision_quantity,
    trade_decision_confidence,
    llm_reasoning,
    llm_name,
    execution_date
)
VALUES
('Alice Johnson', 'BUY', 'High', 'Enter Long', '100', 'Strong', 'The LLM identified a bullish breakout pattern in historical data.', 'GPT-4', '2025-06-20'),
('Bob Smith', 'SELL', 'Medium', 'Exit Position', '50', 'Moderate', 'Earnings report indicates weakening fundamentals.', 'Claude 3', '2025-06-19'),
('Carlos Liu', 'HOLD', 'Low', 'No Action', '0', 'Weak', 'Market volatility is too high for a clear decision.', 'Gemini 1.5', '2025-06-18');


-- Create trade decision table
Create table trade_decision(
    group_decision_id VARCHAR(50) NOT NULL PRIMARY KEY,
    trade_decision_action NVARCHAR(100),
    trade_decision_quantity NVARCHAR(100),
    trade_decision_confidence NVARCHAR(100),
    trade_decision_reasoning NVARCHAR(MAX)
)

-- Create Table backtest
CREATE TABLE backtest (
    trade_date DATE,
    ticker NVARCHAR(10),
    trade_action NVARCHAR(10),
    quantity INT,
    price DECIMAL(10, 2),
    shares INT,
    position_value DECIMAL(18, 2),
    bullish INT,
    bearish INT,
    neutral INT,
    porfolio_id VARCHAR(50)
);

-- create backtest_portfolio_summary table
CREATE TABLE backtest_portfolio_summary (
    total_return VARCHAR(50),
    total_realized_gains VARCHAR(50),
    sharpe_ratio VARCHAR(50),
    max_drawdown VARCHAR(50),
    win_rate VARCHAR(50),
    win_loss_ratio VARCHAR(50),
    max_consecutive_wins INT,
    max_consecutive_losses INT,
    portfolio_id VARCHAR(50) NOT NULL PRIMARY KEY,
    cash FLOAT
    portfolio_value FLOAT,
    return_total_PL FLOAT,
    return_percentage FLOAT,
    buy_hold_value FLOAT,
);

-- Create table InvestmentAgents
CREATE TABLE InvestmentAgents (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100),
    description NVARCHAR(MAX),
    performance_ytd NVARCHAR(20),
    total_trades INT,
    sharpe_ratio DECIMAL(5,2),
    win_rate NVARCHAR(20)
);


INSERT INTO InvestmentAgents (
    name,
    description,
    performance_ytd,
    total_trades,
    sharpe_ratio,
    win_rate
)
VALUES (
    'Bill Ackman Agent',
    'Prominent activist investor taking large, concentrated positions in undervalued companies and pushing for strategic changes. Combines fundamental analysis with active engagement to unlock shareholder value through operational improvements.',
    24.10,
    12,
    1.42,
    68.00
);


-- Create Table agent_backtest
CREATE TABLE agent_backtest (
    agent_name NVARCHAR(25),
    trade_date DATE,
    ticker NVARCHAR(10),
    trade_action NVARCHAR(10),
    quantity INT,
    price DECIMAL(10, 2),
    shares INT,
    position_value DECIMAL(18, 2),
    bullish INT,
    bearish INT,
    neutral INT,
    cash FLOAT,
	portfolio_value FLOAT,
	return_total_PL FLOAT,
	return_percentage FLOAT,
	buy_hold_value FLOAT
);
