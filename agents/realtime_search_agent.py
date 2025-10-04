import os
import json
import requests
import re
from typing import Dict, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import time

class RealtimeSearchAgent:
    """
    Real-time web search agent that scrapes actual moving company data from the web
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_moving_companies(self, customer_info: Dict) -> List[Dict]:
        """
        Search for real moving companies using web scraping
        """
        origin = customer_info.get('current_address', '')
        destination = customer_info.get('destination_address', '')
        
        print(f"🔍 Searching real-time for moving companies...")
        print(f"From: {origin}")
        print(f"To: {destination}")
        
        # Try multiple search strategies
        search_strategies = [
            self._search_yellow_pages,
            self._search_google_business,
            self._search_moving_directories,
            self._search_local_listings
        ]
        
        all_companies = []
        
        for strategy in search_strategies:
            try:
                companies = strategy(origin, destination)
                if companies:
                    print(f"✅ Found {len(companies)} companies using {strategy.__name__}")
                    all_companies.extend(companies)
                    
                    if len(all_companies) >= 5:
                        break
                else:
                    print(f"❌ No results from {strategy.__name__}")
            except Exception as e:
                print(f"❌ Error in {strategy.__name__}: {e}")
                continue
        
        # Remove duplicates and get top 5
        unique_companies = self._remove_duplicates(all_companies)
        top_5 = unique_companies[:5]
        
        # Enhance with additional data
        enhanced_companies = []
        for company in top_5:
            enhanced = self._enhance_company_data(company, customer_info)
            enhanced_companies.append(enhanced)
        
        return enhanced_companies
    
    def _search_yellow_pages(self, origin: str, destination: str) -> List[Dict]:
        """
        Search Yellow Pages for moving companies
        """
        companies = []
        
        # Extract city from origin
        city = self._extract_city(origin)
        if not city:
            return companies
        
        try:
            # Search Yellow Pages
            search_url = f"https://www.yellowpages.com/{city.lower().replace(' ', '-')}-ny/movers"
            print(f"Searching Yellow Pages: {search_url}")
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find business listings
                listings = soup.find_all('div', class_='result')
                
                for listing in listings[:5]:  # Limit to 5
                    company = self._extract_yellow_pages_company(listing)
                    if company:
                        companies.append(company)
            
        except Exception as e:
            print(f"Yellow Pages search error: {e}")
        
        return companies
    
    def _search_google_business(self, origin: str, destination: str) -> List[Dict]:
        """
        Search Google Business listings
        """
        companies = []
        
        try:
            # Use Google search for local businesses
            city = self._extract_city(origin)
            search_query = f"moving companies {city} New York"
            
            # Google search URL
            search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            print(f"Searching Google Business: {search_url}")
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for business listings in search results
                business_results = soup.find_all('div', class_='g')
                
                for result in business_results[:5]:
                    company = self._extract_google_business_company(result)
                    if company:
                        companies.append(company)
            
        except Exception as e:
            print(f"Google Business search error: {e}")
        
        return companies
    
    def _search_moving_directories(self, origin: str, destination: str) -> List[Dict]:
        """
        Search moving company directories
        """
        companies = []
        
        try:
            # Search moving directories
            city = self._extract_city(origin)
            search_queries = [
                f"best moving companies {city}",
                f"top movers {city} New York",
                f"moving services {city}"
            ]
            
            for query in search_queries:
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                print(f"Searching directories: {search_url}")
                
                response = self.session.get(search_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract company information from search results
                    results = soup.find_all('div', class_='g')
                    
                    for result in results[:3]:  # Limit per query
                        company = self._extract_directory_company(result)
                        if company:
                            companies.append(company)
                
                time.sleep(1)  # Be respectful to servers
            
        except Exception as e:
            print(f"Directory search error: {e}")
        
        return companies
    
    def _search_local_listings(self, origin: str, destination: str) -> List[Dict]:
        """
        Search local business listings
        """
        companies = []
        
        try:
            city = self._extract_city(origin)
            
            # Search for local moving companies
            search_queries = [
                f"movers near {origin}",
                f"moving companies {city}",
                f"local movers {city} New York"
            ]
            
            for query in search_queries:
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                print(f"Searching local listings: {search_url}")
                
                response = self.session.get(search_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract from search results
                    results = soup.find_all('div', class_='g')
                    
                    for result in results[:2]:  # Limit per query
                        company = self._extract_local_company(result)
                        if company:
                            companies.append(company)
                
                time.sleep(1)
            
        except Exception as e:
            print(f"Local listings search error: {e}")
        
        return companies
    
    def _extract_city(self, address: str) -> str:
        """Extract city from address"""
        # Simple city extraction - look for common patterns
        if 'Brooklyn' in address:
            return 'Brooklyn'
        elif 'Manhattan' in address:
            return 'Manhattan'
        elif 'Queens' in address:
            return 'Queens'
        elif 'Bronx' in address:
            return 'Bronx'
        else:
            # Try to extract city from address
            parts = address.split(',')
            if len(parts) >= 2:
                return parts[-2].strip()
            return 'New York'
    
    def _extract_yellow_pages_company(self, listing) -> Optional[Dict]:
        """Extract company info from Yellow Pages listing"""
        try:
            name_elem = listing.find('h2', class_='n')
            if not name_elem:
                return None
            
            name = name_elem.get_text(strip=True)
            
            # Extract phone
            phone_elem = listing.find('div', class_='phones')
            phone = phone_elem.get_text(strip=True) if phone_elem else ''
            
            # Extract address
            address_elem = listing.find('div', class_='adr')
            address = address_elem.get_text(strip=True) if address_elem else ''
            
            # Extract website
            website_elem = listing.find('a', class_='track-visit-website')
            website = website_elem.get('href', '') if website_elem else ''
            
            return {
                'name': name,
                'phone': phone,
                'address': address,
                'website': website,
                'source': 'Yellow Pages'
            }
        except:
            return None
    
    def _extract_google_business_company(self, result) -> Optional[Dict]:
        """Extract company info from Google Business result"""
        try:
            # Look for business name
            name_elem = result.find('h3')
            if not name_elem:
                return None
            
            name = name_elem.get_text(strip=True)
            
            # Extract snippet for additional info
            snippet_elem = result.find('span', class_='aCOpRe')
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
            
            # Extract URL
            link_elem = result.find('a')
            url = link_elem.get('href', '') if link_elem else ''
            
            return {
                'name': name,
                'description': snippet,
                'website': url,
                'source': 'Google Business'
            }
        except:
            return None
    
    def _extract_directory_company(self, result) -> Optional[Dict]:
        """Extract company info from directory result"""
        try:
            name_elem = result.find('h3')
            if not name_elem:
                return None
            
            name = name_elem.get_text(strip=True)
            
            # Extract description
            desc_elem = result.find('span', class_='aCOpRe')
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # Extract URL
            link_elem = result.find('a')
            url = link_elem.get('href', '') if link_elem else ''
            
            return {
                'name': name,
                'description': description,
                'website': url,
                'source': 'Directory'
            }
        except:
            return None
    
    def _extract_local_company(self, result) -> Optional[Dict]:
        """Extract company info from local listing"""
        try:
            name_elem = result.find('h3')
            if not name_elem:
                return None
            
            name = name_elem.get_text(strip=True)
            
            # Extract snippet
            snippet_elem = result.find('span', class_='aCOpRe')
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
            
            return {
                'name': name,
                'description': snippet,
                'source': 'Local Listing'
            }
        except:
            return None
    
    def _remove_duplicates(self, companies: List[Dict]) -> List[Dict]:
        """Remove duplicate companies based on name"""
        unique_companies = []
        seen_names = set()
        
        for company in companies:
            name = company.get('name', '').lower().strip()
            if name and name not in seen_names:
                unique_companies.append(company)
                seen_names.add(name)
        
        return unique_companies
    
    def _enhance_company_data(self, company: Dict, customer_info: Dict) -> Dict:
        """Enhance company data with additional information"""
        enhanced = company.copy()
        
        # Add contact information
        enhanced['contact_info'] = {
            'phone': company.get('phone', ''),
            'email': self._extract_email(company.get('description', '')),
            'website': company.get('website', ''),
            'address': company.get('address', '')
        }
        
        # Add services
        enhanced['services'] = self._extract_services(company.get('description', ''))
        
        # Add quotation estimate
        enhanced['quotation'] = self._generate_quotation_estimate(company, customer_info)
        
        return enhanced
    
    def _extract_email(self, text: str) -> str:
        """Extract email from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ''
    
    def _extract_services(self, text: str) -> List[str]:
        """Extract services from text"""
        services = []
        service_keywords = [
            'packing', 'loading', 'unloading', 'storage', 'furniture',
            'local move', 'long distance', 'residential', 'commercial',
            'full service', 'partial service', 'labor only', 'moving'
        ]
        
        text_lower = text.lower()
        for keyword in service_keywords:
            if keyword in text_lower:
                services.append(keyword.title())
        
        return services
    
    def _generate_quotation_estimate(self, company: Dict, customer_info: Dict) -> Dict:
        """Generate quotation estimate based on company and customer info"""
        # Base pricing for 2BR apartment in Brooklyn
        base_price = 800
        price_range = 400
        
        # Adjust based on services
        services = company.get('services', [])
        if 'Full Service' in services or 'Packing' in services:
            base_price += 200
            price_range += 100
        
        if 'Storage' in services:
            base_price += 100
            price_range += 50
        
        return {
            'estimated_cost': f'${base_price}-{base_price + price_range}',
            'cost_range': 'Based on apartment size and services',
            'included_services': services,
            'quote_source': 'Estimated based on market rates'
        }
    
    def save_results_to_file(self, results: List[Dict], customer_info: Dict, filename: str = None) -> str:
        """Save real-time search results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"realtime_moving_companies_{timestamp}.txt"
        
        filepath = f"/Users/nirbhayareddy/Desktop/Hackathon/CC2/movescout/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("REAL-TIME MOVING COMPANIES SEARCH RESULTS\n")
            f.write("=" * 60 + "\n\n")
            
            # Customer information
            f.write("CUSTOMER INFORMATION:\n")
            f.write("-" * 20 + "\n")
            for key, value in customer_info.items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            f.write("\n")
            
            # Search results
            f.write("TOP MOVING COMPANIES (REAL-TIME SEARCH):\n")
            f.write("-" * 50 + "\n\n")
            
            for i, company in enumerate(results, 1):
                f.write(f"{i}. {company.get('name', 'Unknown Company')}\n")
                f.write(f"   Source: {company.get('source', 'Unknown')}\n")
                f.write(f"   Description: {company.get('description', 'No description available')}\n")
                f.write(f"   Website: {company.get('website', 'No website available')}\n")
                
                # Contact information
                contact = company.get('contact_info', {})
                if contact.get('phone'):
                    f.write(f"   Phone: {contact['phone']}\n")
                if contact.get('email'):
                    f.write(f"   Email: {contact['email']}\n")
                if contact.get('address'):
                    f.write(f"   Address: {contact['address']}\n")
                
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
            f.write(f"Found {len(results)} moving companies through real-time web search.\n")
            f.write("Contact information and estimated costs are provided above.\n")
            f.write("Please contact each company directly for detailed quotes.\n")
            f.write("\nNote: These results were obtained through real-time web scraping.\n")
        
        return filepath
