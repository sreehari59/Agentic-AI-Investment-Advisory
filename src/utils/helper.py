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
