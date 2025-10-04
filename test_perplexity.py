"""
Test script for Perplexity integration.
This script tests the Perplexity client independently.

Usage:
    python test_perplexity.py
"""

import os
import sys
import io
from dotenv import load_dotenv

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from integrations.perplexity_client import PerplexityClient, research_market


def test_basic_research():
    """Test basic Perplexity research functionality."""
    print("=" * 60)
    print("Testing Perplexity API Integration")
    print("=" * 60)

    try:
        # Initialize client
        print("\n1. Initializing Perplexity client...")
        client = PerplexityClient()
        print("✅ Client initialized successfully")

        # Test basic research query
        print("\n2. Testing basic research query...")
        query = "What are the average costs for long-distance moving in the USA in 2024?"
        result = client.research(query)

        print(f"\n📊 Query: {result['query']}")
        print(f"🤖 Model: {result['model_used']}")
        print(f"\n📝 Response:\n{result['content']}")

        # Test moving market insights
        print("\n" + "=" * 60)
        print("\n3. Testing moving market insights...")
        origin = "San Francisco, CA"
        destination = "Miami, FL"

        insights = client.get_moving_market_insights(origin, destination, "long-distance")
        print(f"\n🚚 Market Insights for {origin} → {destination}:")
        print(f"\n{insights}")

        # Test mover reputation
        print("\n" + "=" * 60)
        print("\n4. Testing mover reputation research...")
        mover_name = "United Van Lines"
        reputation = client.get_mover_reputation(mover_name)
        print(f"\n⭐ Reputation of {mover_name}:")
        print(f"\n{reputation}")

        print("\n" + "=" * 60)
        print("\n✅ All tests passed successfully!")
        print("=" * 60)

    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure to set PERPLEXITY_API_KEY in your .env file")
        print("   Get your API key from: https://www.perplexity.ai/settings/api")
        return False

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_convenience_function():
    """Test convenience function."""
    print("\n" + "=" * 60)
    print("\n5. Testing convenience function...")

    try:
        result = research_market("New York, NY", "Los Angeles, CA")
        print(f"\n✅ Convenience function works!")
        print(f"\n{result[:200]}...")  # Print first 200 chars

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

    return True


if __name__ == "__main__":
    print("\n🔬 Perplexity Integration Test\n")

    # Check if API key is set
    if not os.getenv("PERPLEXITY_API_KEY"):
        print("⚠️  WARNING: PERPLEXITY_API_KEY not found in environment")
        print("📝 Please add it to your .env file")
        print("🔑 Get your API key from: https://www.perplexity.ai/settings/api\n")
        sys.exit(1)

    # Run tests
    success = test_basic_research()
    if success:
        test_convenience_function()

    print("\n✨ Testing complete!\n")
