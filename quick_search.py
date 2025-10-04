#!/usr/bin/env python3
"""
Quick MoveScout search with pre-filled customer information
"""

import os
import json
from typing import Dict, List
from dotenv import load_dotenv
from agents.linkup_search_agent import LinkUpSearchAgent
from agents.realtime_search_agent import RealtimeSearchAgent
from agents.fallback_search_agent import FallbackSearchAgent

# Load environment variables
load_dotenv()

def get_quick_customer_info() -> Dict:
    """
    Pre-filled customer information for quick testing
    """
    return {
        "name": "Kanishka",
        "phone": "3472009240",
        "current_address": "523 Franklin Ave, Brooklyn, New York",
        "destination_address": "1875 Atlantic Ave, Brooklyn, New York",
        "move_out_date": "10/10/2025",
        "move_in_date": "10/10/2025",
        "apartment_size": "2BR",
        "packing_needed": True,
        "special_items": "none",
        "storage_needed": False
    }

def search_with_linkup(customer_info: Dict) -> List[Dict]:
    """
    Try to search using LinkUp API
    """
    api_key = os.getenv("LINKUP_API_KEY")
    if not api_key or api_key == "your_linkup_api_key_here":
        print("⚠️  LinkUp API key not configured in .env file")
        return []
    
    try:
        print("🔍 Searching with LinkUp API...")
        search_agent = LinkUpSearchAgent(api_key=api_key)
        results = search_agent.search_moving_companies(customer_info)
        
        if results:
            print(f"✅ LinkUp found {len(results)} companies")
            return results
        else:
            print("❌ LinkUp returned no results")
            return []
            
    except Exception as e:
        print(f"❌ LinkUp search failed: {e}")
        return []

def search_with_realtime(customer_info: Dict) -> List[Dict]:
    """
    Use real-time web scraping search
    """
    try:
        print("🔍 Using real-time web search...")
        realtime_agent = RealtimeSearchAgent()
        results = realtime_agent.search_moving_companies(customer_info)
        
        if results:
            print(f"✅ Real-time search found {len(results)} companies")
            return results
        else:
            print("❌ Real-time search returned no results")
            return []
            
    except Exception as e:
        print(f"❌ Real-time search failed: {e}")
        return []

def search_with_fallback(customer_info: Dict) -> List[Dict]:
    """
    Use fallback search method
    """
    try:
        print("🔍 Using fallback search method...")
        fallback_agent = FallbackSearchAgent()
        results = fallback_agent.search_moving_companies(customer_info)
        
        if results:
            print(f"✅ Fallback search found {len(results)} companies")
            return results
        else:
            print("❌ Fallback search returned no results")
            return []
            
    except Exception as e:
        print(f"❌ Fallback search failed: {e}")
        return []

def display_results(results: List[Dict], method: str):
    """
    Display search results
    """
    if not results:
        print("No moving companies found.")
        return
    
    print(f"\n🎯 Found {len(results)} moving companies using {method}:")
    print("=" * 60)
    
    for i, company in enumerate(results, 1):
        print(f"\n{i}. {company.get('name', 'Unknown')}")
        print(f"   Source: {company.get('source', 'Unknown')}")
        print(f"   Description: {company.get('description', 'N/A')[:100]}...")
        print(f"   Website: {company.get('website', 'N/A')}")
        
        contact = company.get('contact_info', {})
        if contact.get('phone'):
            print(f"   📞 Phone: {contact['phone']}")
        if contact.get('email'):
            print(f"   📧 Email: {contact['email']}")
        if contact.get('website'):
            print(f"   🌐 Website: {contact['website']}")
        if contact.get('address'):
            print(f"   📍 Address: {contact['address']}")
        
        quotation = company.get('quotation', {})
        if quotation.get('estimated_cost'):
            print(f"   💰 Estimated Cost: {quotation['estimated_cost']}")
        
        services = company.get('services', [])
        if services:
            print(f"   🛠️  Services: {', '.join(services)}")

