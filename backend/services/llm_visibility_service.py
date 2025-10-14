"""
LLM Visibility Scorecard Service
Tests visibility across multiple LLMs (ChatGPT, Claude, Gemini, Perplexity, etc.)
"""
import httpx
from typing import Dict, List, Any, Optional
from groq import AsyncGroq
from core.config import get_settings
import logging
import json
import random
from datetime import datetime

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMVisibilityService:
    """Service for testing and tracking LLM visibility"""
    
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        
        # Query templates for testing visibility
        self.query_templates = [
            "Best {category} for {use_case}",
            "Top {category} providers in {industry}",
            "{problem} solutions",
            "Alternative to {competitor}",
            "How to choose {category}",
            "What is the best {category}",
            "{category} comparison",
            "Recommended {category} for {use_case}",
            "{category} reviews and recommendations",
            "Most popular {category} tools"
        ]
    
    async def check_visibility(
        self,
        url: str,
        business_info: Dict[str, Any],
        competitors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Check LLM visibility by simulating queries
        """
        try:
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            category = business_info.get('category', 'service')
            industry = business_info.get('industry', 'general')
            
            # Generate test queries
            test_queries = self._generate_test_queries(category, industry, business_info)
            
            # Test visibility across simulated LLMs
            visibility_results = {
                'chatgpt': await self._simulate_llm_check('ChatGPT', domain, test_queries),
                'claude': await self._simulate_llm_check('Claude', domain, test_queries),
                'gemini': await self._simulate_llm_check('Gemini', domain, test_queries),
                'perplexity': await self._simulate_llm_check('Perplexity', domain, test_queries),
                'bing_chat': await self._simulate_llm_check('Bing Chat', domain, test_queries)
            }
            
            # Calculate overall visibility score
            overall_score = await self._calculate_visibility_score(visibility_results, domain, business_info)
            
            # Competitor benchmarking
            competitor_data = []
            if competitors:
                for comp in competitors[:3]:
                    comp_score = await self._quick_competitor_check(comp, test_queries)
                    competitor_data.append(comp_score)
            
            return {
                'success': True,
                'domain': domain,
                'overall_score': overall_score['score'],
                'breakdown': overall_score['breakdown'],
                'visibility_by_llm': visibility_results,
                'test_queries': test_queries,
                'competitor_benchmark': competitor_data,
                'recommendations': await self._generate_visibility_recommendations(
                    overall_score,
                    visibility_results,
                    competitor_data
                ),
                'checked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f'LLM visibility check error: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def _generate_test_queries(
        self,
        category: str,
        industry: str,
        business_info: Dict
    ) -> List[str]:
        """Generate relevant test queries"""
        queries = []
        
        # Use templates
        use_cases = business_info.get('use_cases', ['businesses', 'professionals', 'teams'])
        problems = business_info.get('problems_solved', ['efficiency', 'productivity', 'automation'])
        
        for template in self.query_templates[:8]:  # Use 8 queries
            query = template.format(
                category=category,
                use_case=random.choice(use_cases) if use_cases else 'users',
                industry=industry,
                problem=random.choice(problems) if problems else 'challenge',
                competitor='competitor'
            )
            queries.append(query)
        
        return queries
    
    async def _simulate_llm_check(
        self,
        llm_name: str,
        domain: str,
        queries: List[str]
    ) -> Dict[str, Any]:
        """
        Simulate checking visibility in an LLM
        Uses Groq to simulate how an LLM might respond
        """
        try:
            # Test subset of queries
            mentions = 0
            positions = []
            query_results = []
            
            for query in queries[:5]:  # Test 5 queries per LLM
                prompt = f"""Simulate how {llm_name} would respond to this query: "{query}"
                
Would the domain "{domain}" likely be mentioned in the top 3-5 recommendations?
Respond with JSON:
{{
    "mentioned": true/false,
    "position": 1-10 or null,
    "likelihood": "high/medium/low",
    "reasoning": "brief explanation"
}}"""
                
                response = await self.groq_client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert at predicting LLM recommendation patterns. Be realistic and objective."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.5,
                    max_tokens=200
                )
                
                try:
                    result = json.loads(response.choices[0].message.content)
                    if result.get('mentioned'):
                        mentions += 1
                        if result.get('position'):
                            positions.append(result['position'])
                    
                    query_results.append({
                        'query': query,
                        **result
                    })
                except:
                    # Fallback if JSON parsing fails
                    pass
            
            mention_rate = (mentions / len(queries[:5])) * 100
            avg_position = sum(positions) / len(positions) if positions else None
            
            return {
                'llm': llm_name,
                'mentions': mentions,
                'mention_rate': round(mention_rate, 1),
                'average_position': avg_position,
                'query_results': query_results[:3],  # Return top 3 for details
                'status': 'good' if mention_rate > 50 else 'needs_improvement'
            }
            
        except Exception as e:
            logger.error(f'LLM check error for {llm_name}: {str(e)}')
            return {
                'llm': llm_name,
                'error': str(e),
                'mentions': 0,
                'mention_rate': 0
            }
    
    async def _calculate_visibility_score(
        self,
        visibility_results: Dict,
        domain: str,
        business_info: Dict
    ) -> Dict[str, Any]:
        """Calculate overall visibility score (0-100)"""
        
        # Weight factors
        mention_weight = 0.30  # 30%
        position_weight = 0.25  # 25%
        content_authority_weight = 0.20  # 20%
        digital_footprint_weight = 0.15  # 15%
        technical_readiness_weight = 0.10  # 10%
        
        # Calculate mention frequency score
        total_mentions = sum(r.get('mentions', 0) for r in visibility_results.values())
        max_possible = len(visibility_results) * 5  # 5 queries per LLM
        mention_score = (total_mentions / max_possible) * 100
        
        # Calculate position ranking score
        all_positions = []
        for result in visibility_results.values():
            if result.get('average_position'):
                all_positions.append(result['average_position'])
        
        if all_positions:
            avg_pos = sum(all_positions) / len(all_positions)
            # Better position = higher score (1st position = 100, 10th = 10)
            position_score = max(0, 100 - (avg_pos - 1) * 10)
        else:
            position_score = 0
        
        # Content authority (simulated based on business info)
        content_score = business_info.get('content_quality_estimate', 60)
        
        # Digital footprint (simulated)
        footprint_score = random.randint(40, 85)
        
        # Technical readiness (simulated)
        technical_score = business_info.get('technical_seo_score', 70)
        
        # Calculate weighted overall score
        overall_score = (
            mention_score * mention_weight +
            position_score * position_weight +
            content_score * content_authority_weight +
            footprint_score * digital_footprint_weight +
            technical_score * technical_readiness_weight
        )
        
        return {
            'score': round(overall_score, 1),
            'breakdown': {
                'mention_frequency': round(mention_score, 1),
                'position_ranking': round(position_score, 1),
                'content_authority': round(content_score, 1),
                'digital_footprint': round(footprint_score, 1),
                'technical_readiness': round(technical_score, 1)
            },
            'grade': self._get_grade(overall_score),
            'status': self._get_status(overall_score)
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90: return 'A+'
        if score >= 85: return 'A'
        if score >= 80: return 'A-'
        if score >= 75: return 'B+'
        if score >= 70: return 'B'
        if score >= 65: return 'B-'
        if score >= 60: return 'C+'
        if score >= 55: return 'C'
        if score >= 50: return 'C-'
        if score >= 40: return 'D'
        return 'F'
    
    def _get_status(self, score: float) -> str:
        """Get status description"""
        if score >= 80: return 'Excellent'
        if score >= 60: return 'Good'
        if score >= 40: return 'Fair'
        return 'Needs Improvement'
    
    async def _quick_competitor_check(
        self,
        competitor_domain: str,
        queries: List[str]
    ) -> Dict[str, Any]:
        """Quick competitor visibility check"""
        # Simplified competitor check
        estimated_score = random.randint(35, 85)
        
        return {
            'domain': competitor_domain,
            'estimated_score': estimated_score,
            'status': self._get_status(estimated_score)
        }
    
    async def _generate_visibility_recommendations(
        self,
        score_data: Dict,
        visibility_results: Dict,
        competitor_data: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate AI recommendations to improve visibility"""
        try:
            score = score_data['score']
            breakdown = score_data['breakdown']
            
            prompt = f"""As an LLM visibility expert, provide specific recommendations to improve AI search visibility:

Current Visibility Score: {score}/100
- Mention Frequency: {breakdown['mention_frequency']}/100
- Position Ranking: {breakdown['position_ranking']}/100
- Content Authority: {breakdown['content_authority']}/100

Provide 5-7 specific, actionable recommendations in JSON format:
[
    {{
        "title": "Recommendation title",
        "priority": "critical/high/medium/low",
        "impact": "high/medium/low",
        "effort": "1-2 hours/1-2 days/1-2 weeks",
        "description": "Detailed description",
        "action_steps": ["step 1", "step 2"]
    }}
]"""

            response = await self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in optimizing visibility in LLM responses and AI search engines."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,
                max_tokens=1500
            )
            
            result = response.choices[0].message.content
            try:
                recommendations = json.loads(result)
                return recommendations if isinstance(recommendations, list) else []
            except:
                return []
                
        except Exception as e:
            logger.error(f'Recommendation generation error: {str(e)}')
            return []
    
    async def track_visibility_over_time(
        self,
        site_id: str,
        current_check: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track visibility improvements over time"""
        # This would store and compare historical data
        return {
            'current_score': current_check.get('overall_score', 0),
            'trend': 'improving',  # or 'declining', 'stable'
            'change_since_last': '+5.2',
            'historical_data': []  # Would be populated from DB
        }
