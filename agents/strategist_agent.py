import pandas as pd
from typing import Dict, List
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI

from .config import Config
from .state_models import CustomerInfo, MoverInfo, FilteredMovers, MarketResearch
from . import firebase
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from integrations.perplexity_client import PerplexityClient

# system prompt for creating a new negotiation strategy
planner_system_prompt = """You are a strategic negotiator. Based on the customer requirements and available movers,
you need to create a detailed negotiation instruction for a phone call that maximizes the customer's chances of getting the best price with good quality services.
 Be concise and write the plan in less than 10 sentences, and include key points only.
"""

class StrategistAgent:
    def __init__(self, user_id: str, model: str = Config.PLANNER_MODEL, database_path: str = "./agents/movers_database.csv"):
        self.llm = ChatOpenAI(model=model)
        self.user_id = user_id
        self.movers_db = pd.read_csv(database_path)
        # Initialize Perplexity client for market research
        try:
            self.perplexity_client = PerplexityClient()
            self.perplexity_enabled = True
        except ValueError as e:
            print(f"Warning: Perplexity not initialized - {e}")
            self.perplexity_enabled = False

    def __call__(self, state: Dict) -> Dict:
        customer_info = state["customer_info"]

        # STEP 1: Conduct market research using Perplexity
        market_research = None
        if self.perplexity_enabled:
            print("\nConducting market research with Perplexity...\n")
            move_type = "long-distance" if customer_info.is_long_distance else "local"

            research_result = self.perplexity_client.get_moving_market_insights(
                origin=customer_info.current_address,
                destination=customer_info.destination_address,
                move_type=move_type
            )

            market_research = MarketResearch(
                query=f"Market insights for {move_type} move: {customer_info.current_address} → {customer_info.destination_address}",
                content=research_result,
                model_used="sonar",
                timestamp=datetime.now().isoformat()
            )

            print(f"📊 Market Research:\n{research_result}\n")
            firebase.update_data(self.user_id, { "market_research": market_research.model_dump() })

        # STEP 2: Filter and select movers
        selected_movers = self._get_movers_data(customer_info)

        # STEP 3: Generate negotiation strategy (enhanced with market research)
        strategy_context = f"Customer Info: {customer_info}"
        if market_research:
            strategy_context += f"\n\nMarket Research Insights:\n{market_research.content}"

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", planner_system_prompt),
            ("human", "Generate a concise instruction for guiding the voice agent to negotiate with the mover through a phone call. Use the following information:\n\n{context}"),
        ])
        chain = self.prompt | self.llm
        response = chain.invoke({"context": strategy_context})

        firebase.update_data(self.user_id, { "strategy": response.content })

        print(f"📋 Negotiation strategy: {response.content}")

        state["selected_movers"] = selected_movers
        state["market_research"] = market_research
        state["negotiation_strategy"] = response
        state["customer_info"] = customer_info

        return state


    #TODO: Implementation to read and format movers data from CSV, could use create_pandas_dataframe_agent
    def _get_movers_data(self, customer_info: CustomerInfo) -> List[Dict]:

        movers = self.movers_db.to_dict('records')
        filter_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are a helpful assistant that filters a list of mover vendors based on the user's criteria.
                First determine if the move is local or long distance based on the source and destination zipcodes,
                if zipcodes are not available try to assume them based on the greater area provided.
                Filter only the top 3 movers that best fit the user based on their information.
                Return the names of the filtered movers as a list.
                Also provide a rationale for the filtering.
            """),
            ("human", "Filter the list of movers: {movers} based on the customer information {customer_info}."),
        ])
        chain = filter_prompt | self.llm.with_structured_output(FilteredMovers)
        response: FilteredMovers = chain.invoke({ "customer_info": customer_info, "movers": movers })
        print("Filtered Movers: ", response)


        # prompt = ChatPromptTemplate.from_messages([("human", "Summarzie the list of movers information. {request}")])
        # chain = prompt | self.llm.with_structured_output(FilteredMovers)
        # response = chain.invoke({ "request": response.content })
        # print("Filtered Movers: ", response)

        filtered_movers = [mover for mover in movers if mover["name"] in response.movers]

        firebase.update_data(self.user_id, { "movers": filtered_movers, "moverRationale": response.rationale })
        return filtered_movers