def save_results(results: List[Dict], customer_info: Dict, method: str):
    """
    Save results to file
    """
    if not results:
        print("No results to save.")
        return None
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quick_search_{method}_{timestamp}.txt"
    filepath = f"/Users/nirbhayareddy/Desktop/Hackathon/CC2/movescout/{filename}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"QUICK MOVE SCOUT SEARCH RESULTS ({method.upper()})\n")
        f.write("=" * 70 + "\n\n")
        
        # Customer information
        f.write("CUSTOMER INFORMATION:\n")
        f.write("-" * 20 + "\n")
        for key, value in customer_info.items():
            f.write(f"{key.replace('_', ' ').title()}: {value}\n")
        f.write("\n")
        
        # Search results
        f.write("TOP MOVING COMPANIES:\n")
        f.write("-" * 30 + "\n\n")
        
        for i, company in enumerate(results, 1):
            f.write(f"{i}. {company.get('name', 'Unknown Company')}\n")
            f.write(f"   Source: {company.get('source', 'Unknown')}\n")
            f.write(f"   Description: {company.get('description', 'No description available')}\n")
            f.write(f"   Website: {company.get('website', 'No website available')}\n")
            
            # Contact information
            contact = company.get('contact_info', {})
            if contact.get('phone'):
                f.write(f"   📞 Phone: {contact['phone']}\n")
            if contact.get('email'):
                f.write(f"   📧 Email: {contact['email']}\n")
            if contact.get('website'):
                f.write(f"   🌐 Website: {contact['website']}\n")
            if contact.get('address'):
                f.write(f"   📍 Address: {contact['address']}\n")
            
            # Services
            services = company.get('services', [])
            if services:
                f.write(f"   Services: {', '.join(services)}\n")
            
            # Quotation information
            quotation = company.get('quotation', {})
            if quotation.get('estimated_cost'):
                f.write(f"   Estimated Cost: {quotation['estimated_cost']}\n")
            if quotation.get('cost_range'):
                f.write(f"   Cost Range: {quotation['cost_range']}\n")
            
            f.write("\n")
        
        # Summary
        f.write("SUMMARY:\n")
        f.write("-" * 10 + "\n")
        f.write(f"Found {len(results)} moving companies using {method} method.\n")
        f.write("Contact information and estimated costs are provided above.\n")
        f.write("Please contact each company directly for detailed quotes.\n")
        f.write(f"\nSearch completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    return filepath

def main():
    """
    Quick search with pre-filled customer information
    """
    print("🚚 MoveScout Quick Search")
    print("=" * 40)
    
    # Get pre-filled customer information
    customer_info = get_quick_customer_info()
    
    print(f"Customer: {customer_info['name']}")
    print(f"From: {customer_info['current_address']}")
    print(f"To: {customer_info['destination_address']}")
    print(f"Move date: {customer_info['move_out_date']}")
    print(f"Apartment: {customer_info['apartment_size']}")
    print(f"Packing needed: {customer_info['packing_needed']}")
    print()
    
    # Try different search methods in order of preference
    results = []
    method = ""
    
    # 1. Try LinkUp API first
    results = search_with_linkup(customer_info)
    method = "linkup"
    
    # 2. If LinkUp fails, try real-time web scraping
    if not results:
        results = search_with_realtime(customer_info)
        method = "realtime"
    
    # 3. If real-time fails, use fallback
    if not results:
        results = search_with_fallback(customer_info)
        method = "fallback"
    
    # Display results
    display_results(results, method)
    
    # Save results to file
    if results:
        filepath = save_results(results, customer_info, method)
        print(f"\n💾 Results saved to: {filepath}")
    
    # Display summary
    print("\n" + "=" * 70)
    print("📋 SUMMARY")
    print("=" * 70)
    if results:
        print(f"✅ Found {len(results)} moving companies using {method} method.")
        print("📞 Contact information and estimated costs are provided above.")
        print("💰 Please contact each company directly for detailed quotes.")
        print(f"📄 Detailed results saved to file.")
    else:
        print("❌ No moving companies found. Please try different search criteria.")

if __name__ == "__main__":
    main()
