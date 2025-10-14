"""
Content Intelligence Module
Provides content gap analysis, AI content generation, and schema markup
"""
from typing import Dict, List, Any, Optional
from groq import AsyncGroq
from core.config import get_settings
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)
settings = get_settings()


class ContentIntelligenceService:
    """AI-powered content analysis and generation"""
    
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    
    async def analyze_content_gaps(
        self,
        site_url: str,
        site_content: Dict[str, Any],
        competitors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze content gaps compared to competitors and best practices
        """
        try:
            prompt = f"""Analyze content gaps for this website:

URL: {site_url}
Current Content:
- Word Count: {site_content.get('word_count', 0)}
- H1 Tags: {', '.join(site_content.get('h1_text', [])[:5])}
- H2 Topics: {', '.join(site_content.get('h2_text', [])[:10])}

Identify:
1. Missing essential content pieces
2. Topics competitors cover but you don't
3. Questions your audience is asking
4. Content depth improvements needed
5. Content calendar suggestions (12 articles)

Provide in JSON format:
{{
    "missing_topics": ["topic 1", "topic 2"],
    "competitor_advantages": ["what they have"],
    "audience_questions": ["question 1"],
    "depth_improvements": ["where to go deeper"],
    "content_calendar": [
        {{
            "title": "Article title",
            "type": "guide|how-to|comparison|list",
            "priority": "high|medium|low",
            "estimated_length": "words",
            "keywords": ["kw1", "kw2"]
        }}
    ]
}}"""

            response = await self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert content strategist. Provide specific, actionable content recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            
            try:
                gaps = json.loads(result)
            except:
                gaps = {'error': 'Could not parse AI response', 'raw': result}
            
            return {
                'success': True,
                'gaps': gaps,
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f'Content gap analysis error: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    async def generate_content_outline(
        self,
        topic: str,
        content_type: str = 'guide',
        target_length: int = 2000
    ) -> Dict[str, Any]:
        """
        Generate AI-optimized content outline
        """
        try:
            prompt = f"""Create a comprehensive outline for a {content_type} about: {topic}

Target length: {target_length} words
Optimize for:
- LLM visibility (how LLMs would reference this)
- Natural language queries
- E-E-A-T signals
- Comprehensive coverage

Provide detailed outline in JSON:
{{
    "title": "SEO-optimized title",
    "meta_description": "150-160 chars",
    "target_keywords": ["primary", "secondary"],
    "outline": [
        {{
            "section": "Section title",
            "subsections": ["subsection 1"],
            "word_count": 300,
            "key_points": ["point 1", "point 2"],
            "examples_needed": true,
            "data_points": "What statistics to include"
        }}
    ],
    "faq_questions": ["question 1"],
    "internal_links": ["where to link"],
    "call_to_action": "CTA suggestion"
}}"""

            response = await self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert content creator specializing in LLM-optimized content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.6,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            
            try:
                outline = json.loads(result)
            except:
                outline = {'error': 'Could not parse outline', 'raw': result}
            
            return {
                'success': True,
                'outline': outline,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f'Content generation error: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    async def enhance_existing_content(
        self,
        current_content: str,
        improvement_goals: List[str]
    ) -> Dict[str, Any]:
        """
        Suggest improvements for existing content
        """
        try:
            goals_str = ', '.join(improvement_goals)
            
            prompt = f"""Analyze and suggest improvements for this content:

Current Content (first 2000 chars):
{current_content[:2000]}

Improvement Goals: {goals_str}

Provide specific suggestions in JSON:
{{
    "clarity_improvements": ["suggestion 1"],
    "missing_elements": ["what to add"],
    "structure_changes": ["restructuring ideas"],
    "keyword_optimization": ["keywords to add naturally"],
    "multimedia_suggestions": ["images, videos to add"],
    "faq_additions": ["questions to answer"],
    "rewrite_sections": [
        {{
            "section": "which section",
            "current": "current text",
            "improved": "suggested rewrite"
        }}
    ]
}}"""

            response = await self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert content editor. Provide specific, actionable improvements."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            
            try:
                suggestions = json.loads(result)
            except:
                suggestions = {'error': 'Could not parse suggestions', 'raw': result}
            
            return {
                'success': True,
                'suggestions': suggestions,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f'Content enhancement error: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def generate_schema_markup(
        self,
        schema_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate schema markup for different types
        """
        schemas = {
            'faq': self._generate_faq_schema(data),
            'article': self._generate_article_schema(data),
            'product': self._generate_product_schema(data),
            'organization': self._generate_organization_schema(data),
            'breadcrumb': self._generate_breadcrumb_schema(data),
            'how_to': self._generate_howto_schema(data)
        }
        
        schema = schemas.get(schema_type.lower(), {})
        
        return {
            'success': bool(schema),
            'schema_type': schema_type,
            'schema': schema,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _generate_faq_schema(self, data: Dict) -> Dict:
        """Generate FAQ schema"""
        questions = data.get('questions', [])
        
        faq_list = []
        for q in questions:
            faq_list.append({
                '@type': 'Question',
                'name': q.get('question', ''),
                'acceptedAnswer': {
                    '@type': 'Answer',
                    'text': q.get('answer', '')
                }
            })
        
        return {
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            'mainEntity': faq_list
        }
    
    def _generate_article_schema(self, data: Dict) -> Dict:
        """Generate Article schema"""
        return {
            '@context': 'https://schema.org',
            '@type': 'Article',
            'headline': data.get('title', ''),
            'description': data.get('description', ''),
            'author': {
                '@type': 'Person',
                'name': data.get('author', 'Unknown')
            },
            'datePublished': data.get('published_date', datetime.utcnow().isoformat()),
            'dateModified': data.get('modified_date', datetime.utcnow().isoformat())
        }
    
    def _generate_product_schema(self, data: Dict) -> Dict:
        """Generate Product schema"""
        return {
            '@context': 'https://schema.org',
            '@type': 'Product',
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'image': data.get('image_url', ''),
            'offers': {
                '@type': 'Offer',
                'price': data.get('price', '0'),
                'priceCurrency': data.get('currency', 'USD')
            }
        }
    
    def _generate_organization_schema(self, data: Dict) -> Dict:
        """Generate Organization schema"""
        return {
            '@context': 'https://schema.org',
            '@type': 'Organization',
            'name': data.get('name', ''),
            'url': data.get('url', ''),
            'logo': data.get('logo_url', ''),
            'contactPoint': {
                '@type': 'ContactPoint',
                'contactType': 'customer service',
                'email': data.get('email', '')
            }
        }
    
    def _generate_breadcrumb_schema(self, data: Dict) -> Dict:
        """Generate Breadcrumb schema"""
        breadcrumbs = data.get('breadcrumbs', [])
        
        item_list = []
        for i, crumb in enumerate(breadcrumbs, 1):
            item_list.append({
                '@type': 'ListItem',
                'position': i,
                'name': crumb.get('name', ''),
                'item': crumb.get('url', '')
            })
        
        return {
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': item_list
        }
    
    def _generate_howto_schema(self, data: Dict) -> Dict:
        """Generate HowTo schema"""
        steps = data.get('steps', [])
        
        step_list = []
        for i, step in enumerate(steps, 1):
            step_list.append({
                '@type': 'HowToStep',
                'position': i,
                'name': step.get('name', ''),
                'text': step.get('text', '')
            })
        
        return {
            '@context': 'https://schema.org',
            '@type': 'HowTo',
            'name': data.get('title', ''),
            'description': data.get('description', ''),
            'step': step_list
        }
