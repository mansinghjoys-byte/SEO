from typing import Dict, Any, List
import httpx
from core.config import get_settings
import re
import asyncio

settings = get_settings()

class KeywordService:
    """Service for keyword research and analysis"""
    
    async def research_keywords(self, seed_keyword: str, site_url: str = None) -> List[Dict[str, Any]]:
        """Research keywords using AI analysis"""
        
        # Generate keyword variations using AI
        variations = await self._generate_variations(seed_keyword)
        
        # Analyze each keyword
        results = []
        for keyword in variations:
            analysis = await self._analyze_keyword(keyword, site_url)
            results.append(analysis)
        
        return sorted(results, key=lambda x: x['opportunity_score'], reverse=True)
    
    async def _generate_variations(self, seed_keyword: str) -> List[str]:
        """Generate keyword variations using AI"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {settings.GROQ_API_KEY}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': settings.GROQ_MODEL,
                        'messages': [
                            {
                                'role': 'system',
                                'content': 'You are an SEO keyword research expert. Generate 15 related keyword variations including long-tail keywords, questions, and semantic variations.'
                            },
                            {
                                'role': 'user',
                                'content': f'Generate keyword variations for: {seed_keyword}. Return only the keywords, one per line, no numbering or extra text.'
                            }
                        ],
                        'temperature': 0.8,
                        'max_tokens': 500
                    },
                    timeout=30.0
                )
                
                result = response.json()
                content = result['choices'][0]['message']['content']
                keywords = [k.strip() for k in content.split('\n') if k.strip()]
                return keywords[:15]
            except:
                # Fallback variations
                return [
                    seed_keyword,
                    f'{seed_keyword} guide',
                    f'best {seed_keyword}',
                    f'how to {seed_keyword}',
                    f'{seed_keyword} tips'
                ]
    
    async def _analyze_keyword(self, keyword: str, site_url: str = None) -> Dict[str, Any]:
        """Analyze individual keyword"""
        
        # Estimate metrics (in production, use real API)
        word_count = len(keyword.split())
        
        # Long-tail keywords are generally easier
        if word_count >= 3:
            difficulty = 30 + (word_count * 5)
            search_volume = 500 - (word_count * 50)
        else:
            difficulty = 60 + (word_count * 10)
            search_volume = 2000 - (word_count * 200)
        
        # Determine search intent
        intent = self._determine_intent(keyword)
        
        # Calculate opportunity score
        opportunity_score = (search_volume / 100) * (100 - difficulty) / 100
        
        return {
            'keyword': keyword,
            'search_volume': max(0, search_volume),
            'difficulty': min(100, max(0, difficulty)),
            'intent': intent,
            'opportunity_score': int(opportunity_score),
            'cpc': round(0.5 + (difficulty / 50), 2)
        }
    
    def _determine_intent(self, keyword: str) -> str:
        """Determine search intent from keyword"""
        keyword_lower = keyword.lower()
        
        if any(word in keyword_lower for word in ['buy', 'price', 'cheap', 'discount', 'deal']):
            return 'commercial'
        elif any(word in keyword_lower for word in ['how', 'what', 'why', 'guide', 'tutorial']):
            return 'informational'
        elif any(word in keyword_lower for word in ['login', 'download', 'sign up', 'contact']):
            return 'transactional'
        else:
            return 'navigational'
    
    async def analyze_competitors(self, keyword: str, competitor_urls: List[str]) -> List[Dict[str, Any]]:
        """Analyze how competitors rank for a keyword"""
        results = []
        
        for url in competitor_urls:
            analysis = {
                'url': url,
                'estimated_rank': len(results) + 1,
                'keyword': keyword,
                'title_matches': False,
                'content_optimized': False
            }
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url)
                    content = response.text.lower()
                    
                    # Check if keyword appears in title
                    title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE)
                    if title_match and keyword.lower() in title_match.group(1).lower():
                        analysis['title_matches'] = True
                    
                    # Check content optimization
                    keyword_count = content.count(keyword.lower())
                    if keyword_count >= 3:
                        analysis['content_optimized'] = True
                    
                    analysis['keyword_density'] = round((keyword_count / len(content.split())) * 100, 2)
            except:
                pass
            
            results.append(analysis)
        
        return results
