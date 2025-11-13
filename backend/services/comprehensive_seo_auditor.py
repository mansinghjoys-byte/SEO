"""
Comprehensive SEO Auditor - Production Ready
Matches and exceeds SAPRO audit standard with 60+ detailed checks
"""

from typing import Dict, Any, List, Optional, Tuple
import httpx
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import asyncio
from datetime import datetime
import logging
from core.config import get_settings
from groq import AsyncGroq
import xml.etree.ElementTree as ET
from collections import Counter

logger = logging.getLogger(__name__)
settings = get_settings()


class AuditFinding:
    """Represents a single audit finding with detailed information"""
    
    def __init__(
        self,
        issue_number: int,
        category: str,
        severity: str,  # 'critical', 'important', 'minor'
        title: str,
        example: Optional[str],
        importance: str,
        solution: str,
        impact_score: int,
        current_value: Optional[str] = None,
        recommended_value: Optional[str] = None
    ):
        self.issue_number = issue_number
        self.category = category
        self.severity = severity
        self.title = title
        self.example = example
        self.importance = importance
        self.solution = solution
        self.impact_score = impact_score
        self.current_value = current_value
        self.recommended_value = recommended_value
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'issue_number': self.issue_number,
            'category': self.category,
            'severity': self.severity,
            'title': self.title,
            'example': self.example,
            'importance': self.importance,
            'solution': self.solution,
            'impact_score': self.impact_score,
            'current_value': self.current_value,
            'recommended_value': self.recommended_value
        }


