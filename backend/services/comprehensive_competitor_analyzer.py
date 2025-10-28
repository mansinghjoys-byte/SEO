"""
Comprehensive Competitor Analysis Orchestrator
Combines all competitor analysis services into one comprehensive report
"""
from typing import Dict, List, Any, Optional
import logging
import asyncio
from datetime import datetime
from groq import AsyncGroq
from core.config import get_settings
from services.competitor_discovery import CompetitorDiscoveryService
from services.competitor_backlink_analysis import CompetitorBacklinkService
from services.competitor_content_analysis import CompetitorContentService
from services.competitor_social_analysis import CompetitorSocialService

logger = logging.getLogger(__name__)
settings = get_settings()


class ComprehensiveCompetitorAnalyzer:
    """Orchestrates complete competitor analysis"""
    
    def __init__(self):
        self.discovery_service = CompetitorDiscoveryService()
        self.backlink_service = CompetitorBacklinkService()
        self.content_service = CompetitorContentService()
        self.social_service = CompetitorSocialService()
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    
    async def comprehensive_analysis(
        self,
        site_url: str,
        keywords: List[str],
        industry: Optional[str] = None,
        analyze_top_n_competitors: int = 5
    ) -> Dict[str, Any]:
        """
        Run comprehensive competitor analysis
        """
        try:
            logger.info(f"Starting comprehensive competitor analysis for {site_url}")
            
            your_domain = self._extract_domain(site_url)
            
            # Step 1: Discover competitors
            logger.info("Step 1: Discovering competitors...")
            discovery_result = await self.discovery_service.discover_competitors(
                site_url,
                keywords,
                industry,
                max_competitors=20
            )
            
            if not discovery_result.get('success'):
                return {
                    'success': False,
                    'error': 'Failed to discover competitors',
                    'details': discovery_result
                }
            
            competitors = discovery_result.get('competitors', [])[:analyze_top_n_competitors]
            
            if not competitors:
                return {
                    'success': False,
                    'error': 'No competitors found'
                }
            
            # Step 2: Analyze each competitor in depth
            logger.info(f"Step 2: Analyzing top {len(competitors)} competitors...")
            competitor_analyses = []
            
            for idx, competitor in enumerate(competitors):
                logger.info(f"Analyzing competitor {idx + 1}/{len(competitors)}: {competitor.get('domain')}")
                
                competitor_domain = competitor.get('domain')
                brand_name = competitor_domain.split('.')[0]
                
                # Run analyses in parallel for each competitor
                backlink_task = self.backlink_service.analyze_competitor_backlinks(
                    competitor_domain,
                    your_domain
                )
                
                content_task = self.content_service.analyze_competitor_content(
                    competitor_domain,
                    your_domain,
                    keywords
                )
                
                social_task = self.social_service.analyze_competitor_social_presence(
                    competitor_domain,
                    brand_name
                )
                
                # Wait for all analyses
                backlink_result, content_result, social_result = await asyncio.gather(
                    backlink_task,
                    content_task,
                    social_task,
                    return_exceptions=True
                )
                
                # Handle errors gracefully
                if isinstance(backlink_result, Exception):
                    backlink_result = {'success': False, 'error': str(backlink_result)}
                if isinstance(content_result, Exception):
                    content_result = {'success': False, 'error': str(content_result)}
                if isinstance(social_result, Exception):
                    social_result = {'success': False, 'error': str(social_result)}
                
                competitor_analyses.append({
                    'competitor': competitor,
                    'backlink_analysis': backlink_result,
                    'content_analysis': content_result,
                    'social_analysis': social_result,
                    'overall_score': self._calculate_competitor_score(
                        backlink_result,
                        content_result,
                        social_result
                    )
                })
            
            # Step 3: Cross-competitor insights
            logger.info("Step 3: Generating cross-competitor insights...")
            cross_insights = await self._generate_cross_competitor_insights(
                competitor_analyses,
                your_domain,
                keywords
            )
            
            # Step 4: Actionable recommendations
            logger.info("Step 4: Creating actionable recommendations...")
            recommendations = await self._generate_recommendations(
                competitor_analyses,
                cross_insights,
                your_domain
            )
            
            # Step 5: Competitive landscape summary
            landscape = self._create_competitive_landscape(competitor_analyses)
            
            return {
                'success': True,
                'your_domain': your_domain,
                'analysis_date': datetime.utcnow().isoformat(),
                'competitors_analyzed': len(competitor_analyses),
                'competitors': competitor_analyses,
                'cross_competitor_insights': cross_insights,
                'competitive_landscape': landscape,
                'actionable_recommendations': recommendations,
                'executive_summary': self._create_executive_summary(
                    competitor_analyses,
                    landscape,
                    recommendations
                )
            }
            
        except Exception as e:
            logger.error(f'Comprehensive analysis error: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def _calculate_competitor_score(
        self,
        backlink_result: Dict[str, Any],
        content_result: Dict[str, Any],
        social_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall competitor strength score"""
        
        # Backlink score (0-100)
        backlink_score = 0
        if backlink_result.get('success'):
            metrics = backlink_result.get('metrics', {})
            backlink_score = min(
                (metrics.get('average_authority', 0) +
                 min(metrics.get('high_authority_count', 0) * 2, 50)) / 2,
                100
            )
        
        # Content score (0-100)
        content_score = 0
        if content_result.get('success'):
            quality = content_result.get('quality_metrics', {})
            word_count = quality.get('average_word_count', 0)
            content_score = min((word_count / 20) + 30, 100)
        
        # Social score (0-100)
        social_score = 0
        if social_result.get('success'):
            social_metrics = social_result.get('social_metrics', {})
            social_score = social_metrics.get('overall_social_score', 0)
        
        # Overall score (weighted average)
        overall = (backlink_score * 0.4 + content_score * 0.35 + social_score * 0.25)
        
        # Determine threat level
        if overall >= 75:
            threat_level = 'high'
        elif overall >= 50:
            threat_level = 'medium'
        else:
            threat_level = 'low'
        
        return {
            'overall_score': round(overall, 1),
            'backlink_score': round(backlink_score, 1),
            'content_score': round(content_score, 1),
            'social_score': round(social_score, 1),
            'threat_level': threat_level,
            'strengths': self._identify_strengths(backlink_score, content_score, social_score),
            'weaknesses': self._identify_weaknesses(backlink_score, content_score, social_score)
        }
    
    def _identify_strengths(
        self,
        backlink_score: float,
        content_score: float,
        social_score: float
    ) -> List[str]:
        """Identify competitor strengths"""
        strengths = []
        
        if backlink_score >= 70:
            strengths.append('Strong backlink profile')
        if content_score >= 70:
            strengths.append('High-quality content')
        if social_score >= 70:
            strengths.append('Active social presence')
        
        if not strengths:
            strengths.append('Establishing market presence')
        
        return strengths
    
    def _identify_weaknesses(
        self,
        backlink_score: float,
        content_score: float,
        social_score: float
    ) -> List[str]:
        """Identify competitor weaknesses"""
        weaknesses = []
        
        if backlink_score < 40:
            weaknesses.append('Weak backlink profile')
        if content_score < 40:
            weaknesses.append('Limited content depth')
        if social_score < 40:
            weaknesses.append('Minimal social engagement')
        
        if not weaknesses:
            weaknesses.append('Well-rounded competitor')
        
        return weaknesses
    
    async def _generate_cross_competitor_insights(
        self,
        analyses: List[Dict[str, Any]],
        your_domain: str,
        keywords: List[str]
    ) -> Dict[str, Any]:
        """Generate insights across all competitors"""
        
        # Aggregate metrics
        all_backlink_opportunities = []
        all_content_gaps = []
        common_platforms = {}
        
        for analysis in analyses:
            # Collect backlink opportunities
            backlink_result = analysis.get('backlink_analysis', {})
            if backlink_result.get('success'):
                opportunities = backlink_result.get('link_gap_opportunities', [])
                all_backlink_opportunities.extend(opportunities)
            
            # Collect content gaps
            content_result = analysis.get('content_analysis', {})
            if content_result.get('success'):
                gaps = content_result.get('content_gaps', [])
                all_content_gaps.extend(gaps)
            
            # Track social platforms
            social_result = analysis.get('social_analysis', {})
            if social_result.get('success'):
                social_metrics = social_result.get('social_metrics', {})
                platform = social_metrics.get('strongest_platform', '')
                if platform:
                    common_platforms[platform] = common_platforms.get(platform, 0) + 1
        
        # Find common backlink sources
        common_sources = self._find_common_backlink_sources(all_backlink_opportunities)
        
        # Find most common content gaps
        common_content_gaps = self._find_common_content_gaps(all_content_gaps)
        
        return {
            'common_backlink_sources': common_sources[:10],
            'common_content_topics': common_content_gaps[:10],
            'most_used_social_platform': max(common_platforms.items(), key=lambda x: x[1])[0] if common_platforms else 'unknown',
            'total_unique_opportunities': len(set(o.get('domain', '') for o in all_backlink_opportunities)),
            'industry_trends': self._identify_industry_trends(analyses)
        }
    
    def _find_common_backlink_sources(
        self,
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find backlink sources used by multiple competitors"""
        source_counts = {}
        source_details = {}
        
        for opp in opportunities:
            domain = opp.get('domain', '')
            if domain:
                source_counts[domain] = source_counts.get(domain, 0) + 1
                if domain not in source_details:
                    source_details[domain] = opp
        
        # Sort by count
        common = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'domain': domain,
                'used_by_competitors': count,
                'details': source_details.get(domain, {})
            }
            for domain, count in common if count > 1
        ]
    
    def _find_common_content_gaps(
        self,
        gaps: List[Dict[str, Any]]
    ) -> List[str]:
        """Find content topics covered by multiple competitors"""
        topic_counts = {}
        
        for gap in gaps:
            topic = gap.get('topic', '')
            if topic:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Sort by count
        common = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [topic for topic, count in common if count > 1]
    
    def _identify_industry_trends(
        self,
        analyses: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify industry trends from competitor analysis"""
        trends = []
        
        # Analyze content depth trend
        avg_word_counts = []
        for analysis in analyses:
            content_result = analysis.get('content_analysis', {})
            if content_result.get('success'):
                quality = content_result.get('quality_metrics', {})
                avg_word_counts.append(quality.get('average_word_count', 0))
        
        if avg_word_counts:
            avg = sum(avg_word_counts) / len(avg_word_counts)
            if avg > 2000:
                trends.append('Industry trend: Long-form, comprehensive content (2000+ words)')
            elif avg > 1000:
                trends.append('Industry trend: In-depth content (1000-2000 words)')
        
        # Social media trend
        social_scores = []
        for analysis in analyses:
            social_result = analysis.get('social_analysis', {})
            if social_result.get('success'):
                metrics = social_result.get('social_metrics', {})
                social_scores.append(metrics.get('overall_social_score', 0))
        
        if social_scores:
            avg_social = sum(social_scores) / len(social_scores)
            if avg_social > 60:
                trends.append('Industry trend: Strong social media presence is standard')
        
        if not trends:
            trends.append('Mixed approaches in the industry')
        
        return trends
    
    async def _generate_recommendations(
        self,
        analyses: List[Dict[str, Any]],
        cross_insights: Dict[str, Any],
        your_domain: str
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Backlink recommendations
        common_sources = cross_insights.get('common_backlink_sources', [])
        if common_sources:
            recommendations.append({
                'category': 'backlinks',
                'priority': 'high',
                'action': 'Target common backlink sources',
                'details': f"Focus on getting links from {common_sources[0].get('domain')} and {len(common_sources)} other sources used by multiple competitors",
                'estimated_impact': 'high',
                'estimated_effort': 'medium'
            })
        
        # Content recommendations
        common_topics = cross_insights.get('common_content_topics', [])
        if common_topics:
            recommendations.append({
                'category': 'content',
                'priority': 'high',
                'action': 'Cover trending topics',
                'details': f"Create comprehensive content on: {', '.join(common_topics[:3])}",
                'estimated_impact': 'high',
                'estimated_effort': 'high'
            })
        
        # Social media recommendations
        top_platform = cross_insights.get('most_used_social_platform')
        if top_platform:
            recommendations.append({
                'category': 'social_media',
                'priority': 'medium',
                'action': f'Increase {top_platform} presence',
                'details': f'Competitors are most active on {top_platform}. Build consistent presence there.',
                'estimated_impact': 'medium',
                'estimated_effort': 'medium'
            })
        
        # Competitive gaps
        recommendations.append({
            'category': 'competitive_gap',
            'priority': 'high',
            'action': 'Exploit competitor weaknesses',
            'details': 'Analyze competitor weaknesses and create superior content/links in those areas',
            'estimated_impact': 'very_high',
            'estimated_effort': 'high'
        })
        
        return recommendations
    
    def _create_competitive_landscape(
        self,
        analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create competitive landscape overview"""
        
        # Rank competitors by overall score
        ranked = sorted(
            analyses,
            key=lambda x: x.get('overall_score', {}).get('overall_score', 0),
            reverse=True
        )
        
        return {
            'total_competitors_analyzed': len(analyses),
            'strongest_competitor': ranked[0].get('competitor', {}).get('domain') if ranked else 'unknown',
            'weakest_competitor': ranked[-1].get('competitor', {}).get('domain') if ranked else 'unknown',
            'average_competitor_score': round(
                sum(a.get('overall_score', {}).get('overall_score', 0) for a in analyses) / len(analyses), 1
            ) if analyses else 0,
            'high_threat_competitors': len([a for a in analyses if a.get('overall_score', {}).get('threat_level') == 'high']),
            'medium_threat_competitors': len([a for a in analyses if a.get('overall_score', {}).get('threat_level') == 'medium']),
            'low_threat_competitors': len([a for a in analyses if a.get('overall_score', {}).get('threat_level') == 'low']),
            'competitive_intensity': self._determine_competitive_intensity(analyses)
        }
    
    def _determine_competitive_intensity(self, analyses: List[Dict[str, Any]]) -> str:
        """Determine how competitive the market is"""
        if not analyses:
            return 'unknown'
        
        avg_score = sum(a.get('overall_score', {}).get('overall_score', 0) for a in analyses) / len(analyses)
        
        if avg_score >= 70:
            return 'very_high'
        elif avg_score >= 55:
            return 'high'
        elif avg_score >= 40:
            return 'moderate'
        else:
            return 'low'
    
    def _create_executive_summary(
        self,
        analyses: List[Dict[str, Any]],
        landscape: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create executive summary"""
        
        return {
            'key_findings': [
                f"Analyzed {landscape.get('total_competitors_analyzed')} competitors",
                f"Competitive intensity: {landscape.get('competitive_intensity')}",
                f"Strongest competitor: {landscape.get('strongest_competitor')}",
                f"{landscape.get('high_threat_competitors')} high-threat competitors identified"
            ],
            'top_priorities': [rec.get('action') for rec in recommendations[:3]],
            'opportunity_score': self._calculate_opportunity_score(analyses, landscape),
            'next_steps': [
                'Review detailed competitor profiles',
                'Implement high-priority recommendations',
                'Monitor competitor changes monthly',
                'Execute backlink outreach strategy'
            ]
        }
    
    def _calculate_opportunity_score(
        self,
        analyses: List[Dict[str, Any]],
        landscape: Dict[str, Any]
    ) -> int:
        """Calculate opportunity score (0-100)"""
        
        # Lower competitor scores = higher opportunity
        avg_competitor_score = landscape.get('average_competitor_score', 50)
        opportunity = 100 - avg_competitor_score
        
        # Adjust based on competitive intensity
        intensity = landscape.get('competitive_intensity')
        if intensity == 'low':
            opportunity += 10
        elif intensity == 'very_high':
            opportunity -= 10
        
        return max(0, min(100, int(opportunity)))
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            import re
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            domain = re.sub(r'^www\.', '', domain)
            return domain.split('/')[0].lower()
        except:
            return url
