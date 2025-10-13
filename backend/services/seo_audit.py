from abc import ABC, abstractmethod
from typing import Dict, Any, List
import httpx
import re
from urllib.parse import urlparse
import asyncio
from core.config import get_settings
from schemas.schemas import AuditIssue
from services.crawler import WebCrawler
from services.advanced_crawler import AdvancedSEOCrawler
from groq import AsyncGroq

settings = get_settings()

class BaseAnalyzer(ABC):
    """Base class for SEO analyzers (Open/Closed Principle)"""
    
    @abstractmethod
    async def analyze(self, url: str, content: str = None) -> List[AuditIssue]:
        pass

class TechnicalSEOAnalyzer(BaseAnalyzer):
    """Analyzes technical SEO aspects"""
    
    async def analyze(self, url: str, content: str = None, crawl_data: Dict = None) -> List[AuditIssue]:
        issues = []
        
        if not crawl_data:
            return issues
        
        technical = crawl_data.get('technical', {})
        performance = crawl_data.get('performance', {})
        mobile = crawl_data.get('mobile', {})
        
        # Check HTTPS
        if not technical.get('https'):
            issues.append(AuditIssue(
                category='technical',
                severity='high',
                title='Missing HTTPS',
                description='Site is not using HTTPS encryption',
                fix='Install SSL certificate and redirect HTTP to HTTPS',
                impact_score=80
            ))
        
        # Check page speed
        load_time = performance.get('load_time_seconds', 0)
        if load_time > 3:
            issues.append(AuditIssue(
                category='technical',
                severity='high',
                title='Slow Page Load Time',
                description=f'Page loads in {load_time} seconds (should be <3s)',
                fix='Optimize images, enable caching, use CDN, minify CSS/JS',
                impact_score=75
            ))
        
        # Check mobile viewport
        if not mobile.get('has_viewport'):
            issues.append(AuditIssue(
                category='technical',
                severity='medium',
                title='Missing Mobile Viewport',
                description='No viewport meta tag found',
                fix='Add <meta name="viewport" content="width=device-width, initial-scale=1">',
                impact_score=60
            ))
        elif not mobile.get('is_responsive'):
            issues.append(AuditIssue(
                category='technical',
                severity='medium',
                title='Non-Responsive Viewport',
                description='Viewport meta tag exists but may not be properly configured',
                fix='Ensure viewport contains: width=device-width, initial-scale=1',
                impact_score=55
            ))
        
        # Check redirects
        if technical.get('redirects', 0) > 2:
            issues.append(AuditIssue(
                category='technical',
                severity='medium',
                title='Multiple Redirects',
                description=f'Page has {technical.get("redirects")} redirects',
                fix='Reduce redirect chains to improve load speed',
                impact_score=45
            ))
        
        # Check canonical
        if not technical.get('has_canonical'):
            issues.append(AuditIssue(
                category='technical',
                severity='low',
                title='Missing Canonical Tag',
                description='No canonical URL specified',
                fix='Add canonical tag to prevent duplicate content issues',
                impact_score=35
            ))
        
        # Check HTML size
        if not performance.get('is_optimal_size'):
            size_kb = performance.get('html_size_kb', 0)
            issues.append(AuditIssue(
                category='technical',
                severity='low',
                title='Large HTML Size',
                description=f'HTML size is {size_kb}KB (optimal: <100KB)',
                fix='Minify HTML, remove unnecessary code, optimize inline styles',
                impact_score=30
            ))
        
        return issues

