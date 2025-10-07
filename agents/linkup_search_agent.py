import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from linkup import LinkupClient
from .config import Config

# Load environment variables from .env file
load_dotenv()

class LinkUpSearchAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("LINKUP_API_KEY")
        if not self.api_key:
            raise ValueError("LinkUp API key is required. Set LINKUP_API_KEY environment variable or pass api_key parameter.")
        self.client = LinkupClient(api_key=self.api_key)
    
    def search_moving_companies(self, customer_info: Dict) -> List[Dict]:
        """
        Search for moving companies based on customer information using LinkUp API
        """
        # Extract key information for search
        origin = customer_info.get('current_address', '')
        destination = customer_info.get('destination_address', '')
        move_date = customer_info.get('move_out_date', '')
        apartment_size = customer_info.get('apartment_size', '')
        
        # Create multiple search queries to try
        search_queries = [
            f"moving companies from {origin} to {destination}",
            f"movers {origin} to {destination}",
            f"moving services Brooklyn New York",
            f"local movers Brooklyn",
            f"moving companies near {origin}"
        ]
        
        all_companies = []
        
        for search_query in search_queries:
            print(f"Searching for: {search_query}")
            
            try:
                # Use LinkUp to search for moving companies
                response = self.client.search(
                    query=search_query,
                    depth="deep",  # Use "deep" depth for comprehensive results
                    output_type="sourcedAnswer"
                )
                
                print(f"LinkUp response received: {type(response)}")
                
                # Handle the response object properly
                if hasattr(response, 'sources'):
                    sources = response.sources
                    print(f"Sources found: {len(sources) if sources else 0}")
                elif hasattr(response, 'answer'):
                    print(f"Answer received: {response.answer[:100]}...")
                
                # Extract moving companies from the response
                moving_companies = self._extract_moving_companies(response)
                print(f"Extracted {len(moving_companies)} companies from this query")
                
                all_companies.extend(moving_companies)
                
                # If we have enough companies, break
                if len(all_companies) >= 5:
                    break
                    
            except Exception as e:
                print(f"Error with query '{search_query}': {e}")
                continue
        
        # Remove duplicates and filter out non-companies
        unique_companies = []
        seen_names = set()
        
        for company in all_companies:
            name = company.get('name', '').lower()
            # Filter out non-moving companies
            if (name and name not in seen_names and 
                not any(word in name for word in ['reddit', 'yelp', 'chamber', 'library', 'mosque', 'encyclopedia', 'apartments', 'street', 'atlantic', 'franklin', 'housing', 'people search', 'strolling', 'aloft']) and
                any(word in name for word in ['moving', 'movers', 'storage', 'cake', 'metropolis', 'imperial', 'dumbo', 'gentle', 'urban', 'liffey', 'flatrate', 'elate', 'sven', 'expo', 'eq', 'intense', 'cool', 'zeromax', 'solidarity', 'great', 'sweet', 'perfect', 'optimum', 'vector'])):
                unique_companies.append(company)
                seen_names.add(name)
        
        print(f"Total unique moving companies found: {len(unique_companies)}")
        
        # Get top 5 results
        top_5_companies = unique_companies[:5]
        
        # Get quotations for each company
        companies_with_quotes = []
        for company in top_5_companies:
            company_with_quote = self._get_company_quotation(company, customer_info)
            companies_with_quotes.append(company_with_quote)
        
        return companies_with_quotes
    
    def _extract_moving_companies(self, response) -> List[Dict]:
        """
        Extract moving company information from LinkUp response
        """
        companies = []
        
        print(f"Response type: {type(response)}")
        
        # Handle response object attributes
        if hasattr(response, 'sources') and response.sources:
            print(f"Found {len(response.sources)} sources")
            for i, source in enumerate(response.sources):
                # Handle source object attributes
                name = getattr(source, 'name', 'No name') if hasattr(source, 'name') else 'No name'
                url = getattr(source, 'url', '') if hasattr(source, 'url') else ''
                snippet = getattr(source, 'snippet', '') if hasattr(source, 'snippet') else ''
                
                # Extract actual company name from snippet or name
                actual_company_name = self._extract_company_name(name, snippet)
                
                print(f"Source {i+1}: {name} -> {actual_company_name}")
                company_info = {
                    'name': actual_company_name,
                    'original_name': name,
                    'url': url,
                    'snippet': snippet,
                    'description': snippet,
                    'contact_info': self._extract_contact_info(snippet),
                    'services': self._extract_services(snippet)
                }
                companies.append(company_info)
        elif hasattr(response, 'answer') and response.answer:
            print("Trying to extract from answer field")
            # Create a company from the answer
            company_info = {
                'name': 'Moving Company (from search results)',
                'url': '',
                'snippet': response.answer,
                'description': response.answer,
                'contact_info': self._extract_contact_info(response.answer),
                'services': self._extract_services(response.answer)
            }
            companies.append(company_info)
        else:
            print("No sources or answer found in response")
        
        return companies
    
    def _extract_company_name(self, title: str, snippet: str) -> str:
        """
        Extract actual company name from title and snippet
        """
        import re
        
        # Known moving company names to look for
        known_companies = [
            'Metropolis Moving', 'Piece of Cake Moving & Storage', 'Imperial Moving & Storage', 'Dumbo Moving & Storage',
            'Movers Not Shakers', 'JP Urban Moving', 'Gentle Giant Moving', 'FlatRate Moving',
            'Oz Moving', 'Elate Moving', 'Liffey Van Lines', 'Northeastern Movers',
            'Sven Moving', 'Expo Movers', 'EQ Movers', 'Intense Movers', 'Cool Hand Movers',
            'ZeroMax Moving', 'Solidarity Movers', 'Great Movers', 'Sweet Lou Moves',
            'Perfect Moving', 'Optimum Moving', 'Vector Movers', 'Man With A Van',
            'NYC Great Movers', 'Imperial Moving', 'Dumbo Moving'
        ]
        
        # First, try to find known company names in the snippet
        for company in known_companies:
            if company.lower() in snippet.lower():
                return company
        
        # Look for specific company patterns in snippet
        company_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Moving\s+&?\s*Storage|Moving\s+Company)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Moving',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Movers',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+&',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Storage'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, snippet)
            if matches:
                # Return the first match that looks like a company name
                for match in matches:
                    if (len(match.split()) <= 4 and 
                        not any(word in match.lower() for word in ['best', 'top', 'local', 'brooklyn', 'nyc', 'new york', 'great', 'cheap', 'affordable']) and
                        any(word in match.lower() for word in ['moving', 'movers', 'storage'])):
                        return match.strip()
        
        # If no company name found, try to extract from title
        if '|' in title:
            # Split by | and take the part that looks like a company name
            parts = title.split('|')
            for part in parts:
                part = part.strip()
                if (any(word in part.lower() for word in ['moving', 'movers', 'storage']) and 
                    not any(word in part.lower() for word in ['best', 'top', 'local', 'brooklyn', 'nyc', 'new york', 'great', 'cheap', 'affordable'])):
                    return part
        
        # Look for company names in the title
        title_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Moving\s+&?\s*Storage|Moving\s+Company)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Moving',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Movers',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+&',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Storage'
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, title)
            if matches:
                for match in matches:
                    if (not any(word in match.lower() for word in ['best', 'top', 'local', 'brooklyn', 'nyc', 'new york', 'great', 'cheap', 'affordable']) and
                        any(word in match.lower() for word in ['moving', 'movers', 'storage'])):
                        return match.strip()
        
        # If all else fails, return a cleaned version of the title
        cleaned_title = title.replace('|', ' - ').replace('⭐', '').strip()
        if len(cleaned_title) > 50:
            cleaned_title = cleaned_title[:50] + '...'
        
        return cleaned_title
    
    def _extract_contact_info(self, text: str) -> Dict:
        """
        Extract contact information from text with enhanced phone number detection
        """
        import re
        
        contact_info = {
            'phone': '',
            'email': '',
            'website': '',
            'all_phones': []
        }
        
        # Enhanced phone number patterns for better detection
        phone_patterns = [
            r'(\+?1?[-.\s]?)?(\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})',  # Standard US format
            r'\([0-9]{3}\)\s?[0-9]{3}-[0-9]{4}',  # (XXX) XXX-XXXX
            r'[0-9]{3}-[0-9]{3}-[0-9]{4}',  # XXX-XXX-XXXX
            r'[0-9]{3}\.[0-9]{3}\.[0-9]{4}',  # XXX.XXX.XXXX
            r'[0-9]{3}\s[0-9]{3}\s[0-9]{4}',  # XXX XXX XXXX
            r'\+1\s?[0-9]{3}\s?[0-9]{3}\s?[0-9]{4}',  # +1 XXX XXX XXXX
            r'Call\s+([0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})',  # "Call XXX-XXX-XXXX"
            r'Phone:\s*([0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})',  # "Phone: XXX-XXX-XXXX"
            r'Tel:\s*([0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})',  # "Tel: XXX-XXX-XXXX"
        ]
        
        all_phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    phone = ''.join(match)
                else:
                    phone = match
                # Clean up the phone number
                phone = re.sub(r'[^\d+]', '', phone)
                if len(phone) >= 10:  # Valid phone number length
                    all_phones.append(phone)
        
        # Remove duplicates and get the first valid phone
        unique_phones = list(dict.fromkeys(all_phones))
        contact_info['all_phones'] = unique_phones
        if unique_phones:
            contact_info['phone'] = unique_phones[0]
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group(0)
        
        # Extract website
        website_patterns = [
            r'https?://[^\s]+',
            r'www\.[^\s]+',
            r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?'
        ]
        
        for pattern in website_patterns:
            website_match = re.search(pattern, text)
            if website_match:
                website = website_match.group(0)
                if not website.startswith('http'):
                    website = 'https://' + website
                contact_info['website'] = website
                break
        
        return contact_info
    
    def _extract_services(self, text: str) -> List[str]:
        """
        Extract services offered from text
        """
        services = []
        service_keywords = [
            'packing', 'loading', 'unloading', 'storage', 'furniture', 
            'local move', 'long distance', 'residential', 'commercial',
            'full service', 'partial service', 'labor only'
        ]
        
        text_lower = text.lower()
        for keyword in service_keywords:
            if keyword in text_lower:
                services.append(keyword.title())
        
        return services
    
    def _get_company_quotation(self, company: Dict, customer_info: Dict) -> Dict:
        """
        Get quotation and contact information for a specific company
        """
        company_name = company.get('name', '')
        origin = customer_info.get('current_address', '')
        destination = customer_info.get('destination_address', '')
        
        # Search for contact information first
        contact_queries = [
            f"{company_name} phone number contact information",
            f"{company_name} Brooklyn movers contact",
            f"{company_name} moving company phone",
            f"call {company_name} Brooklyn"
        ]
        
        enhanced_contact_info = company.get('contact_info', {})
        
        for contact_query in contact_queries:
            try:
                print(f"Searching for contact: {contact_query}")
                contact_response = self.client.search(
                    query=contact_query,
                    depth="deep",
                    output_type="sourcedAnswer"
                )
                
                # Extract contact info from response
                if hasattr(contact_response, 'answer') and contact_response.answer:
                    new_contact_info = self._extract_contact_info(contact_response.answer)
                    # Merge contact information
                    if new_contact_info.get('phone') and not enhanced_contact_info.get('phone'):
                        enhanced_contact_info['phone'] = new_contact_info['phone']
                    if new_contact_info.get('all_phones'):
                        enhanced_contact_info['all_phones'] = list(set(enhanced_contact_info.get('all_phones', []) + new_contact_info['all_phones']))
                    if new_contact_info.get('email') and not enhanced_contact_info.get('email'):
                        enhanced_contact_info['email'] = new_contact_info['email']
                    if new_contact_info.get('website') and not enhanced_contact_info.get('website'):
                        enhanced_contact_info['website'] = new_contact_info['website']
                
                # Also check sources for contact info
                if hasattr(contact_response, 'sources') and contact_response.sources:
                    for source in contact_response.sources:
                        snippet = getattr(source, 'snippet', '')
                        if snippet:
                            new_contact_info = self._extract_contact_info(snippet)
                            if new_contact_info.get('phone') and not enhanced_contact_info.get('phone'):
                                enhanced_contact_info['phone'] = new_contact_info['phone']
                            if new_contact_info.get('all_phones'):
                                enhanced_contact_info['all_phones'] = list(set(enhanced_contact_info.get('all_phones', []) + new_contact_info['all_phones']))
                            if new_contact_info.get('email') and not enhanced_contact_info.get('email'):
                                enhanced_contact_info['email'] = new_contact_info['email']
                            if new_contact_info.get('website') and not enhanced_contact_info.get('website'):
                                enhanced_contact_info['website'] = new_contact_info['website']
                
                # If we found contact info, we can stop searching
                if enhanced_contact_info.get('phone'):
                    break
                    
            except Exception as e:
                print(f"Error searching contact for {company_name}: {e}")
                continue
        
        # Update company with enhanced contact info
        company['contact_info'] = enhanced_contact_info
        
        # Now get quotation information
        quote_query = f"{company_name} moving quote estimate from {origin} to {destination}"
        
        try:
            quote_response = self.client.search(
                query=quote_query,
                depth="deep",
                output_type="sourcedAnswer"
            )
            
            # Extract pricing information
            pricing_info = self._extract_pricing_info(quote_response)
            
            # Get quote source URL
            quote_source = ''
            if hasattr(quote_response, 'sources') and quote_response.sources:
                first_source = quote_response.sources[0]
                if hasattr(first_source, 'url'):
                    quote_source = first_source.url
            
            company['quotation'] = {
                'estimated_cost': pricing_info.get('cost', 'Contact for quote'),
                'cost_range': pricing_info.get('range', ''),
                'included_services': pricing_info.get('services', []),
                'additional_fees': pricing_info.get('fees', []),
                'quote_source': quote_source
            }
            
        except Exception as e:
            print(f"Error getting quotation for {company_name}: {e}")
            company['quotation'] = {
                'estimated_cost': 'Contact for quote',
                'cost_range': '',
                'included_services': [],
                'additional_fees': [],
                'quote_source': ''
            }
        
        return company
    
    def _extract_pricing_info(self, response) -> Dict:
        """
        Extract pricing information from LinkUp response
        """
        pricing_info = {
            'cost': '',
            'range': '',
            'services': [],
            'fees': []
        }
        
        # Handle LinkUp response object
        if hasattr(response, 'answer') and response.answer:
            answer = response.answer
            
            # Look for price patterns
            import re
            price_patterns = [
                r'\$[\d,]+(?:\.\d{2})?',
                r'[\d,]+(?:\.\d{2})?\s*dollars?',
                r'starting at \$[\d,]+',
                r'from \$[\d,]+',
                r'estimate.*?\$[\d,]+',
                r'quote.*?\$[\d,]+'
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, answer, re.IGNORECASE)
                if matches:
                    pricing_info['cost'] = matches[0]
                    break
            
            # If no specific price found, look for price ranges
            if not pricing_info['cost']:
                range_patterns = [
                    r'\$[\d,]+-\$[\d,]+',
                    r'\$[\d,]+ to \$[\d,]+',
                    r'between \$[\d,]+ and \$[\d,]+'
                ]
                
                for pattern in range_patterns:
                    matches = re.findall(pattern, answer, re.IGNORECASE)
                    if matches:
                        pricing_info['cost'] = matches[0]
                        break
        
        return pricing_info
    
    def save_results_to_file(self, results: List[Dict], customer_info: Dict, filename: str = None) -> str:
        """
        Save search results and summary to a text file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"moving_companies_search_{timestamp}.txt"
        
        filepath = f"/Users/nirbhayareddy/Desktop/Hackathon/CC2/movescout/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("MOVING COMPANIES SEARCH RESULTS\n")
            f.write("=" * 50 + "\n\n")
            
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
        
        return filepath

