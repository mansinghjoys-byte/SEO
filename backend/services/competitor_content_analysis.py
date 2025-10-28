"""
Competitor Content Analysis Service
Analyzes competitor content strategy and identifies opportunities
"""
from typing import Dict, List, Any, Optional
import logging
import asyncio
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from exa_py import Exa
from groq import AsyncGroq
from core.config import get_settings
import re
from collections import Counter

logger = logging.getLogger(__name__)
settings = get_settings()


class CompetitorContentService:
    """Service for analyzing competitor content"""
    
    def __init__(self):
        self.exa_client = Exa(api_key=settings.EXA_API_KEY) if settings.EXA_API_KEY else None
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def analyze_competitor_content(
        self,
        competitor_domain: str,
        your_domain: str,
        keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze competitor's content strategy
        """
        try:
            logger.info(f"Analyzing content for competitor: {competitor_domain}")
            
            # Discover top content
            top_content = await self._discover_top_content(competitor_domain, keywords)
            
            # Analyze content themes
            content_themes = self._analyze_content_themes(top_content)
            
            # Find content gaps
            content_gaps = await self._find_content_gaps(
                competitor_domain,
                your_domain,
                top_content,
                keywords
            )
            
            # Analyze content quality
            quality_metrics = self._analyze_content_quality(top_content)
            
            # Schema markup analysis
            schema_analysis = await self._analyze_schema_markup(competitor_domain, top_content)
            
            # AI insights
            insights = await self._generate_content_insights(
                top_content,
                content_themes,
                content_gaps,
                quality_metrics,
                your_domain,
                competitor_domain
            )
            
            return {
                'success': True,
                'competitor_domain': competitor_domain,
                'your_domain': your_domain,
                'top_content': top_content[:20],  # Top 20 pages
                'content_themes': content_themes,
                'content_gaps': content_gaps,
                'quality_metrics': quality_metrics,
                'schema_analysis': schema_analysis,
                'insights': insights,
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f'Competitor content analysis error: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    async def _discover_top_content(
        self,
        domain: str,
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """Discover top performing content"""
        content = []
        
        try:
            # Method 1: Exa.ai content discovery
            if self.exa_client:
                for keyword in keywords[:5]:  # Top 5 keywords
                    try:
                        query = f'{keyword} site:{domain}'
                        results = self.exa_client.search_and_contents(
                            query,
                            num_results=5,
                            use_autoprompt=True
                        )
                        
                        for result in results.results:
                            text_content = result.text if hasattr(result, 'text') else ''
                            
                            content.append({
                                'url': result.url,
                                'title': result.title or '',
                                'keyword': keyword,
                                'text': text_content[:500],
                                'word_count': len(text_content.split()) if text_content else 0,
                                'headings': self._extract_headings(text_content),
                                'estimated_traffic': 'high',
                                'discovery_method': 'exa_ai'
                            })
                    
                    except Exception as e:
                        logger.warning(f'Exa content discovery error for "{keyword}": {str(e)}')
            
            # Method 2: Web scraping sitemap
            sitemap_content = await self._scrape_sitemap(domain)
            content.extend(sitemap_content)
            
            # Method 3: Direct page scraping
            main_pages = await self._scrape_main_pages(domain)
            content.extend(main_pages)
        
        except Exception as e:
            logger.error(f'Content discovery error: {str(e)}')
        
        # Deduplicate by URL
        seen_urls = set()
        unique_content = []
        for item in content:
            url = item.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_content.append(item)
        
        return unique_content
    
    async def _scrape_sitemap(self, domain: str) -> List[Dict[str, Any]]:
        """Scrape sitemap for content URLs"""
        content = []
        
        try:
            sitemap_urls = [
                f'https://{domain}/sitemap.xml',
                f'https://{domain}/sitemap_index.xml',
                f'https://{domain}/sitemap-0.xml'
            ]
            
            for sitemap_url in sitemap_urls:
                try:
                    response = requests.get(sitemap_url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'xml')
                        urls = soup.find_all('loc')
                        
                        for url in urls[:10]:  # First 10 URLs
                            url_text = url.get_text()
                            
                            # Skip non-content URLs
                            if any(skip in url_text for skip in ['/tag/', '/category/', '/author/']):
                                continue
                            
                            content.append({
                                'url': url_text,
                                'title': self._extract_title_from_url(url_text),
                                'discovery_method': 'sitemap'
                            })
                        
                        break  # Found sitemap, exit loop
                
                except Exception:
                    continue
        
        except Exception as e:
            logger.warning(f'Sitemap scraping error: {str(e)}')
        
        return content
    
    async def _scrape_main_pages(self, domain: str) -> List[Dict[str, Any]]:
        """Scrape main pages of competitor site"""
        content = []
        
        try:
            url = f'https://{domain}'
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all internal links
                links = soup.find_all('a', href=True)
                
                for link in links[:15]:  # First 15 links
                    href = link['href']
                    
                    # Convert relative to absolute
                    if href.startswith('/'):
                        href = f'https://{domain}{href}'
                    
                    # Only internal links
                    if domain in href:
                        title = link.get_text().strip()
                        
                        if title and len(title) > 5:
                            content.append({
                                'url': href,
                                'title': title,
                                'discovery_method': 'homepage_scraping'
                            })
        
        except Exception as e:
            logger.warning(f'Main page scraping error: {str(e)}')
        
        return content
    
    def _analyze_content_themes(self, content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content themes and topics"""
        all_text = ' '.join([item.get('title', '') + ' ' + item.get('text', '') for item in content])
        words = re.findall(r'\b\w+\b', all_text.lower())
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        filtered_words = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # Count frequencies
        word_freq = Counter(filtered_words)
        top_themes = word_freq.most_common(20)
        
        # Group into themes
        themes = {
            'top_keywords': [{'keyword': k, 'frequency': v} for k, v in top_themes[:10]],
            'content_types': self._identify_content_types(content),
            'topic_clusters': self._identify_topic_clusters(top_themes)
        }
        
        return themes
    
    def _identify_content_types(self, content: List[Dict[str, Any]]) -> List[Dict[str, int]]:
        """Identify types of content"""
        types = {
            'blog': 0,
            'guide': 0,
            'tutorial': 0,
            'review': 0,
            'comparison': 0,
            'listicle': 0,
            'case_study': 0,
            'product': 0
        }
        
        for item in content:
            title = item.get('title', '').lower()
            
            if 'how to' in title or 'guide' in title:
                types['guide'] += 1
            elif 'tutorial' in title:
                types['tutorial'] += 1
            elif 'review' in title:
                types['review'] += 1
            elif 'vs' in title or 'versus' in title or 'comparison' in title:
                types['comparison'] += 1
            elif any(num in title for num in ['top ', 'best ', 'list of']):
                types['listicle'] += 1
            elif 'case study' in title or 'success story' in title:
                types['case_study'] += 1
            else:
                types['blog'] += 1
        
        return [{'type': k, 'count': v} for k, v in types.items() if v > 0]
    
    def _identify_topic_clusters(self, themes: List[tuple]) -> List[str]:
        """Identify topic clusters"""
        # Group related keywords
        clusters = []
        
        # Simple clustering based on keyword similarity
        # In production, use more sophisticated clustering
        keywords = [k for k, v in themes]
        
        # Just return top keywords as clusters for now
        clusters = keywords[:5]
        
        return clusters
    
    async def _find_content_gaps(
        self,
        competitor_domain: str,
        your_domain: str,
        competitor_content: List[Dict[str, Any]],
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """Find content gaps"""
        gaps = []
        
        # Topics competitor covers that you might not
        competitor_topics = set()
        for item in competitor_content:
            title = item.get('title', '').lower()
            # Extract topic from title
            topic = re.sub(r'[^\w\s]', '', title)
            competitor_topics.add(topic)
        
        # Identify gaps (simplified)
        for topic in list(competitor_topics)[:10]:
            gaps.append({
                'topic': topic,
                'competitor_coverage': 'yes',
                'your_coverage': 'unknown',  # Would need to check your content
                'opportunity_score': 85,
                'recommended_action': 'Create comprehensive content on this topic',
                'content_type': 'article'
            })
        
        # Keyword gaps
        for keyword in keywords[:5]:
            has_content = any(keyword.lower() in item.get('title', '').lower() for item in competitor_content)
            
            if has_content:
                gaps.append({
                    'topic': f'Content about "{keyword}"',
                    'competitor_coverage': 'yes',
                    'your_coverage': 'check',
                    'opportunity_score': 90,
                    'recommended_action': f'Create in-depth content targeting "{keyword}"',
                    'content_type': 'guide'
                })
        
        return gaps[:15]  # Top 15 gaps
    
    def _analyze_content_quality(self, content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content quality metrics"""
        if not content:
            return {
                'average_word_count': 0,
                'average_headings': 0,
                'content_depth': 'unknown'
            }
        
        word_counts = [item.get('word_count', 0) for item in content if item.get('word_count')]
        headings_counts = [len(item.get('headings', [])) for item in content]
        
        avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
        avg_headings = sum(headings_counts) / len(headings_counts) if headings_counts else 0
        
        # Determine content depth
        if avg_words > 2000:
            depth = 'very_deep'
        elif avg_words > 1000:
            depth = 'deep'
        elif avg_words > 500:
            depth = 'medium'
        else:
            depth = 'shallow'
        
        return {
            'average_word_count': int(avg_words),
            'average_headings': round(avg_headings, 1),
            'content_depth': depth,
            'total_content_analyzed': len(content),
            'recommendation': self._get_quality_recommendation(depth, avg_words)
        }
    
    def _get_quality_recommendation(self, depth: str, avg_words: int) -> str:
        """Get quality recommendation"""
        if depth == 'very_deep':
            return f'Competitor creates very comprehensive content (avg {int(avg_words)} words). Match or exceed this depth.'
        elif depth == 'deep':
            return f'Competitor creates in-depth content (avg {int(avg_words)} words). Aim for similar depth.'
        elif depth == 'medium':
            return f'Competitor creates moderate-length content (avg {int(avg_words)} words). Consider creating more comprehensive pieces.'
        else:
            return f'Competitor creates short content (avg {int(avg_words)} words). Opportunity to create more in-depth content.'
    
    async def _analyze_schema_markup(
        self,
        domain: str,
        content: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze competitor's schema markup usage"""
        schema_types = []
        
        try:
            # Sample a few URLs
            for item in content[:3]:
                url = item.get('url')
                if not url:
                    continue
                
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Find JSON-LD scripts
                        scripts = soup.find_all('script', type='application/ld+json')
                        
                        for script in scripts:
                            try:
                                import json
                                schema_data = json.loads(script.string)
                                
                                if isinstance(schema_data, dict):
                                    schema_type = schema_data.get('@type', 'Unknown')
                                    if schema_type not in schema_types:
                                        schema_types.append(schema_type)
                                elif isinstance(schema_data, list):
                                    for item in schema_data:
                                        if isinstance(item, dict):
                                            schema_type = item.get('@type', 'Unknown')
                                            if schema_type not in schema_types:
                                                schema_types.append(schema_type)
                            
                            except:
                                continue
                    
                    await asyncio.sleep(1)  # Rate limiting
                
                except Exception:
                    continue
        
        except Exception as e:
            logger.warning(f'Schema analysis error: {str(e)}')
        
        return {
            'uses_schema': len(schema_types) > 0,
            'schema_types': schema_types,
            'recommendation': 'Implement similar schema markup' if schema_types else 'Opportunity to add schema markup for competitive advantage'
        }
    
    async def _generate_content_insights(
        self,
        content: List[Dict[str, Any]],
        themes: Dict[str, Any],
        gaps: List[Dict[str, Any]],
        quality: Dict[str, Any],
        your_domain: str,
        competitor_domain: str
    ) -> Dict[str, Any]:
        """Generate AI-powered content insights"""
        try:
            prompt = f"""Analyze competitor content strategy and provide actionable insights:

Competitor: {competitor_domain}
Your Domain: {your_domain}

Content Analysis:
- Total Content Pieces: {len(content)}
- Average Word Count: {quality.get('average_word_count')}
- Content Depth: {quality.get('content_depth')}
- Top Topics: {', '.join([t['keyword'] for t in themes.get('top_keywords', [])[:5]])}
- Content Gaps Identified: {len(gaps)}

Provide in JSON:
{{
    "content_strategy": "Brief description of competitor's content strategy",
    "your_opportunities": ["opportunity 1", "opportunity 2", "opportunity 3"],
    "quick_wins": ["actionable content idea 1", "actionable content idea 2", "actionable content idea 3"],
    "content_upgrade_plan": "How to improve your content strategy",
    "competitive_edge": "How to gain content advantage"
}}"""

            response = await self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a content strategist analyzing competitor content. Provide actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            import json
            insights = json.loads(response.choices[0].message.content)
            return insights
        
        except Exception as e:
            logger.warning(f'Content insight generation error: {str(e)}')
            return {
                'content_strategy': 'Competitor focuses on comprehensive, in-depth content',
                'your_opportunities': ['Create longer-form content', 'Cover untapped topics', 'Improve content structure'],
                'quick_wins': ['Write how-to guides', 'Create comparison articles', 'Add more visual content'],
                'content_upgrade_plan': 'Focus on depth, quality, and comprehensive coverage',
                'competitive_edge': 'Create more authoritative and comprehensive content'
            }
    
    def _extract_headings(self, text: str) -> List[str]:
        """Extract potential headings from text"""
        # Simple extraction - look for capitalized phrases
        sentences = text.split('.')
        headings = []
        
        for sentence in sentences[:10]:
            sentence = sentence.strip()
            if sentence and len(sentence) < 100 and sentence[0].isupper():
                headings.append(sentence)
        
        return headings[:5]
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract title from URL slug"""
        try:
            # Get the last part of the URL
            slug = url.rstrip('/').split('/')[-1]
            # Remove extension
            slug = slug.split('.')[0]
            # Replace hyphens with spaces and title case
            title = slug.replace('-', ' ').replace('_', ' ').title()
            return title
        except:
            return url
