"""
Community Action Hub
Finds opportunities on Reddit, Quora, and forums for engagement
"""
from typing import Dict, List, Any, Optional
from groq import AsyncGroq
from core.config import get_settings
import logging
import json
from datetime import datetime
import random

logger = logging.getLogger(__name__)
settings = get_settings()


class CommunityHubService:
    """Service for community engagement opportunities"""
    
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    
    async def find_opportunities(
        self,
        business_info: Dict[str, Any],
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Find relevant discussion opportunities
        """
        if not platforms:
            platforms = ['reddit', 'quora', 'forums']
        
        try:
            opportunities = []
            
            for platform in platforms:
                platform_opps = await self._find_platform_opportunities(
                    platform,
                    business_info
                )
                opportunities.extend(platform_opps)
            
            # Rank by relevance and engagement potential
            ranked = self._rank_opportunities(opportunities)
            
            return {
                'success': True,
                'total_opportunities': len(ranked),
                'opportunities': ranked[:20],  # Top 20
                'platforms_searched': platforms,
                'found_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f'Opportunity finding error: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    async def _find_platform_opportunities(
        self,
        platform: str,
        business_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Find opportunities on specific platform (simulated for demo)
        In production, integrate with real APIs
        """
        category = business_info.get('category', 'software')
        keywords = business_info.get('keywords', [])
        if not keywords:
            keywords = [category]
        
        # Simulate opportunities
        opportunities = []
        
        if platform == 'reddit':
            subreddits = self._suggest_subreddits(category)
            for subreddit in subreddits[:5]:
                keyword = keywords[0] if keywords else category
                opportunities.append({
                    'platform': 'Reddit',
                    'location': f'r/{subreddit}',
                    'title': f'Discussion about {keyword}',
                    'url': f'https://reddit.com/r/{subreddit}/post123',
                    'relevance_score': random.randint(70, 95),
                    'engagement': f'{random.randint(10, 200)} comments',
                    'recency': f'{random.randint(1, 48)} hours ago',
                    'opportunity_type': 'answer_question',
                    'why_relevant': f'Discussion directly related to {category}'
                })
        
        elif platform == 'quora':
            for i in range(3):
                opportunities.append({
                    'platform': 'Quora',
                    'location': 'Quora Question',
                    'title': f'What is the best {category} for startups?',
                    'url': f'https://quora.com/question-{i}',
                    'relevance_score': random.randint(75, 98),
                    'engagement': f'{random.randint(5, 50)} answers',
                    'recency': f'{random.randint(1, 72)} hours ago',
                    'opportunity_type': 'expert_answer',
                    'why_relevant': 'Your expertise directly addresses this question'
                })
        
        elif platform == 'forums':
            forums = ['HackerNews', 'ProductHunt', 'IndieHackers']
            for forum in forums:
                opportunities.append({
                    'platform': forum,
                    'location': f'{forum} Discussion',
                    'title': f'Looking for {category} recommendations',
                    'url': f'https://{forum.lower()}.com/thread-123',
                    'relevance_score': random.randint(65, 90),
                    'engagement': f'{random.randint(5, 100)} replies',
                    'recency': f'{random.randint(1, 96)} hours ago',
                    'opportunity_type': 'share_experience',
                    'why_relevant': 'Community actively seeking solutions'
                })
        
        return opportunities
    
    def _suggest_subreddits(self, category: str) -> List[str]:
        """Suggest relevant subreddits"""
        base_suggestions = {
            'software': ['SaaS', 'startups', 'Entrepreneur', 'smallbusiness', 'webdev'],
            'marketing': ['marketing', 'SEO', 'digital_marketing', 'content_marketing'],
            'ecommerce': ['ecommerce', 'shopify', 'Entrepreneur', 'smallbusiness'],
            'productivity': ['productivity', 'gtd', 'productivity', 'software']
        }
        
        return base_suggestions.get(category.lower(), ['business', 'Entrepreneur', 'startups'])
    
    def _rank_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """Rank opportunities by relevance and engagement potential"""
        # Sort by relevance score
        return sorted(opportunities, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    async def generate_response(
        self,
        opportunity: Dict[str, Any],
        business_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AI-powered response for an opportunity
        """
        try:
            prompt = f"""Generate a helpful, non-salesy response for this community discussion:

Platform: {opportunity.get('platform')}
Question/Discussion: {opportunity.get('title')}

Your Business: {business_info.get('name', 'Company')}
What you offer: {business_info.get('description', '')}

Guidelines:
1. Be genuinely helpful first
2. Share personal experience
3. Only mention your product naturally if relevant
4. Provide value even without mentioning your product
5. Avoid marketing language

Provide response in JSON:
{{
    "response": "Full response text",
    "tone": "helpful/casual/expert",
    "includes_product_mention": true/false,
    "product_mention_location": "where in response",
    "alternative_responses": ["variation 1", "variation 2"]
}}"""

            response = await self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at community engagement. Generate authentic, helpful responses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            
            try:
                response_data = json.loads(result)
            except:
                response_data = {'response': result, 'tone': 'helpful'}
            
            return {
                'success': True,
                'response_data': response_data,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f'Response generation error: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def get_response_templates(self) -> Dict[str, List[str]]:
        """Get pre-built response templates"""
        return {
            'experience_share': [
                "I've had a similar challenge...",
                "From my experience with this...",
                "We faced this exact issue and here's what worked..."
            ],
            'comparison': [
                "I've tried both X and Y, here's my take...",
                "Having used several options, here's what I found..."
            ],
            'solution_oriented': [
                "Here's a step-by-step approach that worked for us...",
                "I'd recommend starting with..."
            ],
            'question_answer': [
                "Great question! Here's what you need to know...",
                "The key thing to understand is..."
            ]
        }
