"""
Actionable Recommendation Engine
Provides prioritized, step-by-step recommendations for improving SEO and LLM visibility
"""
from typing import Dict, List, Any, Optional
from groq import AsyncGroq
from core.config import get_settings
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)
settings = get_settings()


class RecommendationEngine:
    """Generate actionable, prioritized SEO recommendations"""
    
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    
    async def generate_recommendations(
        self,
        site_data: Dict[str, Any],
        audit_data: Optional[Dict] = None,
        visibility_data: Optional[Dict] = None,
        content_analysis: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive recommendations from all data sources
        """
        try:
            # Collect all insights
            insights = self._gather_insights(site_data, audit_data, visibility_data, content_analysis)
            
            # Generate AI recommendations
            recommendations = await self._ai_generate_recommendations(insights)
            
            # Categorize and prioritize
            categorized = self._categorize_recommendations(recommendations)
            
            # Add templates and resources
            enriched = self._enrich_with_resources(categorized)
            
            return {
                'success': True,
                'total_recommendations': len(recommendations),
                'quick_wins': enriched.get('quick_wins', []),
                'high_priority': enriched.get('high_priority', []),
                'medium_priority': enriched.get('medium_priority', []),
                'long_term': enriched.get('long_term', []),
                'content_strategy': enriched.get('content_strategy', []),
                'technical_seo': enriched.get('technical_seo', []),
                'link_building': enriched.get('link_building', []),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f'Recommendation generation error: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def _gather_insights(
        self,
        site_data: Dict,
        audit_data: Optional[Dict],
        visibility_data: Optional[Dict],
        content_analysis: Optional[Dict]
    ) -> Dict[str, Any]:
        """Gather insights from all data sources"""
        insights = {
            'url': site_data.get('url'),
            'issues': [],
            'strengths': [],
            'opportunities': []
        }
        
        # From audit data
        if audit_data:
            insights['seo_score'] = audit_data.get('seo_score', 0)
            insights['issues'].extend(audit_data.get('issues', []))
            insights['technical_status'] = audit_data.get('technical_score', 0)
        
        # From visibility data
        if visibility_data:
            insights['visibility_score'] = visibility_data.get('overall_score', 0)
            insights['llm_presence'] = visibility_data.get('breakdown', {})
            
            if visibility_data.get('overall_score', 0) < 50:
                insights['issues'].append({
                    'type': 'visibility',
                    'severity': 'high',
                    'description': 'Low LLM visibility score'
                })
        
        # From content analysis
        if content_analysis:
            insights['content_gaps'] = content_analysis.get('gaps', [])
            insights['content_quality'] = content_analysis.get('quality_score', 0)
        
        return insights
    
    async def _ai_generate_recommendations(
        self,
        insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Use AI to generate detailed recommendations"""
        try:
            prompt = f"""As an expert SEO and LLM visibility consultant, analyze this website and provide actionable recommendations:

URL: {insights.get('url')}
SEO Score: {insights.get('seo_score', 'N/A')}/100
LLM Visibility Score: {insights.get('visibility_score', 'N/A')}/100
Issues Found: {len(insights.get('issues', []))}

Generate 12-15 specific, actionable recommendations in JSON format:
[
    {{
        "id": 1,
        "title": "Clear, actionable title",
        "category": "on_site_content|off_site_visibility|community_engagement|technical_improvements",
        "priority": "critical|high|medium|low",
        "impact": "Expected visibility points increase",
        "effort": "Detailed time estimate (e.g., 2-4 hours)",
        "time_to_impact": "When to expect results (e.g., 2-3 weeks)",
        "why_matters": "Clear explanation of importance",
        "what_to_do": "Detailed instructions",
        "steps": [
            {{
                "step": 1,
                "title": "Step title",
                "description": "Detailed description",
                "example": "Code snippet or example"
            }}
        ],
        "resources": ["Resource 1", "Resource 2"],
        "success_metric": "How to measure success"
    }}
]

Focus on:
1. Quick wins (high impact, low effort)
2. Content optimization for LLM recommendations
3. Technical SEO fixes
4. Authority building
5. Community engagement strategies"""

            response = await self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior SEO consultant specializing in LLM visibility optimization. Provide specific, actionable, step-by-step recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,
                max_tokens=3000
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON
            try:
                recommendations = json.loads(result)
                if isinstance(recommendations, list):
                    return recommendations
            except:
                # Fallback if JSON parsing fails
                pass
            
            # Return fallback recommendations
            return self._generate_fallback_recommendations(insights)
            
        except Exception as e:
            logger.error(f'AI recommendation error: {str(e)}')
            return self._generate_fallback_recommendations(insights)
    
    def _generate_fallback_recommendations(
        self,
        insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate basic recommendations if AI fails"""
        recommendations = []
        
        # Always include essential recommendations
        if insights.get('visibility_score', 0) < 60:
            recommendations.append({
                'id': 1,
                'title': 'Create Comprehensive Guide Content',
                'category': 'on_site_content',
                'priority': 'high',
                'impact': '+15 visibility points',
                'effort': '6-8 hours',
                'time_to_impact': '4-6 weeks',
                'why_matters': 'LLMs frequently reference comprehensive guides. Creating definitive resources increases your chances of being recommended.',
                'what_to_do': 'Create in-depth guides on your core topics',
                'steps': [
                    {
                        'step': 1,
                        'title': 'Identify key topics',
                        'description': 'List the main questions your audience asks',
                        'example': 'If you sell project management software, create "Ultimate Guide to Project Management"'
                    }
                ],
                'resources': ['Content template', 'SEO checklist'],
                'success_metric': 'Track mentions in AI search results'
            })
        
        if insights.get('seo_score', 0) < 70:
            recommendations.append({
                'id': 2,
                'title': 'Optimize Meta Tags and Schema',
                'category': 'technical_improvements',
                'priority': 'high',
                'impact': '+10 visibility points',
                'effort': '2-3 hours',
                'time_to_impact': '2-3 weeks',
                'why_matters': 'Structured data helps LLMs understand your content better',
                'what_to_do': 'Add comprehensive schema markup',
                'steps': [
                    {
                        'step': 1,
                        'title': 'Add FAQ schema',
                        'description': 'Implement FAQ schema for common questions',
                        'example': '<script type="application/ld+json">{"@context": "https://schema.org"...}</script>'
                    }
                ],
                'resources': ['Schema generator tool', 'Validation tool'],
                'success_metric': 'Validate schema with Google Rich Results Test'
            })
        
        return recommendations
    
    def _categorize_recommendations(
        self,
        recommendations: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """Categorize recommendations by priority and type"""
        categorized = {
            'quick_wins': [],
            'high_priority': [],
            'medium_priority': [],
            'long_term': [],
            'content_strategy': [],
            'technical_seo': [],
            'link_building': []
        }
        
        for rec in recommendations:
            priority = rec.get('priority', 'medium')
            category = rec.get('category', 'general')
            
            # Add to priority lists
            if priority == 'critical':
                categorized['high_priority'].append(rec)
            elif priority == 'high':
                # Check if it's a quick win (high impact, low effort)
                effort_str = rec.get('effort', '').lower()
                if any(time in effort_str for time in ['minutes', '1 hour', '2 hours', '1-2 hours']):
                    categorized['quick_wins'].append(rec)
                else:
                    categorized['high_priority'].append(rec)
            elif priority == 'medium':
                categorized['medium_priority'].append(rec)
            else:
                categorized['long_term'].append(rec)
            
            # Add to category lists
            if 'content' in category.lower():
                categorized['content_strategy'].append(rec)
            elif 'technical' in category.lower():
                categorized['technical_seo'].append(rec)
            elif 'link' in category.lower() or 'backlink' in category.lower():
                categorized['link_building'].append(rec)
        
        return categorized
    
    def _enrich_with_resources(
        self,
        categorized: Dict[str, List[Dict]]
    ) -> Dict[str, List[Dict]]:
        """Add templates, code snippets, and resources"""
        
        # Add common resources
        common_resources = {
            'schema_generator': 'https://technicalseo.com/tools/schema-markup-generator/',
            'meta_tag_template': 'Title: 50-60 chars | Description: 150-160 chars',
            'content_template': 'Introduction > Problem > Solution > Examples > FAQ > Conclusion'
        }
        
        for category in categorized:
            for rec in categorized[category]:
                if not rec.get('resources'):
                    rec['resources'] = []
                
                # Add relevant resources based on category
                if 'schema' in rec.get('title', '').lower():
                    rec['resources'].append(common_resources['schema_generator'])
                
                if 'meta' in rec.get('title', '').lower():
                    rec['resources'].append(common_resources['meta_tag_template'])
                
                if 'content' in rec.get('title', '').lower():
                    rec['resources'].append(common_resources['content_template'])
        
        return categorized
    
    async def generate_task_checklist(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Convert recommendations to actionable checklist"""
        tasks = []
        
        for i, rec in enumerate(recommendations[:20], 1):  # Limit to top 20
            task = {
                'task_id': f'task_{i}',
                'title': rec.get('title'),
                'priority': rec.get('priority'),
                'estimated_time': rec.get('effort'),
                'impact': rec.get('impact'),
                'completed': False,
                'steps': rec.get('steps', []),
                'resources': rec.get('resources', [])
            }
            tasks.append(task)
        
        return tasks
