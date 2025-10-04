"""
Perplexity API client for market research and real-time information.
Uses Perplexity's online LLMs for up-to-date moving industry insights.
"""

import os
from typing import Optional, Dict
from openai import OpenAI


class PerplexityClient:
    """
    Client for interacting with Perplexity API.
    Provides market research capabilities for moving services.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Perplexity client.

        Args:
            api_key: Perplexity API key. If not provided, reads from PERPLEXITY_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("Perplexity API key not found. Set PERPLEXITY_API_KEY environment variable.")

        # Perplexity uses OpenAI-compatible API
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.perplexity.ai"
        )

    def research(self, query: str, model: str = "sonar") -> Dict[str, str]:
        """
        Perform market research using Perplexity's online models.

        Args:
            query: Research question or topic
            model: Perplexity model to use (default: sonar for fast responses)
                  Options:
                  - sonar (fast, cost-effective, built on Llama 3.3 70B)
                  - sonar-pro (more comprehensive, handles complex queries)
                  - sonar-reasoning (reasoning model for complex analysis)

        Returns:
            Dict with 'content' (research findings) and 'citations' (if available)
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant specializing in moving industry research. Provide accurate, up-to-date information with relevant data and insights."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ]
            )

            content = response.choices[0].message.content

            # Extract citations if available (Perplexity often includes sources)
            return {
                "content": content,
                "model_used": model,
                "query": query
            }

        except Exception as e:
            print(f"Error in Perplexity research: {str(e)}")
            return {
                "content": f"Unable to complete research: {str(e)}",
                "model_used": model,
                "query": query,
                "error": str(e)
            }

    def get_moving_market_insights(self, origin: str, destination: str, move_type: str = "long-distance") -> str:
        """
        Get specific market insights for a moving route.

        Args:
            origin: Origin location (city, state or zipcode)
            destination: Destination location
            move_type: Type of move ("local" or "long-distance")

        Returns:
            Market insights as formatted string
        """
        query = f"""
        Research the current moving market for {move_type} moves from {origin} to {destination}.
        Include:
        1. Average cost ranges for this route
        2. Typical pricing factors (distance, volume, season)
        3. Current market trends (busy season, pricing changes)
        4. Tips for negotiating with movers

        Keep the response concise and actionable (under 200 words).
        """

        result = self.research(query)
        return result["content"]

    def get_mover_reputation(self, mover_name: str) -> str:
        """
        Research a specific moving company's reputation and reviews.

        Args:
            mover_name: Name of the moving company

        Returns:
            Reputation summary
        """
        query = f"""
        What is the current reputation of {mover_name} moving company?
        Include recent customer reviews, ratings, and any red flags or positive highlights.
        Keep it brief (under 150 words).
        """

        result = self.research(query)
        return result["content"]

    def get_mover_phone_number(self, mover_name: str, location: str = None) -> Dict[str, str]:
        """
        Get contact phone number for a moving company.

        Args:
            mover_name: Name of the moving company
            location: Optional location (city, state) for local offices

        Returns:
            Dict with 'phone_number' and 'raw_response'
        """
        if location:
            query = f"""
            What is the customer service phone number for {mover_name} moving company
            in or near {location}? Provide the direct contact number.
            """
        else:
            query = f"""
            What is the main customer service phone number for {mover_name} moving company?
            Provide the primary contact number for quotes and inquiries.
            """

        result = self.research(query)

        # Extract phone numbers using regex
        import re
        phone_patterns = [
            r'1-?8\d{2}-?\d{3}-?\d{4}',      # 1-800-XXX-XXXX or 800-XXX-XXXX
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', # XXX-XXX-XXXX
            r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}', # (XXX) XXX-XXXX
        ]

        found_numbers = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, result['content'])
            found_numbers.extend(matches)

        # Get the first phone number found (usually the main one)
        phone_number = found_numbers[0] if found_numbers else None

        return {
            "phone_number": phone_number,
            "all_numbers": list(set(found_numbers)),  # All unique numbers found
            "raw_response": result['content'],
            "model_used": result['model_used']
        }


# Singleton instance for easy import
_default_client = None

def get_client() -> PerplexityClient:
    """Get or create the default Perplexity client instance."""
    global _default_client
    if _default_client is None:
        _default_client = PerplexityClient()
    return _default_client


# Convenience functions for direct use
def research_market(origin: str, destination: str, move_type: str = "long-distance") -> str:
    """Quick function to get market insights."""
    client = get_client()
    return client.get_moving_market_insights(origin, destination, move_type)


def research_mover(mover_name: str) -> str:
    """Quick function to research a mover's reputation."""
    client = get_client()
    return client.get_mover_reputation(mover_name)


def get_mover_phone(mover_name: str, location: str = None) -> Dict[str, str]:
    """Quick function to get a mover's phone number."""
    client = get_client()
    return client.get_mover_phone_number(mover_name, location)
