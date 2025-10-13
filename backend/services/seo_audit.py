from abc import ABC, abstractmethod
from typing import Dict, Any, List
import httpx
import re
from urllib.parse import urlparse
import asyncio
from core.config import get_settings
from schemas.schemas import AuditIssue

settings = get_settings()

class BaseAnalyzer(ABC):
    """Base class for SEO analyzers (Open/Closed Principle)"""
    
    @abstractmethod
    async def analyze(self, url: str, content: str = None) -> List[AuditIssue]:
        pass

class TechnicalSEOAnalyzer(BaseAnalyzer):
    """Analyzes technical SEO aspects"""
    
    async def analyze(self, url: str, content: str = None) -> List[AuditIssue]:
        issues = []
        
        if not content:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, follow_redirects=True)
                    content = response.text
                    status_code = response.status_code
                    response_time = response.elapsed.total_seconds()
            except Exception as e:
                issues.append(AuditIssue(
                    category='technical',
                    severity='critical',
                    title='Site Unreachable',
                    description=f'Unable to access the site: {str(e)}',
                    fix='Check if the site is online and accessible',
                    impact_score=100
                ))
                return issues
        
        # Check HTTPS
        if not url.startswith('https://'):
            issues.append(AuditIssue(
                category='technical',
                severity='high',
                title='Missing HTTPS',
                description='Site is not using HTTPS encryption',
                fix='Install SSL certificate and redirect HTTP to HTTPS',
                impact_score=80
            ))
        
        # Check page speed (simulated)
        if 'response_time' in locals() and response_time > 3:
            issues.append(AuditIssue(
                category='technical',
                severity='high',
                title='Slow Page Load Time',
                description=f'Page loads in {response_time:.2f} seconds (should be <3s)',
                fix='Optimize images, enable caching, use CDN, minify CSS/JS',
                impact_score=75
            ))
        
        # Check mobile viewport
        if content and 'viewport' not in content.lower():
            issues.append(AuditIssue(
                category='technical',
                severity='medium',
                title='Missing Mobile Viewport',
                description='No viewport meta tag found',
                fix='Add <meta name="viewport" content="width=device-width, initial-scale=1">',
                impact_score=60
            ))
        
        # Check robots meta
        if content and 'noindex' in content.lower():
            issues.append(AuditIssue(
                category='technical',
                severity='critical',
                title='Page Blocked from Indexing',
                description='Page has noindex directive',
                fix='Remove noindex meta tag unless intentional',
                impact_score=100
            ))
        
        return issues

class OnPageSEOAnalyzer(BaseAnalyzer):
    """Analyzes on-page SEO elements"""
    
    async def analyze(self, url: str, content: str = None) -> List[AuditIssue]:
        issues = []
        
        if not content:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url)
                    content = response.text
            except:
                return issues
        
        # Check title tag
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE)
        if not title_match:
            issues.append(AuditIssue(
                category='on-page',
                severity='critical',
                title='Missing Title Tag',
                description='No title tag found on the page',
                fix='Add a unique, descriptive title tag (50-60 characters)',
                impact_score=100
            ))
        elif title_match:
            title = title_match.group(1)
            if len(title) < 30:
                issues.append(AuditIssue(
                    category='on-page',
                    severity='medium',
                    title='Title Tag Too Short',
                    description=f'Title is only {len(title)} characters (recommended: 50-60)',
                    fix='Expand title to include more descriptive keywords',
                    impact_score=50
                ))
            elif len(title) > 60:
                issues.append(AuditIssue(
                    category='on-page',
                    severity='medium',
                    title='Title Tag Too Long',
                    description=f'Title is {len(title)} characters (recommended: 50-60)',
                    fix='Shorten title to avoid truncation in search results',
                    impact_score=50
                ))
        
        # Check meta description
        meta_desc = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\'>]*)["\']', content, re.IGNORECASE)
        if not meta_desc:
            issues.append(AuditIssue(
                category='on-page',
                severity='high',
                title='Missing Meta Description',
                description='No meta description found',
                fix='Add compelling meta description (150-160 characters)',
                impact_score=70
            ))
        
        # Check H1 tag
        h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE)
        if not h1_matches:
            issues.append(AuditIssue(
                category='on-page',
                severity='high',
                title='Missing H1 Tag',
                description='No H1 heading found on the page',
                fix='Add a single, keyword-rich H1 tag at the top of your content',
                impact_score=75
            ))
        elif len(h1_matches) > 1:
            issues.append(AuditIssue(
                category='on-page',
                severity='medium',
                title='Multiple H1 Tags',
                description=f'Found {len(h1_matches)} H1 tags (should have only 1)',
                fix='Use only one H1 tag per page for main heading',
                impact_score=40
            ))
        
        # Check images without alt tags
        img_tags = re.findall(r'<img[^>]*>', content, re.IGNORECASE)
        images_without_alt = [img for img in img_tags if 'alt=' not in img.lower()]
        if images_without_alt:
            issues.append(AuditIssue(
                category='on-page',
                severity='medium',
                title='Images Missing Alt Text',
                description=f'{len(images_without_alt)} images found without alt attributes',
                fix='Add descriptive alt text to all images for accessibility and SEO',
                impact_score=55
            ))
        
        # Check content length
        text_content = re.sub(r'<[^>]+>', '', content)
        word_count = len(text_content.split())
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
    
    async def analyze(self, url: str, content: str = None) -> List[AuditIssue]:
        issues = []
        
        # Simulated backlink analysis
        issues.append(AuditIssue(
            category='off-page',
            severity='low',
            title='Limited Backlink Profile',
            description='Your site would benefit from more quality backlinks',
            fix='Start link building campaign: guest posting, broken link building, PR outreach',
            impact_score=65
        ))
        
        # Check social signals (simulated)
        if content:
            has_og_tags = 'og:' in content.lower()
            if not has_og_tags:
                issues.append(AuditIssue(
                    category='off-page',
                    severity='medium',
                    title='Missing Open Graph Tags',
                    description='No Open Graph meta tags for social sharing',
                    fix='Add og:title, og:description, og:image tags for better social media appearance',
                    impact_score=45
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
    
    async def run_audit(self, url: str) -> Dict[str, Any]:
        """Run comprehensive SEO audit"""
        all_issues = []
        
        # Fetch content once
        content = None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                content = response.text
        except:
            pass
        
        # Run all analyzers
        for analyzer in self.analyzers:
            issues = await analyzer.analyze(url, content)
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
        
        # Generate AI recommendations
        recommendations = await self._generate_recommendations(all_issues)
        
        return {
            'seo_score': seo_score,
            'technical_score': technical_score,
            'onpage_score': onpage_score,
            'offpage_score': offpage_score,
            'issues': all_issues,
            'recommendations': recommendations
        }
    
    async def _generate_recommendations(self, issues: List[AuditIssue]) -> List[str]:
        """Generate prioritized recommendations using AI"""
        if not issues:
            return ['Great job! No critical issues found. Continue monitoring your SEO performance.']
        
        # Sort by severity and impact
        critical = [i for i in issues if i.severity == 'critical']
        high = [i for i in issues if i.severity == 'high']
        
        recommendations = []
        
        if critical:
            recommendations.append(f'CRITICAL: Fix {len(critical)} critical issues immediately - these are blocking your SEO performance')
        
        if high:
            recommendations.append(f'HIGH PRIORITY: Address {len(high)} high-priority issues this week')
        
        # Add specific recommendations
        for issue in sorted(issues, key=lambda x: x.impact_score, reverse=True)[:3]:
            recommendations.append(f'{issue.title}: {issue.fix}')
        
        return recommendations
