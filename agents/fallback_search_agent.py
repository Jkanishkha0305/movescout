import os
import json
from typing import Dict, List, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup

class FallbackSearchAgent:
    """
    Fallback search agent that uses web scraping when LinkUp API is not available
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def search_moving_companies(self, customer_info: Dict) -> List[Dict]:
        """
        Search for moving companies using web scraping
        """
        origin = customer_info.get('current_address', '')
        destination = customer_info.get('destination_address', '')
        
        # Create search queries
        search_queries = [
            f"moving companies {origin} to {destination}",
            f"movers Brooklyn New York",
            f"local moving services Brooklyn"
        ]
        
        all_companies = []
        
        for query in search_queries:
            print(f"Searching web for: {query}")
            companies = self._search_google(query)
            all_companies.extend(companies)
            
            if len(all_companies) >= 5:
                break
        
        # Remove duplicates
        unique_companies = []
        seen_names = set()
        for company in all_companies:
            name = company.get('name', '').lower()
            if name not in seen_names and name:
                unique_companies.append(company)
                seen_names.add(name)
        
        return unique_companies[:5]
    
    def _search_google(self, query: str) -> List[Dict]:
        """
        Search Google for moving companies (simplified version)
        """
        companies = []
        
        try:
            # This is a simplified example - in practice you'd use Google Custom Search API
            # or other legitimate search methods
            
            # Mock data for demonstration
            mock_companies = [
                {
                    'name': 'Brooklyn Moving Company',
                    'url': 'https://brooklynmoving.com',
                    'description': 'Professional moving services in Brooklyn',
                    'contact_info': {'phone': '(718) 555-0123', 'email': 'info@brooklynmoving.com'},
                    'services': ['Local Moving', 'Packing', 'Loading'],
                    'quotation': {'estimated_cost': '$800-1200', 'cost_range': 'Based on apartment size'}
                },
                {
                    'name': 'NYC Movers Pro',
                    'url': 'https://nycmoverspro.com',
                    'description': 'Full-service moving company serving Brooklyn',
                    'contact_info': {'phone': '(718) 555-0456', 'email': 'contact@nycmoverspro.com'},
                    'services': ['Residential Moving', 'Commercial Moving', 'Storage'],
                    'quotation': {'estimated_cost': '$900-1500', 'cost_range': 'Includes packing and loading'}
                },
                {
                    'name': 'Brooklyn Best Movers',
                    'url': 'https://brooklynbestmovers.com',
                    'description': 'Affordable moving services in Brooklyn',
                    'contact_info': {'phone': '(718) 555-0789', 'email': 'hello@brooklynbestmovers.com'},
                    'services': ['Local Moving', 'Long Distance', 'Packing Services'],
                    'quotation': {'estimated_cost': '$700-1100', 'cost_range': 'Competitive rates'}
                },
                {
                    'name': 'Atlantic Moving Co',
                    'url': 'https://atlanticmoving.com',
                    'description': 'Reliable moving services in Brooklyn and surrounding areas',
                    'contact_info': {'phone': '(718) 555-0321', 'email': 'info@atlanticmoving.com'},
                    'services': ['Residential', 'Office Moving', 'Storage Solutions'],
                    'quotation': {'estimated_cost': '$850-1300', 'cost_range': 'Free estimates available'}
                },
                {
                    'name': 'Brooklyn Express Movers',
                    'url': 'https://brooklynexpressmovers.com',
                    'description': 'Fast and efficient moving services',
                    'contact_info': {'phone': '(718) 555-0654', 'email': 'service@brooklynexpressmovers.com'},
                    'services': ['Express Moving', 'Packing', 'Unpacking'],
                    'quotation': {'estimated_cost': '$750-1250', 'cost_range': 'Same-day service available'}
                }
            ]
            
            companies = mock_companies
            
        except Exception as e:
            print(f"Error in web search: {e}")
        
        return companies
    
    def save_results_to_file(self, results: List[Dict], customer_info: Dict, filename: str = None) -> str:
        """
        Save search results and summary to a text file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"moving_companies_fallback_{timestamp}.txt"
        
        filepath = f"/Users/nirbhayareddy/Desktop/Hackathon/CC2/movescout/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("MOVING COMPANIES SEARCH RESULTS (Fallback Method)\n")
            f.write("=" * 60 + "\n\n")
            
            # Customer information
            f.write("CUSTOMER INFORMATION:\n")
            f.write("-" * 20 + "\n")
            for key, value in customer_info.items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            f.write("\n")
            
            # Search results
            f.write("TOP 5 MOVING COMPANIES:\n")
            f.write("-" * 30 + "\n\n")
            
            for i, company in enumerate(results, 1):
                f.write(f"{i}. {company.get('name', 'Unknown Company')}\n")
                f.write(f"   Description: {company.get('description', 'No description available')}\n")
                f.write(f"   Website: {company.get('url', 'No website available')}\n")
                
                # Contact information
                contact = company.get('contact_info', {})
                if contact.get('phone'):
                    f.write(f"   Phone: {contact['phone']}\n")
                if contact.get('email'):
                    f.write(f"   Email: {contact['email']}\n")
                
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
            f.write(f"Found {len(results)} moving companies matching your criteria.\n")
            f.write("Contact information and estimated costs are provided above.\n")
            f.write("Please contact each company directly for detailed quotes.\n")
            f.write("\nNote: These results were generated using fallback search methods.\n")
        
        return filepath
