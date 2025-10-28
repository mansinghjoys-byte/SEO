"""
Competitor Discovery Service
Identifies competitors using web scraping, Exa.ai, and social media APIs
"""
from typing import Dict, List, Any, Optional
import logging
import asyncio
from datetime import datetime
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from exa_py import Exa
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CompetitorDiscoveryService:
    """Service for discovering and analyzing competitors"""
    
    def __init__(self):
        self.exa_client = Exa(api_key=settings.EXA_API_KEY) if settings.EXA_API_KEY else None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def discover_competitors(
        self,
        site_url: str,
        keywords: List[str],
        industry: Optional[str] = None,
        max_competitors: int = 20
    ) -> Dict[str, Any]:
        """
        Discover competitors using multiple methods
        """
        try:
            domain = self._extract_domain(site_url)
            all_competitors = []
            
            # Method 1: Search engine scraping (Google)
            logger.info(f"Discovering competitors via search engines for {domain}")
            search_competitors = await self._discover_via_search_engines(keywords, domain)
            all_competitors.extend(search_competitors)
            
            # Method 2: Exa.ai semantic search
            if self.exa_client and keywords:
                logger.info(f"Discovering competitors via Exa.ai for {domain}")
                exa_competitors = await self._discover_via_exa(site_url, keywords, industry)
                all_competitors.extend(exa_competitors)
            
            # Method 3: Similar content discovery
            logger.info(f"Discovering competitors via similar content for {domain}")
            content_competitors = await self._discover_via_similar_content(site_url, domain)
            all_competitors.extend(content_competitors)
            
            # Deduplicate and rank competitors
            competitors = self._deduplicate_and_rank(all_competitors, domain, max_competitors)
            
            return {
                'success': True,
                'your_domain': domain,
                'total_found': len(competitors),
                'competitors': competitors,
                'discovery_methods_used': {
                    'search_engines': True,
                    'exa_ai': self.exa_client is not None,
                    'similar_content': True
                },
                'discovered_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f'Competitor discovery error: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    async def _discover_via_search_engines(
        self,
        keywords: List[str],
        exclude_domain: str
    ) -> List[Dict[str, Any]]:
        """
        Discover competitors via Google search scraping
        """
        competitors = []
        
        try:
            # Use primary keywords for search
            for keyword in keywords[:3]:  # Top 3 keywords
                search_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}"
                
                try:
                    response = requests.get(search_url, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract search results
                        results = soup.find_all('div', class_='g')
                        for result in results[:10]:  # Top 10 results
                            link_elem = result.find('a')
                            if link_elem and 'href' in link_elem.attrs:
                                url = link_elem['href']
                                domain = self._extract_domain(url)
                                
                                # Skip own domain and common sites
                                if domain and domain != exclude_domain and not self._is_common_site(domain):
                                    title = result.find('h3')
                                    competitors.append({
                                        'domain': domain,
                                        'url': f"https://{domain}",
                                        'title': title.get_text() if title else domain,
                                        'keyword': keyword,
                                        'source': 'google_search',
                                        'relevance_score': 90 - (len(competitors) * 2)  # Higher for top results
                                    })
                    
                    # Rate limiting
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.warning(f'Search scraping error for keyword "{keyword}": {str(e)}')
                    continue
        
        except Exception as e:
            logger.error(f'Search engine discovery error: {str(e)}')
        
        return competitors
    
    async def _discover_via_exa(
        self,
        site_url: str,
        keywords: List[str],
        industry: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Discover competitors using Exa.ai semantic search
        """
        competitors = []
        
        if not self.exa_client:
            return competitors
        
        try:
            # Build search query
            query_parts = []
            if industry:
                query_parts.append(f"{industry} companies")
            if keywords:
                query_parts.append(f"focusing on {', '.join(keywords[:3])}")
            
            query = " ".join(query_parts) or f"websites similar to {site_url}"
            
            # Search with Exa
            results = self.exa_client.search_and_contents(
                query,
                num_results=15,
                use_autoprompt=True,
                category="company"
            )
            
            domain = self._extract_domain(site_url)
            
            for result in results.results:
                result_domain = self._extract_domain(result.url)
                
                # Skip own domain and common sites
                if result_domain and result_domain != domain and not self._is_common_site(result_domain):
                    competitors.append({
                        'domain': result_domain,
                        'url': result.url,
                        'title': result.title or result_domain,
                        'snippet': result.text[:200] if hasattr(result, 'text') else '',
                        'source': 'exa_ai',
                        'relevance_score': int(result.score * 100) if hasattr(result, 'score') else 75
                    })
        
        except Exception as e:
            logger.error(f'Exa.ai discovery error: {str(e)}')
        
        return competitors
    
    async def _discover_via_similar_content(
        self,
        site_url: str,
        domain: str
    ) -> List[Dict[str, Any]]:
        """
        Discover competitors by finding similar websites
        """
        competitors = []
        
        try:
            # Use Exa's find_similar if available
            if self.exa_client:
                try:
                    results = self.exa_client.find_similar(
                        site_url,
                        num_results=10,
                        category="company"
                    )
                    
                    for result in results.results:
                        result_domain = self._extract_domain(result.url)
                        
                        if result_domain and result_domain != domain and not self._is_common_site(result_domain):
                            competitors.append({
                                'domain': result_domain,
                                'url': result.url,
                                'title': result.title or result_domain,
                                'source': 'similar_content',
                                'relevance_score': int(result.score * 100) if hasattr(result, 'score') else 70
                            })
                
                except Exception as e:
                    logger.warning(f'Exa find_similar error: {str(e)}')
        
        except Exception as e:
            logger.error(f'Similar content discovery error: {str(e)}')
        
        return competitors
    
    def _deduplicate_and_rank(
        self,
        competitors: List[Dict[str, Any]],
        exclude_domain: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Deduplicate competitors and rank by relevance
        """
        # Deduplicate by domain
        seen_domains = set()
        unique_competitors = []
        
        for comp in competitors:
            domain = comp.get('domain', '')
            if domain and domain not in seen_domains and domain != exclude_domain:
                seen_domains.add(domain)
                unique_competitors.append(comp)
        
        # Sort by relevance score
        unique_competitors.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Return top N
        return unique_competitors[:max_results]
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            if not url:
                return ''
            
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            
            # Remove www.
            domain = re.sub(r'^www\.', '', domain)
            
            # Remove path
            domain = domain.split('/')[0]
            
            return domain.lower()
        
        except Exception:
            return ''
    
    def _is_common_site(self, domain: str) -> bool:
        """Check if domain is a common non-competitor site"""
        common_sites = {
            'google.com', 'facebook.com', 'twitter.com', 'linkedin.com',
            'youtube.com', 'instagram.com', 'wikipedia.org', 'amazon.com',
            'reddit.com', 'quora.com', 'medium.com', 'github.com',
            'stackoverflow.com', 'pinterest.com'
        }
        
        return domain in common_sites
    
    async def get_competitor_details(
        self,
        competitor_domain: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific competitor
        """
        try:
            url = f"https://{competitor_domain}"
            
            # Basic web scraping for details
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract meta information
                title = soup.find('title')
                description = soup.find('meta', attrs={'name': 'description'})
                
                # Try to estimate technology stack
                tech_stack = self._detect_technology(soup, response)
                
                return {
                    'success': True,
                    'domain': competitor_domain,
                    'url': url,
                    'title': title.get_text() if title else '',
                    'description': description['content'] if description and 'content' in description.attrs else '',
                    'technology_stack': tech_stack,
                    'analyzed_at': datetime.utcnow().isoformat()
                }
            
            return {
                'success': False,
                'domain': competitor_domain,
                'error': f'HTTP {response.status_code}'
            }
        
        except Exception as e:
            logger.error(f'Competitor details error: {str(e)}')
            return {'success': False, 'domain': competitor_domain, 'error': str(e)}
    
    def _detect_technology(self, soup: BeautifulSoup, response) -> List[str]:
        """Detect technology stack from HTML"""
        technologies = []
        
        html = str(soup)
        headers = dict(response.headers)
        
        # Check for common frameworks
        if 'react' in html.lower() or 'react' in headers.get('X-Powered-By', '').lower():
            technologies.append('React')
        
        if 'vue' in html.lower():
            technologies.append('Vue.js')
        
        if 'angular' in html.lower():
            technologies.append('Angular')
        
        if 'next' in html.lower():
            technologies.append('Next.js')
        
        if 'wordpress' in html.lower():
            technologies.append('WordPress')
        
        if 'shopify' in html.lower():
            technologies.append('Shopify')
        
        # Check server headers
        server = headers.get('Server', '')
        if 'nginx' in server.lower():
            technologies.append('Nginx')
        if 'apache' in server.lower():
            technologies.append('Apache')
        
        return technologies if technologies else ['Unknown']