class OnPageSEOAnalyzer(BaseAnalyzer):
    """Analyzes on-page SEO elements"""
    
    async def analyze(self, url: str, content: str = None, crawl_data: Dict = None) -> List[AuditIssue]:
        issues = []
        
        if not crawl_data:
            return issues
        
        meta = crawl_data.get('meta', {})
        content_data = crawl_data.get('content', {})
        images = crawl_data.get('images', {})
        
        # Check title tag
        title = meta.get('title', '')
        title_length = meta.get('title_length', 0)
        
        if not meta.get('has_title'):
            issues.append(AuditIssue(
                category='on-page',
                severity='critical',
                title='Missing Title Tag',
                description='No title tag found on the page',
                fix='Add a unique, descriptive title tag (50-60 characters)',
                impact_score=100
            ))
        elif title_length < 30:
            issues.append(AuditIssue(
                category='on-page',
                severity='medium',
                title='Title Tag Too Short',
                description=f'Title is only {title_length} characters (recommended: 50-60)',
                fix='Expand title to include more descriptive keywords',
                impact_score=50
            ))
        elif title_length > 60:
            issues.append(AuditIssue(
                category='on-page',
                severity='medium',
                title='Title Tag Too Long',
                description=f'Title is {title_length} characters (recommended: 50-60)',
                fix='Shorten title to avoid truncation in search results',
                impact_score=50
            ))
        
        # Check meta description
        description_length = meta.get('description_length', 0)
        if not meta.get('has_description'):
            issues.append(AuditIssue(
                category='on-page',
                severity='high',
                title='Missing Meta Description',
                description='No meta description found',
                fix='Add compelling meta description (150-160 characters)',
                impact_score=70
            ))
        elif description_length < 120:
            issues.append(AuditIssue(
                category='on-page',
                severity='low',
                title='Meta Description Too Short',
                description=f'Description is {description_length} characters (optimal: 150-160)',
                fix='Expand description to provide more context',
                impact_score=30
            ))
        elif description_length > 160:
            issues.append(AuditIssue(
                category='on-page',
                severity='low',
                title='Meta Description Too Long',
                description=f'Description is {description_length} characters (optimal: 150-160)',
                fix='Shorten description to prevent truncation',
                impact_score=30
            ))
        
        # Check H1 tag
        h1_count = content_data.get('h1_count', 0)
        if h1_count == 0:
            issues.append(AuditIssue(
                category='on-page',
                severity='high',
                title='Missing H1 Tag',
                description='No H1 heading found on the page',
                fix='Add a single, keyword-rich H1 tag at the top of your content',
                impact_score=75
            ))
        elif h1_count > 1:
            issues.append(AuditIssue(
                category='on-page',
                severity='medium',
                title='Multiple H1 Tags',
                description=f'Found {h1_count} H1 tags (should have only 1)',
                fix='Use only one H1 tag per page for main heading',
                impact_score=40
            ))
        
        # Check heading structure
        if not content_data.get('has_heading_structure'):
            issues.append(AuditIssue(
                category='on-page',
                severity='low',
                title='Weak Heading Structure',
                description='Page lacks proper heading hierarchy',
                fix='Implement logical heading structure (H1 > H2 > H3)',
                impact_score=35
            ))
        
        # Check images without alt tags
        images_without_alt = images.get('images_without_alt', 0)
        if images_without_alt > 0:
            issues.append(AuditIssue(
                category='on-page',
                severity='medium',
                title='Images Missing Alt Text',
                description=f'{images_without_alt} images found without alt attributes',
                fix='Add descriptive alt text to all images for accessibility and SEO',
                impact_score=55
            ))
        
        # Check content length
        word_count = content_data.get('word_count', 0)
        if word_count < 300:
            issues.append(AuditIssue(
                category='on-page',
                severity='medium',
                title='Thin Content',
                description=f'Page has only {word_count} words (recommended: 300+)',
                fix='Add more comprehensive, valuable content to the page',
                impact_score=60
            ))
        
        return issues

class OffPageSEOAnalyzer(BaseAnalyzer):
    """Analyzes off-page SEO factors"""
    
    async def analyze(self, url: str, content: str = None, crawl_data: Dict = None) -> List[AuditIssue]:
        issues = []
        
        if not crawl_data:
            return issues
        
        meta = crawl_data.get('meta', {})
        structured_data = crawl_data.get('structured_data', {})
        
        # Check social signals (Open Graph)
        if not meta.get('has_og_tags'):
            issues.append(AuditIssue(
                category='off-page',
                severity='medium',
                title='Missing Open Graph Tags',
                description='No Open Graph meta tags for social sharing',
                fix='Add og:title, og:description, og:image tags for better social media appearance',
                impact_score=45
            ))
        
        # Check Twitter Card
        if not meta.get('has_twitter_card'):
            issues.append(AuditIssue(
                category='off-page',
                severity='low',
                title='Missing Twitter Card',
                description='No Twitter Card meta tags found',
                fix='Add Twitter Card tags for better Twitter sharing',
                impact_score=30
            ))
        
        # Check structured data
        if not structured_data.get('has_json_ld') and not structured_data.get('has_microdata'):
            issues.append(AuditIssue(
                category='off-page',
                severity='medium',
                title='Missing Structured Data',
                description='No Schema.org structured data found',
                fix='Add JSON-LD structured data for better rich snippet appearance',
                impact_score=50
            ))
        
        return issues

