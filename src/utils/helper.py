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