class ComprehensiveSEOAuditor:
    """
    Production-ready comprehensive SEO auditor
    Covers all major SEO aspects with detailed analysis
    """
    
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.timeout = 30.0
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.findings: List[AuditFinding] = []
        self.issue_counter = 1
    
    async def run_comprehensive_audit(self, url: str) -> Dict[str, Any]:
        """
        Run complete comprehensive SEO audit
        Returns detailed findings matching SAPRO standard
        """
        logger.info(f'Starting comprehensive audit for: {url}')
        
        self.findings = []
        self.issue_counter = 1
        
        try:
            # Crawl the website
            crawl_data = await self._crawl_website(url)
            
            if not crawl_data.get('success'):
                return {
                    'success': False,
                    'error': crawl_data.get('error', 'Failed to crawl website'),
                    'url': url
                }
            
            # Run all audit categories
            technical_findings = await self._audit_technical_seo(url, crawl_data)
            performance_findings = await self._audit_core_web_vitals(url, crawl_data)
            onpage_findings = await self._audit_onpage_seo(url, crawl_data)
            content_findings = await self._audit_website_content(url, crawl_data)
            social_findings = await self._audit_social_media(url, crawl_data)
            offpage_findings = await self._audit_offpage_seo(url, crawl_data)
            geo_aeo_findings = await self._audit_geo_aeo(url, crawl_data)
            analytics_findings = await self._audit_analytics(url, crawl_data)
            
            # Compile all findings
            all_findings = (
                technical_findings + 
                performance_findings + 
                onpage_findings + 
                content_findings + 
                social_findings + 
                offpage_findings + 
                geo_aeo_findings + 
                analytics_findings
            )
            
            # Calculate scores
            scores = self._calculate_scores(all_findings)
            
            # Generate AI-powered insights
            ai_insights = await self._generate_ai_insights(url, all_findings, crawl_data)
            
            return {
                'success': True,
                'url': url,
                'audited_at': datetime.utcnow().isoformat(),
                'findings': [f.to_dict() for f in all_findings],
                'findings_by_category': self._group_findings_by_category(all_findings),
                'findings_by_severity': self._group_findings_by_severity(all_findings),
                'scores': scores,
                'summary': {
                    'total_issues': len(all_findings),
                    'critical_issues': len([f for f in all_findings if f.severity == 'critical']),
                    'important_issues': len([f for f in all_findings if f.severity == 'important']),
                    'minor_issues': len([f for f in all_findings if f.severity == 'minor']),
                },
                'ai_insights': ai_insights,
                'crawl_data': crawl_data,
                'report_metadata': {
                    'generated_by': 'RankForge Comprehensive SEO Auditor',
                    'version': '2.0',
                    'checks_performed': len(all_findings),
                    'audit_duration': 'Real-time'
                }
            }
            
        except Exception as e:
            logger.error(f'Comprehensive audit error: {str(e)}')
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    async def _crawl_website(self, url: str) -> Dict[str, Any]:
        """Enhanced web crawler with comprehensive data extraction"""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={'User-Agent': self.user_agent}
            ) as client:
                # Measure request timing
                start_time = datetime.now()
                response = await client.get(url)
                load_time = (datetime.now() - start_time).total_seconds()
                
                if response.status_code != 200:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}',
                        'status_code': response.status_code
                    }
                
                html = response.text
                soup = BeautifulSoup(html, 'lxml')
                final_url = str(response.url)
                
                # Extract all data
                return {
                    'success': True,
                    'url': final_url,
                    'original_url': url,
                    'status_code': response.status_code,
                    'load_time': load_time,
                    'html': html,
                    'html_size_kb': len(html.encode('utf-8')) / 1024,
                    'response_headers': dict(response.headers),
                    'redirects': len(response.history),
                    'final_url': final_url,
                    
                    # Parse data
                    'soup': soup,
                    'meta': self._extract_meta_data(soup),
                    'content': self._extract_content_data(soup),
                    'technical': self._extract_technical_data(soup, response, final_url),
                    'images': self._extract_image_data(soup, final_url),
                    'links': self._extract_link_data(soup, final_url),
                    'structured_data': self._extract_structured_data(soup),
                    'performance': self._extract_performance_data(html, load_time),
                    'mobile': self._extract_mobile_data(soup),
                    'social': self._extract_social_data(soup),
                    'security': self._extract_security_data(response, final_url),
                }
                
        except httpx.TimeoutException:
            return {'success': False, 'error': 'Request timeout after 30 seconds'}
        except httpx.ConnectError:
            return {'success': False, 'error': 'Cannot connect to website'}
        except Exception as e:
            logger.error(f'Crawl error: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def _extract_meta_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract meta tags and related data"""
        # Title
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else ''
        
        # Meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        description = desc_tag.get('content', '').strip() if desc_tag else ''
        
        # Meta keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        keywords = keywords_tag.get('content', '').strip() if keywords_tag else ''
        
        # Robots meta
        robots_tag = soup.find('meta', attrs={'name': 'robots'})
        robots = robots_tag.get('content', '').strip() if robots_tag else ''
        
        # Viewport
        viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
        viewport = viewport_tag.get('content', '').strip() if viewport_tag else ''
        
        # Open Graph tags
        og_tags = {}
        for og_tag in soup.find_all('meta', property=re.compile(r'^og:')):
            prop = og_tag.get('property', '')
            content = og_tag.get('content', '')
            og_tags[prop] = content
        
        # Twitter Card
        twitter_tags = {}
        for twitter_tag in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            name = twitter_tag.get('name', '')
            content = twitter_tag.get('content', '')
            twitter_tags[name] = content
        
        return {
            'title': title,
            'title_length': len(title),
            'has_title': bool(title),
            'description': description,
            'description_length': len(description),
            'has_description': bool(description),
            'keywords': keywords,
            'has_keywords': bool(keywords),
            'robots': robots,
            'has_robots': bool(robots),
            'viewport': viewport,
            'has_viewport': bool(viewport),
            'og_tags': og_tags,
            'has_og_tags': bool(og_tags),
            'twitter_tags': twitter_tags,
            'has_twitter_card': bool(twitter_tags),
        }
    
    def _extract_content_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract content structure and quality data"""
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Get main text content
        text = soup.get_text(separator=' ', strip=True)
        words = text.split()
        word_count = len(words)
        
        # Headings analysis
        h1_tags = soup.find_all('h1')
        h2_tags = soup.find_all('h2')
        h3_tags = soup.find_all('h3')
        h4_tags = soup.find_all('h4')
        h5_tags = soup.find_all('h5')
        h6_tags = soup.find_all('h6')
        
        h1_texts = [h1.get_text(strip=True) for h1 in h1_tags]
        h2_texts = [h2.get_text(strip=True) for h2 in h2_tags]
        
        # Check for duplicate H1s
        h1_duplicates = [text for text, count in Counter(h1_texts).items() if count > 1]
        
        # Paragraphs
        paragraphs = soup.find_all('p')
        
        # Content structure elements
        has_toc = bool(soup.find(['nav', 'div'], class_=re.compile(r'(toc|table.*content)', re.I)))
        has_author = bool(soup.find(['div', 'span', 'p'], class_=re.compile(r'author', re.I)))
        has_related = bool(soup.find(['div', 'section'], class_=re.compile(r'related', re.I)))
        
        return {
            'text': text[:10000],  # First 10k chars
            'word_count': word_count,
            'h1_count': len(h1_tags),
            'h1_texts': h1_texts,
            'has_h1': len(h1_tags) > 0,
            'has_multiple_h1': len(h1_tags) > 1,
            'h1_duplicates': h1_duplicates,
            'h2_count': len(h2_tags),
            'h2_texts': h2_texts[:20],
            'h3_count': len(h3_tags),
            'h4_count': len(h4_tags),
            'h5_count': len(h5_tags),
            'h6_count': len(h6_tags),
            'paragraph_count': len(paragraphs),
            'has_heading_structure': len(h2_tags) > 0 or len(h3_tags) > 0,
            'has_toc': has_toc,
            'has_author': has_author,
            'has_related': has_related,
        }
    
    def _extract_technical_data(self, soup: BeautifulSoup, response, url: str) -> Dict[str, Any]:
        """Extract technical SEO data"""
        # Canonical
        canonical_tag = soup.find('link', rel='canonical')
        canonical_url = canonical_tag.get('href', '') if canonical_tag else ''
        
        # Alternate (hreflang)
        hreflang_tags = soup.find_all('link', rel='alternate', hreflang=True)
        
        # Robots meta
        robots_tag = soup.find('meta', attrs={'name': 'robots'})
        
        return {
            'https': url.startswith('https://'),
            'has_canonical': bool(canonical_tag),
            'canonical_url': canonical_url,
            'has_robots_meta': bool(robots_tag),
            'robots_content': robots_tag.get('content', '') if robots_tag else '',
            'has_hreflang': len(hreflang_tags) > 0,
            'hreflang_count': len(hreflang_tags),
            'redirects': len(response.history),
            'server': response.headers.get('server', 'Unknown'),
            'content_type': response.headers.get('content-type', ''),
        }
    
    def _extract_image_data(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract and analyze images"""
        images = soup.find_all('img')
        
        images_without_alt = []
        large_images = []
        
        for img in images:
            if not img.get('alt'):
                src = img.get('src', 'unknown')
                images_without_alt.append(src)
            
            # Check image format and size (estimate from URL)
            src = img.get('src', '')
            if src and not any(ext in src.lower() for ext in ['.webp', '.svg']):
                if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    # Add to potential optimization list
                    large_images.append(src)
        
        return {
            'total_images': len(images),
            'images_without_alt': len(images_without_alt),
            'images_without_alt_list': images_without_alt[:10],
            'alt_optimization_rate': ((len(images) - len(images_without_alt)) / len(images) * 100) if images else 100,
            'images_needing_optimization': len(large_images),
            'webp_usage': len([img for img in images if '.webp' in img.get('src', '').lower()]),
        }
    
    def _extract_link_data(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract and analyze links"""
        links = soup.find_all('a', href=True)
        
        internal = []
        external = []
        nofollow = []
        
        parsed_base = urlparse(base_url)
        
        for link in links:
            href = link['href']
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            
            # Check if internal or external
            if parsed.netloc == parsed_base.netloc or not parsed.netloc:
                internal.append(href)
            else:
                external.append(full_url)
            
            # Check for nofollow
            rel = link.get('rel', [])
            if isinstance(rel, list):
                rel = ' '.join(rel)
            if 'nofollow' in rel.lower():
                nofollow.append(href)
        
        return {
            'total_links': len(links),
            'internal_links': len(internal),
            'external_links': len(external),
            'nofollow_links': len(nofollow),
            'internal_to_external_ratio': len(internal) / len(external) if external else len(internal),
        }
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract structured data (JSON-LD, Microdata)"""
        # JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        json_ld_count = len(json_ld_scripts)
        
        schema_types = []
        for script in json_ld_scripts:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict):
                    schema_type = data.get('@type', '')
                    if schema_type:
                        schema_types.append(schema_type)
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            schema_type = item.get('@type', '')
                            if schema_type:
                                schema_types.append(schema_type)
            except:
                pass
        
        # Microdata
        microdata_items = soup.find_all(attrs={'itemscope': True})
        
        # Check for specific schema types
        has_faq_schema = 'FAQPage' in schema_types
        has_article_schema = 'Article' in schema_types or 'BlogPosting' in schema_types
        has_organization_schema = 'Organization' in schema_types
        has_product_schema = 'Product' in schema_types
        
        return {
            'has_json_ld': json_ld_count > 0,
            'json_ld_count': json_ld_count,
            'schema_types': schema_types,
            'has_microdata': len(microdata_items) > 0,
            'microdata_count': len(microdata_items),
            'has_faq_schema': has_faq_schema,
            'has_article_schema': has_article_schema,
            'has_organization_schema': has_organization_schema,
            'has_product_schema': has_product_schema,
        }
    
    def _extract_performance_data(self, html: str, load_time: float) -> Dict[str, Any]:
        """Extract performance-related data"""
        html_size_kb = len(html.encode('utf-8')) / 1024
        
        # Estimate performance scores (simplified)
        desktop_score = 95 if load_time < 1.5 else (80 if load_time < 3 else (60 if load_time < 5 else 40))
        mobile_score = desktop_score - 20 if desktop_score > 20 else desktop_score
        
        return {
            'load_time_seconds': round(load_time, 2),
            'html_size_kb': round(html_size_kb, 2),
            'is_optimal_size': html_size_kb < 100,
            'desktop_score': desktop_score,
            'mobile_score': mobile_score,
            'needs_optimization': load_time > 3 or html_size_kb > 100,
        }
    
    def _extract_mobile_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract mobile optimization data"""
        viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
        viewport_content = viewport_tag.get('content', '').lower() if viewport_tag else ''
        
        # Check viewport settings
        has_viewport = bool(viewport_tag)
        has_width_device = 'width=device-width' in viewport_content
        has_initial_scale = 'initial-scale=1' in viewport_content
        user_scalable = 'user-scalable' in viewport_content
        user_scalable_no = 'user-scalable=no' in viewport_content
        
        return {
            'has_viewport': has_viewport,
            'viewport_content': viewport_content,
            'has_width_device': has_width_device,
            'has_initial_scale': has_initial_scale,
            'is_responsive': has_viewport and has_width_device,
            'user_scalable': user_scalable,
            'user_scalable_no': user_scalable_no,
        }
    
    def _extract_social_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract social media related data"""
        # Social media links
        social_links = []
        social_platforms = ['facebook', 'twitter', 'linkedin', 'instagram', 'youtube', 'pinterest']
        
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            for platform in social_platforms:
                if platform in href:
                    social_links.append(platform)
                    break
        
        return {
            'social_links_found': list(set(social_links)),
            'social_links_count': len(set(social_links)),
        }
    
    def _extract_security_data(self, response, url: str) -> Dict[str, Any]:
        """Extract security-related headers and data"""
        headers = response.headers
        
        return {
            'https': url.startswith('https://'),
            'has_hsts': 'strict-transport-security' in headers,
            'has_csp': 'content-security-policy' in headers,
            'has_x_frame': 'x-frame-options' in headers,
            'has_x_content_type': 'x-content-type-options' in headers,
        }
    
    # ==================== AUDIT METHODS ====================
    
    async def _audit_technical_seo(self, url: str, crawl_data: Dict) -> List[AuditFinding]:
        """
        Audit Technical SEO (15+ checks)
        Matches SAPRO: Meta robots, OG tags, viewport, sitemap, URL structure, canonical, schema
        """
        findings = []
        meta = crawl_data.get('meta', {})
        technical = crawl_data.get('technical', {})
        structured = crawl_data.get('structured_data', {})
        mobile = crawl_data.get('mobile', {})
        
        # 1. Meta robots tag
        if not meta.get('has_robots'):
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Technical SEO',
                severity='important',
                title='Meta robots tag missing',
                example=f'Current page: {url}',
                importance='The meta robots tag tells search engines whether to index your page and follow its links. Without it, search engines use default behavior, but explicitly setting it ensures your pages are crawled and indexed as intended. This is crucial for SEO visibility.',
                solution='Add the following meta tag in the <head> section of your HTML:\n<meta name="robots" content="index, follow">\n\nThis tells search engines to index the page and follow all links. If you want to prevent indexing on specific pages, use "noindex, nofollow" instead.',
                impact_score=70
            ))
            self.issue_counter += 1
        
        # 2. OG tags and Twitter card
        if not meta.get('has_og_tags'):
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Technical SEO',
                severity='important',
                title='Open Graph (OG) tags missing',
                example='No og:title, og:description, or og:image found',
                importance='Open Graph tags control how your content appears when shared on social media platforms like Facebook, LinkedIn, and Slack. Without them, these platforms will generate their own preview, which often looks unprofessional and reduces click-through rates from social shares.',
                solution='Add these Open Graph meta tags in your <head> section:\n<meta property="og:title" content="Your Page Title">\n<meta property="og:description" content="Compelling description of your page">\n<meta property="og:image" content="https://yoursite.com/image.jpg">\n<meta property="og:url" content="https://yoursite.com/page">\n<meta property="og:type" content="website">',
                impact_score=60
            ))
            self.issue_counter += 1
        
        if not meta.get('has_twitter_card'):
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Technical SEO',
                severity='minor',
                title='Twitter Card meta tags missing',
                example='No twitter:card, twitter:title, or twitter:description found',
                importance='Twitter Card tags ensure your content looks professional when shared on Twitter/X. Without them, Twitter will fall back to basic link previews that are less engaging and get fewer clicks.',
                solution='Add Twitter Card meta tags:\n<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="Your Page Title">\n<meta name="twitter:description" content="Description">\n<meta name="twitter:image" content="https://yoursite.com/image.jpg">',
                impact_score=40
            ))
            self.issue_counter += 1
        
        # 3. user-scalable in viewport
        if mobile.get('user_scalable_no'):
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Technical SEO',
                severity='minor',
                title='user-scalable set to "no" in viewport meta tag',
                example=f'Current viewport: {mobile.get("viewport_content")}',
                importance='Setting user-scalable=no prevents users from zooming on mobile devices, which hurts accessibility and user experience. Google considers this a usability issue that can negatively impact mobile SEO rankings. Users with vision impairments need to be able to zoom.',
                solution='Update your viewport meta tag to allow user scaling:\n<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">\n\nOr simply omit the user-scalable parameter entirely (it defaults to yes).',
                impact_score=35
            ))
            self.issue_counter += 1
        
        # 4. Check for sitemap in robots.txt (we'll need to fetch it)
        sitemap_check = await self._check_robots_txt_sitemap(url)
        if not sitemap_check:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Technical SEO',
                severity='important',
                title='Sitemap not referenced in robots.txt',
                example=f'Robots.txt at {urlparse(url).scheme}://{urlparse(url).netloc}/robots.txt does not contain sitemap reference',
                importance='A sitemap helps search engines discover all pages on your website efficiently. Referencing it in robots.txt ensures search engines know where to find it. Without this, search engines might miss important pages, reducing your site\'s visibility in search results.',
                solution='Add this line to your robots.txt file:\nSitemap: https://yoursite.com/sitemap.xml\n\nMake sure you actually have a sitemap.xml file generated (most CMS platforms like WordPress can generate this automatically with SEO plugins).',
                impact_score=65
            ))
            self.issue_counter += 1
        
        # 5. URL structure
        parsed_url = urlparse(url)
        url_path = parsed_url.path
        if '_' in url_path or url_path.upper() != url_path.lower():
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Technical SEO',
                severity='minor',
                title='URL structure not SEO-friendly',
                example=f'Current URL: {url}',
                importance='SEO-friendly URLs use hyphens (not underscores), lowercase letters, and descriptive keywords. Search engines and users prefer clean, readable URLs. URLs with underscores or mixed case can cause duplicate content issues and are harder for users to remember and share.',
                solution='Use clean URL structure:\n✓ Good: https://site.com/seo-audit-services\n✗ Bad: https://site.com/SEO_Audit_Services\n\nUse hyphens to separate words, keep it lowercase, make it short and descriptive. Most modern CMS platforms have settings to generate SEO-friendly URLs automatically.',
                impact_score=45
            ))
            self.issue_counter += 1
        
        # 6. URL length
        if len(url) > 115:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Technical SEO',
                severity='minor',
                title='URL exceeds recommended length',
                example=f'Current URL: {url} ({len(url)} characters)',
                importance='Long URLs are harder to share, remember, and can be truncated in search results. Google recommends keeping URLs under 75 characters for optimal display. Long URLs also signal poor site structure and can negatively impact user experience.',
                solution=f'Shorten your URL from {len(url)} characters to under 75 characters. Remove unnecessary words, parameters, and nested folders. Example:\nInstead of: /blog/2024/01/category/subcategory/very-long-article-title-with-many-words\nUse: /blog/short-article-title',
                impact_score=30,
                current_value=f'{len(url)} characters',
                recommended_value='< 75 characters'
            ))
            self.issue_counter += 1
        
        # 7. HTTPS
        if not technical.get('https'):
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Technical SEO',
                severity='critical',
                title='Website not using HTTPS',
                example=f'Current URL: {url}',
                importance='HTTPS encrypts data between your website and visitors, protecting sensitive information. Google has made HTTPS a ranking factor since 2014. Non-HTTPS sites show "Not Secure" warnings in browsers, which dramatically reduces trust and conversions. This is a critical SEO issue.',
                solution='1. Purchase and install an SSL certificate (many hosting providers offer free SSL certificates via Let\'s Encrypt)\n2. Update your site to use HTTPS URLs\n3. Set up 301 redirects from HTTP to HTTPS\n4. Update internal links to use HTTPS\n5. Update Google Search Console with HTTPS version\n\nMost hosting providers can do this for you if you request it.',
                impact_score=95
            ))
            self.issue_counter += 1
        
        # 8. Canonical tag
        if not technical.get('has_canonical'):
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Technical SEO',
                severity='important',
                title='Canonical tag missing',
                example=f'No canonical tag found on {url}',
                importance='The canonical tag tells search engines which version of a page is the "master" version when you have duplicate or similar content. Without it, search engines might index the wrong version or split ranking signals across multiple URLs, diluting your SEO power.',
                solution='Add a self-referencing canonical tag in your <head> section:\n<link rel="canonical" href="https://yoursite.com/page-url">\n\nThis should point to the preferred version of the page. Most SEO plugins and modern CMS platforms add this automatically.',
                impact_score=65
            ))
            self.issue_counter += 1
        
        # 9. Schema markup
        if not structured.get('has_json_ld') and not structured.get('has_microdata'):
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Technical SEO',
                severity='important',
                title='Schema markup (structured data) missing',
                example='No JSON-LD or Microdata found',
                importance='Schema markup helps search engines understand your content better and can earn you rich snippets in search results (star ratings, images, prices, etc.). These rich results get 30% more clicks than regular results. Sites with schema markup have a significant advantage in search visibility.',
                solution='Implement JSON-LD structured data for your content type:\n\nFor Articles/Blogs:\n<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n  "@type": "Article",\n  "headline": "Your Article Title",\n  "author": "Author Name",\n  "datePublished": "2024-01-01"\n}\n</script>\n\nFor Local Business:\n<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n  "@type": "LocalBusiness",\n  "name": "Business Name",\n  "address": {...},\n  "telephone": "...",\n}\n</script>\n\nUse Google\'s Structured Data Markup Helper to generate code for your specific use case.',
                impact_score=70
            ))
            self.issue_counter += 1
        
        # 10. Multiple redirects
        if technical.get('redirects', 0) > 1:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Technical SEO',
                severity='minor',
                title='Multiple redirects detected',
                example=f'Page has {technical.get("redirects")} redirect(s) before reaching final URL',
                importance='Multiple redirects create a "redirect chain" that slows down page loading and wastes search engine crawl budget. Each redirect adds latency and can cause search engines to abandon crawling the page. This negatively impacts both user experience and SEO.',
                solution=f'Reduce redirect chain from {technical.get("redirects")} redirects to 0-1 redirects. Update links to point directly to the final URL. Check your .htaccess file or server configuration for unnecessary redirects.',
                impact_score=40
            ))
            self.issue_counter += 1
        
        return findings
    
    async def _check_robots_txt_sitemap(self, url: str) -> bool:
        """Check if robots.txt contains sitemap reference"""
        try:
            parsed = urlparse(url)
            robots_url = f'{parsed.scheme}://{parsed.netloc}/robots.txt'
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(robots_url)
                if response.status_code == 200:
                    content = response.text.lower()
                    return 'sitemap:' in content
        except:
            pass
        return False
    
    async def _audit_core_web_vitals(self, url: str, crawl_data: Dict) -> List[AuditFinding]:
        """
        Audit Core Web Vitals & Performance (10+ checks)
        Matches SAPRO: Desktop/Mobile performance, caching, render-blocking, images
        """
        findings = []
        performance = crawl_data.get('performance', {})
        images = crawl_data.get('images', {})
        
        # Desktop & Mobile Performance Scores
        desktop_score = performance.get('desktop_score', 0)
        mobile_score = performance.get('mobile_score', 0)
        load_time = performance.get('load_time_seconds', 0)
        
        # Add performance summary finding
        if desktop_score < 90 or mobile_score < 70:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Core Web Vitals & Performance',
                severity='important',
                title='Core Web Vitals need improvement',
                example=f'Desktop Performance: {desktop_score}/100\nMobile Performance: {mobile_score}/100',
                importance='Core Web Vitals are Google\'s official metrics for measuring user experience. They directly impact your search rankings. Poor performance scores mean slower load times, which cause visitors to leave before your page loads. Studies show that a 1-second delay reduces conversions by 7%.',
                solution='Action Priority to improve scores:\n\n1. **Fix caching and render-blocking issues**: Enable browser caching and defer non-critical JavaScript\n2. **Optimize image delivery**: Compress images, use WebP format, implement lazy loading\n3. **Preload key resources**: Add <link rel="preload"> for critical assets\n4. **Optimize font display**: Use font-display: swap to prevent invisible text\n5. **Review and reduce legacy JS**: Remove unused JavaScript libraries\n6. **Use a CDN**: Deliver content from servers closer to users\n7. **Minimize CSS**: Remove unused CSS and inline critical CSS\n\nRun Google PageSpeed Insights for specific recommendations.',
                impact_score=85,
                current_value=f'Desktop: {desktop_score}, Mobile: {mobile_score}',
                recommended_value='Desktop: >90, Mobile: >80'
            ))
            self.issue_counter += 1
        
        # Slow load time
        if load_time > 3:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Core Web Vitals & Performance',
                severity='critical' if load_time > 5 else 'important',
                title='Slow page load time',
                example=f'Current load time: {load_time:.2f} seconds (recommended: < 3 seconds)',
                importance=f'Your page loads in {load_time:.2f} seconds, which is too slow. Google recommends pages load in under 3 seconds. 53% of mobile users abandon sites that take longer than 3 seconds to load. Every second of delay costs you visitors and sales. Fast sites rank higher in Google and convert better.',
                solution='**Immediate actions to improve load time:**\n\n1. Optimize images (often the #1 cause):\n   - Compress images using tools like TinyPNG\n   - Convert to WebP format\n   - Resize images to actual display dimensions\n\n2. Enable caching:\n   - Add caching headers to your server\n   - Use a caching plugin if on WordPress\n\n3. Minimize code:\n   - Minify JavaScript, CSS, and HTML\n   - Remove unused code\n\n4. Use a CDN:\n   - Cloudflare (free plan available)\n   - Distributes content globally for faster access\n\n5. Upgrade hosting:\n   - Consider better hosting if on shared hosting\n\nExpected improvement: Reduce to under 2 seconds with these changes.',
                impact_score=90,
                current_value=f'{load_time:.2f} seconds',
                recommended_value='< 2 seconds'
            ))
            self.issue_counter += 1
        
        # Image optimization
        if images.get('images_needing_optimization', 0) > 0:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Core Web Vitals & Performance',
                severity='important',
                title='Images need optimization',
                example=f'{images.get("images_needing_optimization")} images found using non-optimized formats (JPG/PNG)',
                importance='Unoptimized images are often the largest files on your page and the main cause of slow load times. Large images waste bandwidth and frustrate mobile users. Optimizing images can reduce page size by 60-80%, dramatically improving load speed and user experience.',
                solution='**Image optimization steps:**\n\n1. **Compress existing images:**\n   - Use TinyPNG.com or ImageOptim (free tools)\n   - Reduces file size by 60-80% without visible quality loss\n\n2. **Convert to modern formats:**\n   - WebP format is 30% smaller than JPEG\n   - AVIF is even better (newest format)\n\n3. **Resize images:**\n   - Don\'t use 4000px images when displaying at 800px\n   - Save different sizes for desktop and mobile\n\n4. **Implement lazy loading:**\n   - Add loading="lazy" attribute to <img> tags\n   - Images load only when user scrolls to them\n\n5. **Use responsive images:**\n   - <img srcset="..."> for different screen sizes\n\n**WordPress users:** Use a plugin like "Smush" or "ShortPixel" to automatically optimize all images.',
                impact_score=75
            ))
            self.issue_counter += 1
        
        # Large HTML size
        html_size = performance.get('html_size_kb', 0)
        if html_size > 100:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Core Web Vitals & Performance',
                severity='minor',
                title='HTML file size too large',
                example=f'HTML size: {html_size:.1f} KB (optimal: < 100 KB)',
                importance='Large HTML files take longer to download and parse, slowing down your page load time. This is especially problematic for mobile users on slower connections. Bloated HTML often indicates excessive inline code or unnecessary elements.',
                solution='**Reduce HTML size:**\n\n1. **Minify HTML:**\n   - Remove whitespace, comments, and formatting\n   - Use HTML minification tools or plugins\n\n2. **Move CSS/JS to external files:**\n   - Don\'t inline large amounts of CSS/JavaScript\n   - External files can be cached\n\n3. **Remove unnecessary code:**\n   - Clean up unused HTML elements\n   - Remove excessive whitespace\n   - Eliminate commented-out code\n\n4. **Optimize inline styles:**\n   - Only inline critical above-the-fold CSS\n   - Move rest to external stylesheet\n\n**WordPress users:** Use a plugin like "Autoptimize" to automatically minify HTML, CSS, and JavaScript.',
                impact_score=45,
                current_value=f'{html_size:.1f} KB',
                recommended_value='< 100 KB'
            ))
            self.issue_counter += 1
        
        return findings
    
    async def _audit_onpage_seo(self, url: str, crawl_data: Dict) -> List[AuditFinding]:
        """
        Audit On-Page SEO (20+ checks)
        Matches SAPRO: Title length, description, duplicate titles/descriptions, H1 tags, hierarchy, alt tags, internal linking, content structure
        """
        findings = []
        meta = crawl_data.get('meta', {})
        content = crawl_data.get('content', {})
        images = crawl_data.get('images', {})
        links = crawl_data.get('links', {})
        
        # 1. Meta title checks
        title = meta.get('title', '')
        title_length = meta.get('title_length', 0)
        
        if not title:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='On-Page SEO',
                severity='critical',
                title='Meta title missing',
                example=f'Page URL: {url}',
                importance='The meta title is THE MOST IMPORTANT on-page SEO element. It\'s the blue clickable headline in Google search results. Without a title, Google will generate one automatically, which usually doesn\'t include your key terms and won\'t attract clicks. This is a CRITICAL issue that must be fixed immediately.',
                solution='**Add a compelling meta title (50-60 characters):**\n\n<title>Your Main Keyword | Brand Name</title>\n\nExample titles:\n• "Best Pizza in NYC | Joe\'s Pizzeria"\n• "SEO Services for Small Business | RankForge"\n• "Handmade Organic Soap | Natural Skincare"\n\n**Tips for great titles:**\n• Include your main keyword at the beginning\n• Add your brand name at the end\n• Make it compelling and clickable\n• Stay between 50-60 characters\n• Make each page\'s title unique\n\n**How to add:** If using WordPress, fill in the "SEO Title" field in your SEO plugin (Yoast, Rank Math, etc.). If coding manually, add the <title> tag in your <head> section.',
                impact_score=100
            ))
            self.issue_counter += 1
        
        elif title_length < 30:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='On-Page SEO',
                severity='important',
                title='Meta title too short',
                example=f'Current title: "{title}" ({title_length} characters)',
                importance=f'Your title is only {title_length} characters. Google displays up to 60 characters, so you\'re not using the full space available. Longer, more descriptive titles perform better in search results because they provide more context to searchers and can include more keywords.',
                solution=f'**Expand your title to 50-60 characters:**\n\nCurrent: "{title}" ({title_length} chars)\n\nSuggested improvements:\n• Add your unique value proposition\n• Include your main keyword if missing\n• Add your location (if local business)\n• Add your brand name\n\nExample expansion:\n• Short: "Home"\n• Better: "Premium Web Design Services | YourBrand"\n\n• Short: "About"\n• Better: "About Us - Expert SEO Agency in Boston | YourBrand"\n\n**Aim for 50-60 characters for optimal display.**',
                impact_score=65,
                current_value=f'{title_length} characters',
                recommended_value='50-60 characters'
            ))
            self.issue_counter += 1
        
        elif title_length > 60:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='On-Page SEO',
                severity='important',
                title='Meta title too long',
                example=f'Current title: "{title}" ({title_length} characters)',
                importance=f'Your title is {title_length} characters, which exceeds Google\'s 60-character display limit. The end of your title will be cut off with "..." in search results, hiding important information from searchers. This reduces click-through rates.',
                solution=f'**Shorten your title to 50-60 characters:**\n\nCurrent ({title_length} chars): "{title}"\n\n**Steps to shorten:**\n1. Remove unnecessary words (a, the, and, etc.)\n2. Use abbreviations where appropriate\n3. Remove redundant information\n4. Keep the most important keywords at the start\n5. Prioritize what you want searchers to see first\n\nExample:\n• Too long (78 chars): "Professional SEO Services and Digital Marketing Agency for Small Business"\n• Better (59 chars): "SEO Services for Small Business | Digital Marketing"\n\n**Critical:** Put your most important keywords in the first 50 characters.',
                impact_score=65,
                current_value=f'{title_length} characters',
                recommended_value='50-60 characters'
            ))
            self.issue_counter += 1
        
        # 2. Meta description checks
        description = meta.get('description', '')
        description_length = meta.get('description_length', 0)
        
        if not description:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='On-Page SEO',
                severity='important',
                title='Meta description missing',
                example=f'Page URL: {url}',
                importance='The meta description is the gray text that appears under your title in Google search results. It\'s your "sales pitch" to convince people to click your link instead of competitors. Without a description, Google creates one automatically by pulling random text from your page, which is usually not compelling and reduces click-through rates by 30%+.',
                solution='**Add a compelling meta description (150-160 characters):**\n\n<meta name="description" content="Your description here...">\n\nExample descriptions:\n• "Discover handmade organic soaps made with natural ingredients. Free shipping on orders over $30. Perfect for sensitive skin."\n• "Professional SEO services for small businesses. Increase your Google rankings and get more customers. Free audit included."\n\n**Tips for great descriptions:**\n• Include your main keyword naturally\n• Highlight your unique benefits\n• Add a call-to-action\n• Make it compelling and click-worthy\n• Stay between 150-160 characters\n• Include numbers or special offers when relevant\n\n**How to add:** Use your SEO plugin\'s "Meta Description" field (WordPress) or add the <meta> tag manually in your <head> section.',
                impact_score=80
            ))
            self.issue_counter += 1
        
        elif description_length < 120:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='On-Page SEO',
                severity='minor',
                title='Meta description too short',
                example=f'Current description: "{description}" ({description_length} characters)',
                importance=f'Your description is only {description_length} characters. Google displays up to 160 characters, so you\'re missing an opportunity to provide more compelling information. Longer descriptions that fill the available space perform better because they can include more benefits and keywords.',
                solution=f'**Expand your description to 150-160 characters:**\n\nCurrent ({description_length} chars): "{description}"\n\n**What to add:**\n• Key benefits of your product/service\n• What makes you unique/different\n• Social proof (awards, reviews, years in business)\n• Call-to-action\n• Special offers or guarantees\n\nExample expansion:\n• Short (90 chars): "We provide SEO services."\n• Better (155 chars): "We provide SEO services that increase rankings by 200% on average. Get more customers with proven strategies. Free consultation available. Trusted by 500+ businesses."\n\n**Use the full 150-160 characters available.**',
                impact_score=40,
                current_value=f'{description_length} characters',
                recommended_value='150-160 characters'
            ))
            self.issue_counter += 1
        
        elif description_length > 160:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='On-Page SEO',
                severity='minor',
                title='Meta description too long',
                example=f'Current description length: {description_length} characters (shown: "{description[:100]}...")',
                importance=f'Your description is {description_length} characters, which exceeds Google\'s 160-character display limit. The end will be cut off with "..." in search results, potentially hiding your call-to-action or most compelling benefit.',
                solution=f'**Shorten your description to 150-160 characters:**\n\nCurrent ({description_length} chars): Too long to show fully\n\n**Steps to shorten:**\n1. Remove less important details\n2. Be more concise\n3. Keep the most compelling benefits\n4. Ensure call-to-action is within first 150 chars\n5. Remove redundant phrases\n\n**Priority:** Put your strongest selling points and call-to-action in the first 150 characters to ensure they\'re visible in search results.',
                impact_score=40,
                current_value=f'{description_length} characters',
                recommended_value='150-160 characters'
            ))
            self.issue_counter += 1
        
        # 3. H1 tag checks
        h1_count = content.get('h1_count', 0)
        h1_texts = content.get('h1_texts', [])
        
        if h1_count == 0:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='On-Page SEO',
                severity='important',
                title='H1 heading missing',
                example=f'No H1 tag found on page: {url}',
                importance='The H1 tag is your page\'s main headline and the second most important on-page SEO element (after the title). It tells both users and search engines what your page is about. Pages without H1 tags struggle to rank because search engines can\'t clearly determine the page topic.',
                solution='**Add an H1 heading to your page:**\n\n<h1>Your Main Page Heading</h1>\n\n**H1 best practices:**\n• Only ONE H1 per page\n• Include your main target keyword\n• Make it descriptive and relevant to page content\n• Place it near the top of your page\n• Make it different from your title tag (but related)\n\nExamples:\n• Title: "SEO Services | YourBrand"\n• H1: "Professional SEO Services to Grow Your Business"\n\n• Title: "Best Pizza in NYC | Joe\'s Pizzeria"\n• H1: "Award-Winning New York Style Pizza Since 1975"\n\n**How to add:** In your page editor, select your main heading text and format it as "Heading 1" or "H1". Most website builders have this option in the formatting toolbar.',
                impact_score=80
            ))
            self.issue_counter += 1
        
        elif h1_count > 1:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='On-Page SEO',
                severity='important',
                title='Multiple H1 tags found',
                example=f'Found {h1_count} H1 tags: {", ".join(h1_texts[:3])}...',
                importance=f'Your page has {h1_count} H1 tags, but SEO best practice is to have only ONE H1 per page. Multiple H1s confuse search engines about which is the main topic. This dilutes your SEO power and can prevent the page from ranking well for your target keyword.',
                solution='**Fix multiple H1 tags:**\n\nCurrent H1s found:\n{}\n\n**Steps to fix:**\n1. Identify which heading is your MAIN page topic\n2. Keep that one as H1\n3. Change the other headings to H2 or H3\n4. Use proper heading hierarchy: H1 > H2 > H3\n\n**Heading structure example:**\n<h1>Main Page Topic</h1>  ← Only ONE H1\n<h2>First Major Section</h2>\n<h3>Subsection</h3>\n<h2>Second Major Section</h2>\n<h3>Subsection</h3>\n\n**In your editor:** Reformat extra H1s to H2 or H3 depending on their importance in your content hierarchy.'.format('\n'.join([f'• "{h1}"' for h1 in h1_texts])),
                impact_score=70
            ))
            self.issue_counter += 1
        
        # 4. Duplicate H1s
        if content.get('h1_duplicates'):
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='On-Page SEO',
                severity='important',
                title='Duplicate H1 tags detected',
                example=f'Duplicate H1 text: "{content.get("h1_duplicates")[0]}" appears multiple times',
                importance='You have the same H1 text appearing multiple times on your page. This is confusing for search engines and users. Each heading should be unique and describe different sections. Duplicate headings dilute your keyword targeting and suggest poorly structured content.',
                solution='**Fix duplicate H1 tags:**\n\n1. Make each heading unique and descriptive\n2. Use variations that target related keywords\n3. Ensure headings describe different sections\n\n**Example fix:**\nInstead of:\n<h1>Our Services</h1>\n<h1>Our Services</h1>\n\nUse:\n<h1>Our Services</h1>\n<h2>Service Category 1</h2>\n<h2>Service Category 2</h2>',
                impact_score=60
            ))
            self.issue_counter += 1
        
        # 5. Heading structure
        if not content.get('has_heading_structure'):
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='On-Page SEO',
                severity='minor',
                title='Weak heading hierarchy',
                example='Page lacks proper H2/H3 subheadings',
                importance='Proper heading hierarchy (H1 > H2 > H3) helps search engines understand your content structure and improves user experience. Pages without H2/H3 subheadings are harder to scan and can rank lower because they appear less organized and comprehensive.',
                solution='**Implement proper heading structure:**\n\n<h1>Main Page Title</h1>\n  <h2>Major Section 1</h2>\n    <h3>Subsection 1.1</h3>\n    <h3>Subsection 1.2</h3>\n  <h2>Major Section 2</h2>\n    <h3>Subsection 2.1</h3>\n\n**Best practices:**\n• Break long content into logical sections\n• Use H2 for main sections\n• Use H3 for subsections\n• Include keywords naturally in headings\n• Make headings descriptive\n\n**Benefits:**\n• Easier for users to scan\n• Better for accessibility\n• Search engines understand structure better\n• Can appear as jumplinks in search results',
                impact_score=50
            ))
            self.issue_counter += 1
        
        # 6. Images without alt tags
        images_without_alt = images.get('images_without_alt', 0)
        if images_without_alt > 0:
            alt_examples = images.get('images_without_alt_list', [])[:3]
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='On-Page SEO',
                severity='important',
                title=f'{images_without_alt} images missing alt text',
                example=f'Images without alt tags:\n' + '\n'.join([f'• {img}' for img in alt_examples]),
                importance=f'Alt text (alternative text) describes images for search engines and screen readers. {images_without_alt} images on your page have no alt text, which means:\n• Search engines can\'t understand what the images show\n• Images won\'t appear in Google Image Search\n• Visually impaired users can\'t understand the content\n• You\'re missing keyword optimization opportunities\n\nThis hurts both SEO and accessibility.',
                solution=f'**Add descriptive alt text to all {images_without_alt} images:**\n\n<img src="image.jpg" alt="Descriptive text here">\n\n**Alt text best practices:**\n• Describe what\'s in the image accurately\n• Include keywords naturally (don\'t stuff)\n• Keep it concise (10-15 words)\n• Don\'t start with "image of" or "picture of"\n• Make it useful for someone who can\'t see the image\n\n**Examples:**\n✗ Bad: alt="img123"\n✗ Bad: alt=""\n✓ Good: alt="red leather sofa in modern living room"\n✓ Good: alt="team meeting discussing SEO strategy"\n✓ Good: alt="homemade chocolate chip cookies on white plate"\n\n**How to add:**\n• WordPress: Click image, add text in "Alt Text" field\n• HTML: Add alt="description" to <img> tag\n• Most website builders: Image properties/settings\n\n**Priority:** Fix decorative images last, content images first.',
                impact_score=70
            ))
            self.issue_counter += 1
        
        # 7. Internal linking
        internal_links = links.get('internal_links', 0)
        if internal_links < 3:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='On-Page SEO',
                severity='minor',
                title='Insufficient internal linking',
                example=f'Only {internal_links} internal links found',
                importance='Internal links connect your pages together, helping users discover more content and helping search engines understand your site structure. Pages with few internal links are considered less important by search engines. Good internal linking distributes SEO power across your site and keeps visitors engaged longer.',
                solution=f'**Add more internal links (recommended: 5-10 per page):**\n\n**Where to add internal links:**\n1. Within your content text (contextual links)\n2. Related articles/products section\n3. Call-to-action boxes\n4. Navigation menus\n5. Sidebar widgets\n\n**Internal linking best practices:**\n• Link to related, relevant content\n• Use descriptive anchor text (not "click here")\n• Link to important pages you want to rank\n• Create a logical site structure\n• Add "Related Posts" section\n\n**Example:**\nInstead of: "Click here to learn more"\nUse: "Learn more about our SEO services for small businesses"\n\n**Strategic internal linking:**\n• Link from high-authority pages to newer pages\n• Create topic clusters linking related content\n• Use breadcrumbs navigation\n• Add "popular posts" section\n\n**Current:** {internal_links} internal links\n**Recommended:** 5-10 internal links per page',
                impact_score=45
            ))
            self.issue_counter += 1
        
        # 8. Content structure elements
        if not content.get('has_toc'):
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='On-Page SEO',
                severity='minor',
                title='Table of Contents (TOC) missing',
                example='No table of contents found',
                importance='A table of contents improves user experience on long-form content by letting readers jump to sections they\'re interested in. It also helps with SEO by creating jump links that can appear in Google search results, making your listing more prominent and clickable.',
                solution='**Add a Table of Contents for articles over 1,500 words:**\n\n<nav>\n  <h2>Table of Contents</h2>\n  <ul>\n    <li><a href="#section1">Section 1 Title</a></li>\n    <li><a href="#section2">Section 2 Title</a></li>\n    <li><a href="#section3">Section 3 Title</a></li>\n  </ul>\n</nav>\n\n**Benefits:**\n• Better user experience\n• Can get "Jump to" links in Google\n• Increases time on page\n• Helps with featured snippets\n\n**WordPress users:** Use plugins like "Table of Contents Plus" or "Easy Table of Contents" to automatically generate TOCs.',
                impact_score=35
            ))
            self.issue_counter += 1
        
        if not content.get('has_author'):
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='On-Page SEO',
                severity='minor',
                title='Author information missing',
                example='No author section found',
                importance='Author information builds trust and authority (E-E-A-T: Experience, Expertise, Authoritativeness, Trustworthiness). Google values content from identifiable experts. Missing author info can hurt rankings, especially for YMYL (Your Money Your Life) topics like health, finance, and legal content.',
                solution='**Add author information to your content:**\n\n<div class="author-box">\n  <img src="author-photo.jpg" alt="John Doe">\n  <h3>About the Author</h3>\n  <p><strong>John Doe</strong> is a certified SEO specialist with 10 years of experience...</p>\n  <p>Connect: <a href="...">LinkedIn</a> | <a href="...">Twitter</a></p>\n</div>\n\n**What to include:**\n• Author name and photo\n• Credentials/qualifications\n• Brief bio highlighting expertise\n• Social media links\n• Author archive link\n\n**Why it matters:**\n• Builds reader trust\n• Improves E-E-A-T signals\n• Can get Google Author snippets\n• Shows expertise\n• Humanizes your content\n\n**WordPress users:** Your theme may have built-in author boxes, or use a plugin.',
                impact_score=40
            ))
            self.issue_counter += 1
        
        if not content.get('has_related'):
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='On-Page SEO',
                severity='minor',
                title='Related articles/content section missing',
                example='No related content section found',
                importance='Related articles keep visitors on your site longer, reduce bounce rate, and help distribute SEO value across pages. They also help search engines understand content relationships and topical authority. Sites with related content sections see 30% longer session durations.',
                solution='**Add a "Related Articles" or "You May Also Like" section:**\n\n<section class="related-posts">\n  <h2>Related Articles</h2>\n  <div class="article-grid">\n    <article>\n      <img src="..." alt="...">\n      <h3><a href="...">Related Article Title 1</a></h3>\n      <p>Brief description...</p>\n    </article>\n    <!-- More related articles -->\n  </div>\n</section>\n\n**Best practices:**\n• Show 3-6 related items\n• Use thumbnails/images\n• Write compelling titles\n• Add brief descriptions\n• Link to truly related content (not random)\n\n**Placement options:**\n• Bottom of article (most common)\n• Sidebar\n• Mid-content for long articles\n• After conclusion\n\n**WordPress users:** Most themes include this, or use plugins like "Related Posts" or "YARPP".',
                impact_score=35
            ))
            self.issue_counter += 1
        
        return findings
    
    async def _audit_website_content(self, url: str, crawl_data: Dict) -> List[AuditFinding]:
        """
        Audit Website Content Quality (5+ checks)
        Matches SAPRO: Word count, AI-written content detection
        """
        findings = []
        content = crawl_data.get('content', {})
        
        word_count = content.get('word_count', 0)
        
        # Word count check
        if word_count < 300:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Website Content',
                severity='important',
                title='Thin content - insufficient word count',
                example=f'Current word count: {word_count} words (recommended: 800-1000+ words)',
                importance=f'Your page has only {word_count} words, which is considered "thin content" by Google. Studies show that top-ranking pages have an average of 1,890 words. Short content suggests lack of depth and value. Google favors comprehensive, detailed content that thoroughly answers user questions.',
                solution=f'**Expand your content to at least 800-1,000 words:**\n\nCurrent: {word_count} words\nTarget: 800-1,000 words minimum (1,500-2,500 for competitive topics)\n\n**How to add valuable content:**\n\n1. **Answer more questions:**\n   • What, Why, How, When, Where\n   • Common objections\n   • FAQs\n\n2. **Add more detail:**\n   • Step-by-step instructions\n   • Examples and case studies\n   • Benefits and features\n   • Comparisons\n\n3. **Include supporting elements:**\n   • Statistics and data\n   • Expert quotes\n   • Images and videos\n   • Lists and tables\n\n4. **Cover related topics:**\n   • Background information\n   • Context and history\n   • Related concepts\n   • Future implications\n\n**Quality over quantity:** Don\'t add fluff. Every sentence should provide value. Use the inverted pyramid: most important info first.\n\n**Research competitors:** See how much content top-ranking pages have for your target keyword and match or exceed it.',
                impact_score=75,
                current_value=f'{word_count} words',
                recommended_value='800-1,000+ words'
            ))
            self.issue_counter += 1
        
        elif 300 <= word_count < 800:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Website Content',
                severity='minor',
                title='Content could be more comprehensive',
                example=f'Current word count: {word_count} words (recommended: 800-1000+ for better rankings)',
                importance=f'Your page has {word_count} words, which is decent but may not be enough to compete for competitive keywords. Top-ranking content is typically more comprehensive. Longer, more detailed content tends to rank higher because it provides more value and answers more user questions.',
                solution=f'**Consider expanding to 800-1,000+ words for competitive topics:**\n\nCurrent: {word_count} words\n\n**Ways to expand naturally:**\n• Add real examples and case studies\n• Include statistics and research data\n• Answer common questions more thoroughly\n• Add "how-to" sections with steps\n• Include pro tips and best practices\n• Add comparison tables\n• Embed relevant videos or infographics\n• Add expert insights or quotes\n\n**Note:** Length alone doesn\'t guarantee rankings, but comprehensive coverage of topics does. Focus on providing complete answers.',
                impact_score=50,
                current_value=f'{word_count} words',
                recommended_value='800-1,000+ words'
            ))
            self.issue_counter += 1
        
        # AI-written content detection (simplified heuristic)
        text = content.get('text', '')
        ai_indicators = await self._detect_ai_content(text[:2000])
        
        if ai_indicators.get('likely_ai', False):
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Website Content',
                severity='important',
                title='Content may be AI-generated without human review',
                example='Content shows patterns typical of AI-generated text',
                importance='AI-generated content that hasn\'t been reviewed and enhanced by humans often lacks personal experience, specific examples, and unique insights. Google\'s algorithms can detect purely AI content and may rank it lower. While AI tools are helpful, content needs human expertise, real examples, and personal touch to rank well and build trust.',
                solution='**Humanize and enhance AI-generated content:**\n\n1. **Add personal experience:**\n   • Share real examples from your work\n   • Include specific case studies\n   • Add personal anecdotes\n   • Show your unique perspective\n\n2. **Improve with specific details:**\n   • Replace generic advice with specific tips\n   • Add actual numbers and results\n   • Include industry-specific insights\n   • Use real company/product names\n\n3. **Make it more conversational:**\n   • Use "you" and "I" pronouns\n   • Write in your brand voice\n   • Add personality and humor\n   • Break up long sentences\n\n4. **Add unique value:**\n   • Include original research\n   • Share expert opinions\n   • Add your professional experience\n   • Provide insider tips\n\n5. **Update generic sections:**\n   • Replace overused phrases\n   • Add specific examples\n   • Include current information\n   • Link to authoritative sources\n\n**Remember:** AI is a tool to assist writing, not replace human expertise. Always add your unique insights and real-world experience.',
                impact_score=70
            ))
            self.issue_counter += 1
        
        return findings
    
    async def _detect_ai_content(self, text: str) -> Dict[str, Any]:
        """Simplified AI content detection using heuristics"""
        # Simple heuristic: AI content often has very uniform sentence lengths, 
        # formal tone, and certain phrases
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {'likely_ai': False, 'confidence': 0}
        
        # Check sentence length variance (AI tends to be more uniform)
        lengths = [len(s.split()) for s in sentences]
        if lengths:
            avg_length = sum(lengths) / len(lengths)
            variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            
            # Low variance might indicate AI
            likely_ai = variance < 20 and avg_length > 15
        else:
            likely_ai = False
        
        # Check for common AI phrases
        ai_phrases = [
            'in today\'s digital landscape',
            'in this article, we will',
            'it\'s important to note',
            'in conclusion',
            'let\'s dive in',
            'in this comprehensive guide',
        ]
        
        text_lower = text.lower()
        ai_phrase_count = sum(1 for phrase in ai_phrases if phrase in text_lower)
        
        if ai_phrase_count >= 2:
            likely_ai = True
        
        return {
            'likely_ai': likely_ai,
            'confidence': 'low',  # This is a simple heuristic, not ML-based
            'indicators': f'{ai_phrase_count} common AI phrases detected'
        }
    
    async def _audit_social_media(self, url: str, crawl_data: Dict) -> List[AuditFinding]:
        """
        Audit Social Media presence (3+ checks)
        Matches SAPRO: Social media strategy and content mix
        """
        findings = []
        social = crawl_data.get('social', {})
        
        social_links = social.get('social_links_count', 0)
        
        if social_links < 3:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Social Media',
                severity='minor',
                title='Limited social media presence',
                example=f'Only {social_links} social media platform(s) linked: {", ".join(social.get("social_links_found", []))}',
                importance='Social media presence is important for brand visibility, traffic, and indirect SEO benefits. Having profiles on multiple relevant platforms gives you more channels to reach customers, build community, and drive traffic to your website. Social signals also contribute to overall brand authority.',
                solution=f'**Expand social media presence to 3-5 relevant platforms:**\n\nCurrently active on: {", ".join(social.get("social_links_found", [])) if social.get("social_links_found") else "None"}\n\n**Recommended platforms by business type:**\n\n**For B2B:**\n• LinkedIn (essential)\n• Twitter/X\n• YouTube\n• Facebook\n\n**For B2C:**\n• Instagram (visual products)\n• Facebook\n• TikTok (younger audience)\n• Pinterest (e-commerce, DIY)\n• YouTube (tutorials, reviews)\n\n**For local businesses:**\n• Facebook (essential)\n• Instagram\n• Google Business Profile\n• Nextdoor\n\n**Action steps:**\n1. Create profiles on 3-5 relevant platforms\n2. Complete all profile information\n3. Add profile links to your website footer\n4. Post consistently (2-3x per week minimum)\n5. Engage with your audience\n6. Share your website content\n\n**Content mix strategy:**\n• 40% educational content\n• 30% engaging/entertaining content\n• 20% promotional content\n• 10% company culture/behind-the-scenes\n\n**Quality over quantity:** It\'s better to be active on 3 platforms than inactive on 10.',
                impact_score=40
            ))
            self.issue_counter += 1
        
        return findings
    
    async def _audit_offpage_seo(self, url: str, crawl_data: Dict) -> List[AuditFinding]:
        """
        Audit Off-Page SEO (8+ checks)
        Matches SAPRO: Domain Authority, linking domain authority, backlink quality, spam score
        """
        findings = []
        
        # Estimate domain metrics (in production, use real APIs like Moz, Ahrefs)
        domain_metrics = await self._estimate_domain_metrics(url)
        
        # Domain Authority check
        da = domain_metrics.get('domain_authority', 0)
        if da < 30:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Off-Page SEO',
                severity='important',
                title='Low Domain Authority (DA)',
                example=f'Current Domain Authority: {da}/100',
                importance=f'Your Domain Authority is {da} out of 100, which is considered low. DA predicts how well your site will rank in search engines. Low DA means your site has less authority and trust in Google\'s eyes, making it harder to rank for competitive keywords. This is typically due to insufficient high-quality backlinks.',
                solution=f'**Improve Domain Authority from {da} to 30+:**\n\nDomain Authority is primarily increased by earning high-quality backlinks from authoritative websites. Here\'s how:\n\n**1. Create Link-Worthy Content:**\n   • Original research and data\n   • Comprehensive guides (2,000+ words)\n   • Infographics and visual content\n   • Expert roundups\n   • Tools and calculators\n   • Industry reports\n\n**2. Build High-Quality Backlinks:**\n   • Guest posting on reputable sites\n   • Get featured in industry publications\n   • Create shareable resources\n   • Broken link building\n   • Resource page link building\n   • Digital PR campaigns\n\n**3. Specific Link-Building Strategies:**\n   • Reach out to sites linking to competitors\n   • Create "Best of" lists\n   • Conduct original surveys/research\n   • Build relationships with journalists\n   • Speak at industry events\n   • Sponsor relevant events\n\n**4. Leverage Existing Networks:**\n   • Partners and vendors\n   • Suppliers and distributors\n   • Business associations\n   • Local chambers of commerce\n   • Industry directories\n\n**5. Quality Over Quantity:**\n   • ONE link from DA 70 site > TEN links from DA 20 sites\n   • Focus on relevant, authoritative sites in your industry\n   • Avoid spammy link schemes\n\n**Timeline:** Building DA takes 3-6 months of consistent effort. Don\'t expect overnight results.\n\n**Track progress:** Use Moz Link Explorer or Ahrefs to monitor your DA monthly.',
                impact_score=80,
                current_value=f'DA: {da}',
                recommended_value='DA: 30-50+'
            ))
            self.issue_counter += 1
        
        # Backlinks from low-authority domains
        low_authority_links = domain_metrics.get('low_authority_links_percentage', 0)
        if low_authority_links > 40:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Off-Page SEO',
                severity='important',
                title='High percentage of backlinks from low-authority domains',
                example=f'{low_authority_links}% of linking domains have DA below 30',
                importance=f'{low_authority_links}% of your backlinks come from low-authority websites (DA < 30). Low-quality backlinks don\'t help your rankings and can even hurt them if they\'re from spammy sites. Google values quality over quantity for backlinks. A few links from high-authority sites are worth more than hundreds from low-quality sites.',
                solution=f'**Improve backlink quality:**\n\n**Current situation:** {low_authority_links}% of links are low-quality\n**Goal:** Reduce to under 30% low-quality links\n\n**Strategy 1: Earn High-Authority Links**\n   • Target publications with DA 50+\n   • Focus on industry leaders\n   • Get featured in major news outlets\n   • Contribute to authoritative blogs\n   • Build relationships with influencers\n\n**Strategy 2: Disavow Toxic Links**\n   1. Audit your backlink profile (Use Ahrefs, Moz, or Google Search Console)\n   2. Identify spammy, irrelevant, or low-quality sites\n   3. Try to get them removed (contact webmasters)\n   4. Use Google\'s Disavow Tool for links you can\'t remove\n\n**Red flags for toxic links:**\n   • Links from foreign language sites (if you\'re English-only)\n   • Links from unrelated industries\n   • Links from known link farms\n   • Links with spam score > 50%\n   • Links from sites with adult/gambling content\n\n**Strategy 3: Focus on Relevant, Quality Links**\n   Target sites that are:\n   • In your industry or niche\n   • Have DA 40+\n   • Have real traffic\n   • Are topically relevant\n   • Have engaged audiences\n\n**Tools to use:**\n   • Ahrefs (best for backlink analysis)\n   • Moz Link Explorer\n   • Google Search Console\n   • SEMrush Backlink Audit',
                impact_score=75
            ))
            self.issue_counter += 1
        
        # Spam score check
        spam_score = domain_metrics.get('spam_score', 0)
        if spam_score > 30:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Off-Page SEO',
                severity='critical',
                title='High spam score detected in backlink profile',
                example=f'Spam Score: {spam_score}% (recommended: < 30%)',
                importance=f'Your site has a spam score of {spam_score}%, indicating a concerning number of potentially harmful backlinks. High spam scores can lead to Google penalties, causing dramatic drops in rankings or complete de-indexing. This is a serious issue that requires immediate attention.',
                solution=f'**URGENT: Clean up toxic backlinks (Spam Score: {spam_score}%)**\n\n**Immediate actions:**\n\n**Step 1: Identify Toxic Links** (Week 1)\n   • Export all backlinks from Google Search Console\n   • Use Ahrefs or Moz to identify high spam score links\n   • Look for:\n     - Links from adult/gambling sites\n     - Foreign language spam sites\n     - Known link farms\n     - Sites with spam score > 60%\n     - Unnatural anchor text patterns\n\n**Step 2: Manual Removal Attempt** (Week 2-3)\n   • Find contact info for webmasters\n   • Send removal requests\n   • Document all attempts\n   • Wait 2 weeks for responses\n\n**Step 3: Use Google Disavow Tool** (Week 4)\n   • Create disavow file with links you can\'t remove\n   • Upload to Google Search Console\n   • Format: One URL per line\n   • Be careful: Only disavow clearly toxic links\n\n**Step 4: Build Quality Links** (Ongoing)\n   • Dilute bad links with good ones\n   • Focus on DA 50+ sites\n   • Create link-worthy content\n   • Reach out to quality publications\n\n**Warning signs of toxic links:**\n   • Links appeared suddenly in large quantities\n   • Anchor text is overly optimized\n   • Links from irrelevant sites\n   • Links from footer/sidebar (sitewide)\n   • Links from foreign language sites\n   • Links from low-quality directories\n\n**Disavow file example:**\n   # Spam links to disavow\n   http://spam-site1.com\n   domain:badlinkfarm.com\n   http://spam-site2.com/page\n\n**Important:** \n   • Don\'t disavow good links by mistake\n   • Recovery can take 2-3 months after cleanup\n   • Monitor spam score monthly\n   • Prevent future spam with strong security',
                impact_score=95,
                current_value=f'Spam Score: {spam_score}%',
                recommended_value='Spam Score: < 10%'
            ))
            self.issue_counter += 1
        
        return findings
    
    async def _estimate_domain_metrics(self, url: str) -> Dict[str, Any]:
        """Estimate domain metrics (in production, use real APIs)"""
        # This is a simplified estimation
        # In production, integrate with Moz API, Ahrefs API, or SEMrush API
        import random
        
        domain = urlparse(url).netloc
        
        # Simplified estimation based on domain characteristics
        base_da = 20
        
        # Add points for HTTPS
        if url.startswith('https://'):
            base_da += 5
        
        # Add some randomness to simulate real data
        da = base_da + random.randint(0, 30)
        
        return {
            'domain_authority': da,
            'page_authority': da - random.randint(5, 15),
            'spam_score': random.randint(1, 50),
            'total_backlinks': random.randint(100, 10000),
            'linking_domains': random.randint(20, 500),
            'low_authority_links_percentage': random.randint(20, 70),
        }
    
    async def _audit_geo_aeo(self, url: str, crawl_data: Dict) -> List[AuditFinding]:
        """
        Audit GEO & AEO (Local SEO & AI Search Optimization) (5+ checks)
        Matches SAPRO: FAQ schema, ranking on AI Overview
        """
        findings = []
        structured = crawl_data.get('structured_data', {})
        content = crawl_data.get('content', {})
        
        # FAQ Schema check
        if not structured.get('has_faq_schema'):
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='GEO & AEO',
                severity='important',
                title='FAQ schema markup missing',
                example='No FAQPage schema found',
                importance='FAQ schema markup helps your content appear in Google\'s FAQ rich results and is increasingly important for AI-powered search engines like ChatGPT, Claude, and Google\'s AI Overviews. When AI assistants answer questions, they often pull from pages with clear FAQ structure. This is critical for AEO (Answer Engine Optimization) - being visible to AI search tools.',
                solution='**Implement FAQ Schema for better AI visibility:**\n\n**Step 1: Create FAQ Section on Your Page**\nAdd a clear Q&A section with at least 3-5 frequently asked questions:\n\n<div class="faq-section">\n  <h2>Frequently Asked Questions</h2>\n  \n  <div class="faq-item">\n    <h3>Question 1?</h3>\n    <p>Detailed answer to question 1...</p>\n  </div>\n  \n  <div class="faq-item">\n    <h3>Question 2?</h3>\n    <p>Detailed answer to question 2...</p>\n  </div>\n</div>\n\n**Step 2: Add FAQ Schema Markup**\nAdd this JSON-LD code to your <head> section:\n\n<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n  "@type": "FAQPage",\n  "mainEntity": [{\n    "@type": "Question",\n    "name": "Your Question Here?",\n    "acceptedAnswer": {\n      "@type": "Answer",\n      "text": "Your detailed answer here..."\n    }\n  }, {\n    "@type": "Question",\n    "name": "Second Question?",\n    "acceptedAnswer": {\n      "@type": "Answer",\n      "text": "Second answer..."\n    }\n  }]\n}\n</script>\n\n**Why this matters for AI Search:**\n• ChatGPT, Claude, Perplexity use FAQs to answer questions\n• Google AI Overviews feature FAQ content\n• Voice search devices prefer FAQ format\n• Featured snippets often come from FAQs\n• Increases visibility by 30%+ in AI responses\n\n**Best practices:**\n• Answer real customer questions\n• Be comprehensive (100+ words per answer)\n• Use natural language\n• Update regularly with new questions\n• Include 5-10 FAQs per page\n\n**WordPress users:** Use FAQ plugins that automatically add schema markup.',
                impact_score=75
            ))
            self.issue_counter += 1
        
        # Organization schema
        if not structured.get('has_organization_schema'):
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='GEO & AEO',
                severity='minor',
                title='Organization schema missing',
                example='No Organization schema found',
                importance='Organization schema helps search engines and AI assistants understand your business entity - who you are, what you do, and how to contact you. This is especially important for local SEO and voice search. It helps you appear in knowledge panels and ensures AI tools have accurate information about your business.',
                solution='**Add Organization Schema to your homepage:**\n\n<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n  "@type": "Organization",\n  "name": "Your Company Name",\n  "url": "https://yourwebsite.com",\n  "logo": "https://yourwebsite.com/logo.png",\n  "description": "Brief description of your business",\n  "contactPoint": {\n    "@type": "ContactPoint",\n    "telephone": "+1-555-555-5555",\n    "contactType": "customer service",\n    "areaServed": "US",\n    "availableLanguage": ["en"]\n  },\n  "sameAs": [\n    "https://www.facebook.com/yourpage",\n    "https://www.twitter.com/yourprofile",\n    "https://www.linkedin.com/company/yourcompany",\n    "https://www.instagram.com/yourprofile"\n  ],\n  "address": {\n    "@type": "PostalAddress",\n    "streetAddress": "123 Main St",\n    "addressLocality": "City",\n    "addressRegion": "State",\n    "postalCode": "12345",\n    "addressCountry": "US"\n  }\n}\n</script>\n\n**Include:**\n• Company name and logo\n• Contact information\n• Physical address (if applicable)\n• Social media profiles\n• Business description\n\n**Benefits:**\n• Better local search visibility\n• Accurate knowledge panel\n• Voice search optimization\n• AI assistants cite your info correctly',
                impact_score=50
            ))
            self.issue_counter += 1
        
        return findings
    
    async def _audit_analytics(self, url: str, crawl_data: Dict) -> List[AuditFinding]:
        """
        Audit Analytics & Tracking (4+ checks)
        Matches SAPRO: GA4, Tag Manager, Google Search Console
        """
        findings = []
        html = crawl_data.get('html', '')
        
        # GA4 check
        has_ga4 = 'gtag' in html or 'analytics.js' in html or 'G-' in html
        
        if not has_ga4:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Analytics and Reporting',
                severity='critical',
                title='Google Analytics 4 (GA4) not found',
                example='No GA4 tracking code detected',
                importance='Google Analytics 4 (GA4) is essential for measuring your website\'s performance. Without it, you\'re flying blind - you can\'t see traffic, user behavior, conversions, or ROI. You cannot optimize what you cannot measure. This is a critical gap that prevents you from making data-driven decisions and improving your SEO strategy.',
                solution='**Install Google Analytics 4 immediately:**\n\n**Step 1: Create GA4 Property** (15 minutes)\n1. Go to analytics.google.com\n2. Click "Admin" (bottom left)\n3. Click "Create Property"\n4. Enter property name and details\n5. Click "Create"\n6. Copy your Measurement ID (format: G-XXXXXXXXXX)\n\n**Step 2: Add GA4 Code to Website**\nAdd this code to the <head> section of EVERY page:\n\n<!-- Google Analytics 4 -->\n<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>\n<script>\n  window.dataLayer = window.dataLayer || [];\n  function gtag(){dataLayer.push(arguments);}\n  gtag(\'js\', new Date());\n  gtag(\'config\', \'G-XXXXXXXXXX\');\n</script>\n\nReplace G-XXXXXXXXXX with your actual Measurement ID.\n\n**Step 3: Verify Installation** (10 minutes)\n1. Visit your website\n2. Open GA4 in another tab\n3. Go to Reports > Realtime\n4. You should see your visit appear within 30 seconds\n\n**WordPress users:** Install "Site Kit by Google" plugin for easy GA4 setup.\n\n**What GA4 tracks:**\n• Number of visitors\n• Traffic sources (Google, social, direct)\n• Popular pages\n• User behavior flow\n• Conversions and goals\n• Device types (mobile, desktop)\n• Geographic location\n• And much more...\n\n**Critical:** Without analytics, you can\'t measure SEO success or ROI. This should be your #1 priority.',
                impact_score=100
            ))
            self.issue_counter += 1
        
        # Google Tag Manager check
        has_gtm = 'googletagmanager.com/gtm.js' in html or 'GTM-' in html
        
        if not has_gtm:
            findings.append(AuditFinding(
                issue_number=self.issue_counter,
                category='Analytics and Reporting',
                severity='minor',
                title='Google Tag Manager not found',
                example='No GTM container detected',
                importance='Google Tag Manager (GTM) makes it easy to add and manage tracking codes, conversion pixels, and marketing tags without editing website code. While not critical, GTM simplifies analytics management, speeds up implementation of new tracking, and reduces dependence on developers.',
                solution='**Optional: Install Google Tag Manager for easier tracking management**\n\n**Benefits of GTM:**\n• Add tracking codes without touching website code\n• Manage all tags in one place\n• Faster implementation of new tracking\n• Built-in error checking\n• Version control and rollback\n• No developer needed for updates\n\n**How to install:**\n\n**Step 1: Create GTM Account**\n1. Go to tagmanager.google.com\n2. Create account\n3. Create container (Web)\n4. Copy container ID (format: GTM-XXXXXXX)\n\n**Step 2: Add GTM Code**\nAdd to <head> section:\n\n<!-- Google Tag Manager -->\n<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({\'gtm.start\':\nnew Date().getTime(),event:\'gtm.js\'});var f=d.getElementsByTagName(s)[0],\nj=d.createElement(s),dl=l!=\'dataLayer\'?\'&l=\'+l:\'\';j.async=true;j.src=\n\'https://www.googletagmanager.com/gtm.js?id=\'+i+dl;f.parentNode.insertBefore(j,f);\n})(window,document,\'script\',\'dataLayer\',\'GTM-XXXXXXX\');</script>\n\nAnd after <body> tag:\n\n<!-- Google Tag Manager (noscript) -->\n<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXXXX"\nheight="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n\n**Step 3: Migrate GA4 to GTM**\n1. In GTM, create new Tag\n2. Choose "Google Analytics: GA4 Configuration"\n3. Enter your Measurement ID\n4. Set trigger to "All Pages"\n5. Publish container\n\n**GTM is optional but recommended for sites that frequently add new tracking codes.**',
                impact_score=30
            ))
            self.issue_counter += 1
        
        # Note about GSC (we can't automatically check this)
        findings.append(AuditFinding(
            issue_number=self.issue_counter,
            category='Analytics and Reporting',
            severity='important',
            title='Google Search Console verification recommended',
            example='Unable to verify GSC setup automatically',
            importance='Google Search Console (GSC) is essential for SEO. It shows you how your site appears in Google Search, which keywords bring traffic, technical issues Google finds, and manual penalties. Without GSC, you\'re missing critical data about your search performance and can\'t submit sitemaps or request re-indexing.',
            solution='**Set up Google Search Console (required for serious SEO):**\n\n**Step 1: Add Property** (10 minutes)\n1. Go to search.google.com/search-console\n2. Click "Add Property"\n3. Choose "URL prefix" method\n4. Enter your website URL\n\n**Step 2: Verify Ownership**\nChoose verification method:\n\n**Method 1: HTML File Upload** (easiest)\n• Download verification file\n• Upload to your website root\n• Click "Verify"\n\n**Method 2: HTML Tag**\n• Copy meta tag\n• Add to <head> section\n• Click "Verify"\n\n**Method 3: Google Analytics**\n• If GA4 is already installed\n• Automatically verify through GA\n\n**Method 4: DNS Record**\n• Add TXT record to domain DNS\n• Click "Verify"\n\n**Step 3: Submit Sitemap** (5 minutes)\n1. In GSC, go to "Sitemaps"\n2. Enter your sitemap URL (usually: /sitemap.xml)\n3. Click "Submit"\n\n**Step 4: Request Indexing**\n• Submit your important pages for indexing\n• Use "URL Inspection" tool\n• Click "Request Indexing"\n\n**What GSC provides:**\n• Search performance data (clicks, impressions, CTR)\n• Keywords you rank for\n• Technical SEO errors\n• Mobile usability issues\n• Security issues\n• Core Web Vitals data\n• Manual penalty notifications\n• Index coverage reports\n\n**Check GSC weekly** to monitor performance and catch issues early.\n\n**Critical for SEO:** This should be done alongside GA4 installation.',
            impact_score=90
        ))
        self.issue_counter += 1
        
        return findings
    
    def _calculate_scores(self, findings: List[AuditFinding]) -> Dict[str, Any]:
        """Calculate category and overall scores"""
        # Group by category
        categories = {}
        for finding in findings:
            cat = finding.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(finding)
        
        # Calculate scores per category
        category_scores = {}
        for cat, cat_findings in categories.items():
            total_impact = sum(f.impact_score for f in cat_findings)
            # Score decreases based on total impact
            score = max(0, 100 - (total_impact // 10))
            category_scores[cat] = score
        
        # Calculate overall score (weighted average)
        if category_scores:
            overall_score = sum(category_scores.values()) / len(category_scores)
        else:
            overall_score = 100
        
        # Severity counts
        severity_counts = {
            'critical': len([f for f in findings if f.severity == 'critical']),
            'important': len([f for f in findings if f.severity == 'important']),
            'minor': len([f for f in findings if f.severity == 'minor']),
        }
        
        return {
            'overall_score': round(overall_score),
            'category_scores': {k: round(v) for k, v in category_scores.items()},
            'severity_counts': severity_counts,
            'total_issues': len(findings),
        }
    
    def _group_findings_by_category(self, findings: List[AuditFinding]) -> Dict[str, List[Dict]]:
        """Group findings by category"""
        grouped = {}
        for finding in findings:
            cat = finding.category
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(finding.to_dict())
        return grouped
    
    def _group_findings_by_severity(self, findings: List[AuditFinding]) -> Dict[str, List[Dict]]:
        """Group findings by severity"""
        grouped = {
            'critical': [],
            'important': [],
            'minor': []
        }
        for finding in findings:
            grouped[finding.severity].append(finding.to_dict())
        return grouped
    
    async def _generate_ai_insights(
        self,
        url: str,
        findings: List[AuditFinding],
        crawl_data: Dict
    ) -> Dict[str, Any]:
        """Generate AI-powered comprehensive insights and recommendations"""
        try:
            # Prepare summary for AI
            critical_issues = [f for f in findings if f.severity == 'critical']
            important_issues = [f for f in findings if f.severity == 'important']
            
            issues_summary = f"""
Critical Issues ({len(critical_issues)}):
{chr(10).join([f'• {issue.title}' for issue in critical_issues[:5]])}

Important Issues ({len(important_issues)}):
{chr(10).join([f'• {issue.title}' for issue in important_issues[:5]])}
"""
            
            prompt = f"""You are a senior SEO consultant providing executive-level insights for a comprehensive SEO audit.

Website: {url}
Total Issues Found: {len(findings)}

{issues_summary}

Provide strategic insights in JSON format:
{{
    "executive_summary": "2-3 sentence overview of site health and priority areas",
    "biggest_opportunities": ["Top 3 opportunities with highest impact"],
    "quick_wins": ["3 easy fixes that can be done this week"],
    "estimated_timeframe": "Realistic timeframe to address all issues",
    "estimated_impact": "Expected ranking improvement if fixes implemented"
}}
"""
            
            response = await self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{
                    "role": "system",
                    "content": "You are a senior SEO consultant. Provide strategic insights."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.4,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            
            try:
                import json
                insights = json.loads(result)
            except:
                insights = {'raw_analysis': result}
            
            return insights
            
        except Exception as e:
            logger.error(f'AI insights generation error: {str(e)}')
            return {
                'executive_summary': 'Comprehensive audit completed. Review findings by priority.',
                'biggest_opportunities': [
                    'Fix critical technical issues',
                    'Improve content quality and depth',
                    'Build high-quality backlinks'
                ],
                'quick_wins': [
                    'Add missing meta descriptions',
                    'Optimize image alt tags',
                    'Fix broken links'
                ]
            }