class SEOAuditService:
    """Main service orchestrating all SEO analyses"""
    
    def __init__(self):
        self.analyzers: List[BaseAnalyzer] = [
            TechnicalSEOAnalyzer(),
            OnPageSEOAnalyzer(),
            OffPageSEOAnalyzer()
        ]
        self.crawler = WebCrawler()
    
    async def run_audit(self, url: str) -> Dict[str, Any]:
        """Run comprehensive SEO audit with real crawler"""
        
        # Crawl the website
        crawl_data = await self.crawler.crawl_and_analyze(url)
        
        if not crawl_data.get('success'):
            # Return error if crawl failed
            error_msg = crawl_data.get('error', 'Unknown error')
            return {
                'seo_score': 0,
                'technical_score': 0,
                'onpage_score': 0,
                'offpage_score': 0,
                'issues': [AuditIssue(
                    category='technical',
                    severity='critical',
                    title='Site Unreachable',
                    description=f'Unable to crawl site: {error_msg}',
                    fix='Check if the site is online and accessible. Ensure URL is correct.',
                    impact_score=100
                )],
                'recommendations': ['Fix site accessibility issues before running SEO analysis'],
                'crawl_data': crawl_data
            }
        
        all_issues = []
        
        # Run all analyzers with crawl data
        for analyzer in self.analyzers:
            issues = await analyzer.analyze(url, None, crawl_data)
            all_issues.extend(issues)
        
        # Calculate scores
        total_impact = sum(issue.impact_score for issue in all_issues)
        seo_score = max(0, 100 - (total_impact // 10))
        
        technical_issues = [i for i in all_issues if i.category == 'technical']
        onpage_issues = [i for i in all_issues if i.category == 'on-page']
        offpage_issues = [i for i in all_issues if i.category == 'off-page']
        
        technical_score = max(0, 100 - sum(i.impact_score for i in technical_issues) // 5)
        onpage_score = max(0, 100 - sum(i.impact_score for i in onpage_issues) // 5)
        offpage_score = max(0, 100 - sum(i.impact_score for i in offpage_issues) // 5)
        
        # Generate AI recommendations with real data
        recommendations = await self._generate_recommendations(all_issues, crawl_data)
        
        return {
            'seo_score': seo_score,
            'technical_score': technical_score,
            'onpage_score': onpage_score,
            'offpage_score': offpage_score,
            'issues': all_issues,
            'recommendations': recommendations,
            'crawl_data': crawl_data  # Include for AI agents
        }
    
    async def _generate_recommendations(self, issues: List[AuditIssue], crawl_data: Dict) -> List[str]:
        """Generate prioritized recommendations using AI and crawl data"""
        if not issues:
            return ['Excellent! No critical issues found. Continue monitoring your SEO performance.']
        
        # Generate detailed AI-powered recommendations
        try:
            groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            
            # Prepare issue summary for AI
            issues_summary = []
            for issue in issues[:10]:  # Top 10 issues
                issues_summary.append({
                    'title': issue.title,
                    'severity': issue.severity,
                    'description': issue.description,
                    'category': issue.category
                })
            
            meta = crawl_data.get('meta', {})
            content_data = crawl_data.get('content', {})
            
            prompt = f"""You are an SEO expert helping a beginner improve their website. Analyze these issues and provide DETAILED, STEP-BY-STEP recommendations that anyone can follow without technical knowledge.

Website Issues Found:
{issues_summary}

Current Stats:
- Title: {meta.get('title', 'Missing')}
- Description: {meta.get('description', 'Missing')}
- Word Count: {content_data.get('word_count', 0)}
- H1 Tags: {content_data.get('h1_count', 0)}

Provide 8-10 detailed recommendations in this EXACT format (each as a separate item):

1. **[Category] Issue Name** - [Why it matters]
   • Step 1: [Exact action to take]
   • Step 2: [Next action]
   • Step 3: [Final action]
   📌 Example: [Show a concrete example]
   ⏱️ Time needed: [5 mins/30 mins/1 hour]
   🎯 Impact: [High/Medium/Low] - [What will improve]

Make it BEGINNER-FRIENDLY with:
- Simple language (avoid jargon)
- Exact steps they can follow
- Real examples they can copy
- Why it matters for rankings
- How long it takes

Focus on the HIGHEST IMPACT issues first."""

            response = await groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{
                    "role": "system",
                    "content": "You are a patient SEO teacher helping beginners improve their websites. Provide detailed, actionable steps."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=2000
            )
            
            ai_recommendations = response.choices[0].message.content
            
            # Return as single text block for better formatting
            return [ai_recommendations]
            
        except Exception as e:
            # Fallback to basic recommendations
            recommendations = []
            
            # Sort by severity and impact
            critical = [i for i in issues if i.severity == 'critical']
            high = [i for i in issues if i.severity == 'high']
            
            if critical:
                recommendations.append(f'🔴 CRITICAL: Fix {len(critical)} critical issues immediately - these are blocking your SEO performance')
            
            if high:
                recommendations.append(f'🟠 HIGH PRIORITY: Address {len(high)} high-priority issues this week')
            
            # Add specific data-driven recommendations
            meta = crawl_data.get('meta', {})
            content_data = crawl_data.get('content', {})
            performance = crawl_data.get('performance', {})
            
            # Content recommendations
            word_count = content_data.get('word_count', 0)
            if word_count < 500:
                recommendations.append(f'📝 Content: Expand content from {word_count} to at least 500 words for better rankings')
            
            # Performance recommendations
            load_time = performance.get('load_time_seconds', 0)
            if load_time > 2:
                recommendations.append(f'⚡ Performance: Improve page speed from {load_time}s to under 2 seconds')
            
            # Meta recommendations
            if not meta.get('has_description'):
                recommendations.append('🎯 Meta: Add compelling meta description to improve click-through rate')
            
            # Add top 3 specific issues
            for issue in sorted(issues, key=lambda x: x.impact_score, reverse=True)[:3]:
                recommendations.append(f'✓ {issue.title}: {issue.fix}')
            
            return recommendations[:8]  # Limit to 8 recommendations

