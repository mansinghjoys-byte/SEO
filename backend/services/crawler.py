import httpx
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, urljoin
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WebCrawler:
    """Real web crawler with comprehensive analysis"""
    
    def __init__(self, user_agent: str = None):
        self.user_agent = user_agent or 'RankForge-SEO-Bot/1.0'
        self.timeout = 15.0
    
    async def crawl_and_analyze(self, url: str) -> Dict[str, Any]:
        """Crawl a URL and perform comprehensive SEO analysis"""
        logger.info(f'Crawling: {url}')
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(
                    url,
                    headers={'User-Agent': self.user_agent}
                )
                
                if response.status_code != 200:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}',
                        'url': url
                    }
                
                html_content = response.text
                final_url = str(response.url)
                load_time = response.elapsed.total_seconds()
                
                # Parse HTML
                soup = BeautifulSoup(html_content, 'lxml')
                
                # Perform analysis
                analysis = {
                    'success': True,
                    'url': final_url,
                    'load_time': load_time,
                    'status_code': response.status_code,
                    'content_length': len(html_content),
                    'technical': self._analyze_technical(soup, response, final_url),
                    'content': self._analyze_content(soup, html_content),
                    'meta': self._analyze_meta(soup),
                    'images': self._analyze_images(soup, final_url),
                    'links': self._analyze_links(soup, final_url),
                    'performance': self._analyze_performance(html_content, load_time),
                    'mobile': self._analyze_mobile(soup),
                    'structured_data': self._analyze_structured_data(soup),
                    'crawled_at': datetime.utcnow().isoformat()
                }
                
                return analysis
                
        except httpx.TimeoutException:
            return {'success': False, 'error': 'Request timeout', 'url': url}
        except httpx.RequestError as e:
            return {'success': False, 'error': str(e), 'url': url}
        except Exception as e:
            logger.error(f'Crawl error for {url}: {str(e)}')
            return {'success': False, 'error': f'Crawl failed: {str(e)}', 'url': url}
    
    def _analyze_technical(self, soup: BeautifulSoup, response, url: str) -> Dict:
        """Analyze technical SEO factors"""
        parsed_url = urlparse(url)
        
        return {
            'https': url.startswith('https://'),
            'www_redirect': parsed_url.netloc.startswith('www.'),
            'has_robots_meta': bool(soup.find('meta', attrs={'name': 'robots'})),
            'has_canonical': bool(soup.find('link', rel='canonical')),
            'canonical_url': soup.find('link', rel='canonical')['href'] if soup.find('link', rel='canonical') else None,
            'has_sitemap_reference': bool(soup.find('link', attrs={'type': 'application/xml'})),
            'headers': dict(response.headers),
            'redirects': len(response.history),
            'content_type': response.headers.get('content-type', '')
        }
    
    def _analyze_content(self, soup: BeautifulSoup, html: str) -> Dict:
        """Analyze on-page content"""
        # Extract text content
        text_content = soup.get_text(separator=' ', strip=True)
        words = text_content.split()
        
        # Headings
        h1_tags = soup.find_all('h1')
        h2_tags = soup.find_all('h2')
        h3_tags = soup.find_all('h3')
        
        # Paragraphs
        paragraphs = soup.find_all('p')
        
        return {
            'word_count': len(words),
            'character_count': len(text_content),
            'h1_count': len(h1_tags),
            'h1_text': [h1.get_text(strip=True) for h1 in h1_tags],
            'h2_count': len(h2_tags),
            'h3_count': len(h3_tags),
            'paragraph_count': len(paragraphs),
            'has_heading_structure': len(h1_tags) > 0 and len(h2_tags) > 0,
            'main_content_length': sum(len(p.get_text(strip=True)) for p in paragraphs)
        }
    
    def _analyze_meta(self, soup: BeautifulSoup) -> Dict:
        """Analyze meta tags"""
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else ''
        
        description = soup.find('meta', attrs={'name': 'description'})
        description_text = description['content'] if description and description.get('content') else ''
        
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        keywords_text = keywords['content'] if keywords and keywords.get('content') else ''
        
        # Open Graph
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        og_image = soup.find('meta', property='og:image')
        
        # Twitter Card
        twitter_card = soup.find('meta', attrs={'name': 'twitter:card'})
        
        return {
            'title': title_text,
            'title_length': len(title_text),
            'has_title': bool(title_text),
            'description': description_text,
            'description_length': len(description_text),
            'has_description': bool(description_text),
            'keywords': keywords_text,
            'has_keywords': bool(keywords_text),
            'has_og_tags': bool(og_title or og_description or og_image),
            'og_title': og_title['content'] if og_title and og_title.get('content') else None,
            'og_description': og_description['content'] if og_description and og_description.get('content') else None,
            'og_image': og_image['content'] if og_image and og_image.get('content') else None,
            'has_twitter_card': bool(twitter_card)
        }
    
    def _analyze_images(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Analyze images on page"""
        images = soup.find_all('img')
        
        images_without_alt = [img for img in images if not img.get('alt')]
        images_with_empty_alt = [img for img in images if img.get('alt') == '']
        
        return {
            'total_images': len(images),
            'images_without_alt': len(images_without_alt),
            'images_with_empty_alt': len(images_with_empty_alt),
            'images_with_alt': len(images) - len(images_without_alt),
            'alt_percentage': ((len(images) - len(images_without_alt)) / len(images) * 100) if images else 100
        }
    
    def _analyze_links(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Analyze links on page"""
        all_links = soup.find_all('a', href=True)
        
        internal_links = []
        external_links = []
        broken_links = []
        
        parsed_base = urlparse(base_url)
        
        for link in all_links:
            href = link['href']
            
            # Resolve relative URLs
            absolute_url = urljoin(base_url, href)
            parsed_link = urlparse(absolute_url)
            
            if parsed_link.netloc == parsed_base.netloc:
                internal_links.append(href)
            elif parsed_link.scheme in ['http', 'https']:
                external_links.append(href)
        
        return {
            'total_links': len(all_links),
            'internal_links': len(internal_links),
            'external_links': len(external_links),
            'nofollow_links': len(soup.find_all('a', rel='nofollow'))
        }
    
    def _analyze_performance(self, html: str, load_time: float) -> Dict:
        """Analyze performance metrics"""
        html_size_kb = len(html.encode('utf-8')) / 1024
        
        return {
            'load_time_seconds': round(load_time, 2),
            'html_size_kb': round(html_size_kb, 2),
            'is_fast': load_time < 2.0,
            'is_optimal_size': html_size_kb < 100
        }
    
    def _analyze_mobile(self, soup: BeautifulSoup) -> Dict:
        """Analyze mobile-friendliness"""
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        viewport_content = viewport['content'] if viewport and viewport.get('content') else ''
        
        return {
            'has_viewport': bool(viewport),
            'viewport_content': viewport_content,
            'is_responsive': 'width=device-width' in viewport_content.lower() if viewport_content else False
        }
    
    def _analyze_structured_data(self, soup: BeautifulSoup) -> Dict:
        """Analyze structured data (Schema.org)"""
        json_ld = soup.find_all('script', type='application/ld+json')
        microdata = soup.find_all(attrs={'itemtype': True})
        
        return {
            'has_json_ld': len(json_ld) > 0,
            'json_ld_count': len(json_ld),
            'has_microdata': len(microdata) > 0,
            'microdata_count': len(microdata)
        }
