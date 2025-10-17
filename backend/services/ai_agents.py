from abc import ABC, abstractmethod
from typing import Dict, Any, List
import httpx
from core.config import get_settings
import json

settings = get_settings()

class BaseAIAgent(ABC):
    """Abstract base class for AI agents following Open/Closed Principle"""
    
    def __init__(self, name: str, purpose: str, context: Dict[str, Any] = None):
        self.name = name
        self.purpose = purpose
        self.context = context or {}
        self.conversation_history = []
    
    @abstractmethod
    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process user message and return response"""
        pass
    
    async def call_llm(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Call LLM API with messages using Emergent LLM key"""
        try:
            # Use Emergent LLM key with OpenAI API
            emergent_key = settings.EMERGENT_LLM_KEY
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {emergent_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'gpt-4o-mini',
                        'messages': messages,
                        'temperature': temperature,
                        'max_tokens': 2000
                    },
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    error_detail = response.text
                    raise Exception(f"LLM API error ({response.status_code}): {error_detail}")
                
                result = response.json()
                
                if 'choices' not in result or not result['choices']:
                    raise Exception(f"Invalid LLM API response: {result}")
                
                return result['choices'][0]['message']['content']
        except httpx.TimeoutException:
            raise Exception("LLM API timeout. Please try again.")
        except Exception as e:
            # Log error but provide friendly message
            import logging
            logging.error(f"LLM API call failed: {str(e)}")
            raise Exception(f"AI service error: {str(e)}")

class SEOAuditAgent(BaseAIAgent):
    """AI Agent specialized in SEO audits and recommendations"""
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        # Get real audit data from context if available
        audit_data = self.context.get('latest_audit', {})
        crawl_data = self.context.get('crawl_data', {})
        
        # Build context with real data
        context_info = []
        if audit_data:
            context_info.append(f"Latest SEO Score: {audit_data.get('seo_score', 'N/A')}/100")
            context_info.append(f"Technical: {audit_data.get('technical_score', 'N/A')}/100")
            context_info.append(f"On-Page: {audit_data.get('onpage_score', 'N/A')}/100")
            context_info.append(f"Issues Found: {len(audit_data.get('issues', []))}")
        
        if crawl_data and crawl_data.get('success'):
            meta = crawl_data.get('meta', {})
            content = crawl_data.get('content', {})
            performance = crawl_data.get('performance', {})
            
            context_info.append("\nReal Website Data:")
            context_info.append(f"- Title: '{meta.get('title', 'N/A')}'")
            context_info.append(f"- Word Count: {content.get('word_count', 0)}")
            context_info.append(f"- Load Time: {performance.get('load_time_seconds', 0)}s")
            context_info.append(f"- Images: {crawl_data.get('images', {}).get('total_images', 0)}")
            context_info.append(f"- H1 Tags: {content.get('h1_count', 0)}")
        
        system_prompt = f"""
You are an expert SEO audit assistant named {self.name}. Your purpose is to help users understand and fix SEO issues on their websites.

REAL WEBSITE DATA:
{chr(10).join(context_info) if context_info else 'No audit data available yet. Ask user to run an audit first.'}

Provide clear, actionable SEO advice. Break down technical concepts into simple terms. 
Always prioritize recommendations by impact and ease of implementation.
Base your advice on the REAL data provided above.
"""
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            *self.conversation_history[-5:],  # Last 5 messages for context
            {'role': 'user', 'content': message}
        ]
        
        response = await self.call_llm(messages)
        
        # Update conversation history
        self.conversation_history.append({'role': 'user', 'content': message})
        self.conversation_history.append({'role': 'assistant', 'content': response})
        
        # Generate suggestions based on real data
        suggestions = await self._generate_suggestions(message, response, audit_data, crawl_data)
        
        return {
            'response': response,
            'suggestions': suggestions
        }
    
    async def _generate_suggestions(self, user_message: str, agent_response: str, audit_data: Dict, crawl_data: Dict) -> List[str]:
        """Generate follow-up suggestions based on real data"""
        suggestions = []
        
        if not audit_data:
            return ['Run an audit first', 'Add your website', 'Check SEO basics']
        
        issues = audit_data.get('issues', [])
        critical = [i for i in issues if i.get('severity') == 'critical']
        high = [i for i in issues if i.get('severity') == 'high']
        
        if critical:
            suggestions.append('Fix critical issues first')
        if high:
            suggestions.append('Review high priority items')
        
        if crawl_data and crawl_data.get('success'):
            meta = crawl_data.get('meta', {})
            content = crawl_data.get('content', {})
            
            if not meta.get('has_description'):
                suggestions.append('Add meta description')
            if content.get('word_count', 0) < 500:
                suggestions.append('Expand content length')
            if content.get('h1_count', 0) == 0:
                suggestions.append('Add H1 heading')
        
        return suggestions[:3]

class KeywordResearchAgent(BaseAIAgent):
    """AI Agent specialized in keyword research and strategy"""
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        system_prompt = f"""
You are an expert keyword research specialist named {self.name}. You help users discover profitable keywords and develop effective content strategies.

Context: {json.dumps(self.context, indent=2)}

Provide keyword suggestions with search intent analysis, difficulty estimates, and content recommendations.
Focus on long-tail keywords and semantic variations.
"""
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            *self.conversation_history[-5:],
            {'role': 'user', 'content': message}
        ]
        
        response = await self.call_llm(messages)
        
        self.conversation_history.append({'role': 'user', 'content': message})
        self.conversation_history.append({'role': 'assistant', 'content': response})
        
        suggestions = [
            'Analyze keyword clusters',
            'Find question-based keywords',
            'Compare with competitors'
        ]
        
        return {
            'response': response,
            'suggestions': suggestions
        }

class ContentOptimizationAgent(BaseAIAgent):
    """AI Agent specialized in content optimization"""
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        system_prompt = f"""
You are an expert content optimization specialist named {self.name}. You help users create and optimize content for better search rankings.

Context: {json.dumps(self.context, indent=2)}

Provide specific recommendations for improving content, including:
- Keyword placement and density
- Content structure and headings
- Internal linking opportunities
- Meta tags optimization
- Readability improvements
"""
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            *self.conversation_history[-5:],
            {'role': 'user', 'content': message}
        ]
        
        response = await self.call_llm(messages)
        
        self.conversation_history.append({'role': 'user', 'content': message})
        self.conversation_history.append({'role': 'assistant', 'content': response})
        
        suggestions = [
            'Generate optimized title',
            'Create meta description',
            'Suggest header structure'
        ]
        
        return {
            'response': response,
            'suggestions': suggestions
        }

class CompetitorAnalysisAgent(BaseAIAgent):
    """AI Agent specialized in competitor analysis"""
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        system_prompt = f"""
You are an expert competitor analysis specialist named {self.name}. You help users understand their competition and find opportunities.

Context: {json.dumps(self.context, indent=2)}

Analyze competitor strategies and provide actionable insights for outranking them.
Focus on gaps and opportunities.
"""
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            *self.conversation_history[-5:],
            {'role': 'user', 'content': message}
        ]
        
        response = await self.call_llm(messages)
        
        self.conversation_history.append({'role': 'user', 'content': message})
        self.conversation_history.append({'role': 'assistant', 'content': response})
        
        suggestions = [
            'Find competitor keywords',
            'Analyze content gaps',
            'Review backlink strategies'
        ]
        
        return {
            'response': response,
            'suggestions': suggestions
        }


class LLMVisibilityAgent(BaseAIAgent):
    """AI Agent specialized in LLM Visibility Optimization - Remembers website-specific context"""
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        # Get comprehensive website data from context
        website_url = self.context.get('website_url', 'your website')
        site_id = self.context.get('site_id')
        
        # Build comprehensive context from all available data
        context_parts = [f"Website: {website_url}"]
        
        # Latest audit data
        latest_audit = self.context.get('latest_audit', {})
        if latest_audit:
            context_parts.append(f"\nLatest SEO Score: {latest_audit.get('seo_score', 'N/A')}/100")
            context_parts.append(f"Technical: {latest_audit.get('technical_score', 'N/A')}/100")
            context_parts.append(f"On-Page: {latest_audit.get('onpage_score', 'N/A')}/100")
            issues_count = len(latest_audit.get('issues', []))
            context_parts.append(f"Issues Found: {issues_count}")
        
        # LLM Visibility data
        visibility_data = self.context.get('llm_visibility', {})
        if visibility_data:
            context_parts.append(f"\n📊 LLM Visibility Score: {visibility_data.get('overall_score', 'N/A')}/100")
            llm_breakdown = visibility_data.get('visibility_by_llm', {})
            if llm_breakdown:
                context_parts.append("LLM-specific scores:")
                for llm_name, score in llm_breakdown.items():
                    context_parts.append(f"  - {llm_name}: {score}/100")
        
        # Recommendations
        recommendations = self.context.get('recommendations', {})
        if recommendations:
            total_recs = recommendations.get('total_recommendations', 0)
            context_parts.append(f"\n💡 Generated Recommendations: {total_recs}")
            high_priority = recommendations.get('high_priority', [])
            if high_priority:
                context_parts.append("Top priority actions:")
                for i, rec in enumerate(high_priority[:3], 1):
                    context_parts.append(f"  {i}. {rec.get('title', 'N/A')}")
        
        # Content gap analysis
        content_gaps = self.context.get('content_gaps', {})
        if content_gaps:
            gaps = content_gaps.get('gaps', [])
            if gaps:
                context_parts.append(f"\n📝 Content Gaps Identified: {len(gaps)}")
        
        # Community opportunities
        community_data = self.context.get('community_opportunities', {})
        if community_data:
            opps = community_data.get('opportunities', [])
            if opps:
                context_parts.append(f"\n👥 Community Opportunities: {len(opps)}")
        
        # Backlink data
        backlink_data = self.context.get('backlink_analysis', {})
        if backlink_data:
            opportunities = backlink_data.get('opportunities', [])
            if opportunities:
                context_parts.append(f"\n🔗 Backlink Opportunities: {len(opportunities)}")
        
        # Historical data count
        audit_count = self.context.get('total_audits', 0)
        if audit_count:
            context_parts.append(f"\n📊 Total Audits Performed: {audit_count}")
        
        context_summary = '\n'.join(context_parts)
        
        system_prompt = f"""
You are an expert LLM Visibility Optimization specialist named {self.name}. 

Your mission is to help improve the visibility and discoverability of websites in AI-powered search engines 
like ChatGPT, Claude, Gemini, and Perplexity.

WEBSITE-SPECIFIC CONTEXT (This is your memory):
{context_summary}

IMPORTANT: You REMEMBER all previous audits, analyses, and recommendations for this specific website.
Use this historical context to provide continuity in your advice.

Your expertise includes:
- Analyzing LLM visibility scores and providing actionable improvements
- Identifying content gaps that prevent AI recommendations
- Optimizing content structure for LLM comprehension
- Building authority signals that AI systems trust
- Community engagement strategies for visibility
- Schema markup and structured data optimization
- Backlink strategies that improve LLM trust

Always:
1. Reference specific data from the context above
2. Track progress over time (compare current vs. historical data)
3. Provide step-by-step, actionable recommendations
4. Prioritize high-impact, achievable improvements
5. Explain WHY each recommendation matters for LLM visibility

If no data is available yet, guide the user to run analyses first.
"""
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            *self.conversation_history[-10:],  # More history for better context
            {'role': 'user', 'content': message}
        ]
        
        response = await self.call_llm(messages)
        
        # Update conversation history
        self.conversation_history.append({'role': 'user', 'content': message})
        self.conversation_history.append({'role': 'assistant', 'content': response})
        
        # Generate smart suggestions based on available data
        suggestions = await self._generate_smart_suggestions(message, response)
        
        return {
            'response': response,
            'suggestions': suggestions,
            'context_loaded': True,
            'website': website_url
        }
    
    async def _generate_smart_suggestions(self, user_message: str, agent_response: str) -> List[str]:
        """Generate context-aware follow-up suggestions"""
        suggestions = []
        
        # Check what data we have and suggest next steps
        if not self.context.get('llm_visibility'):
            suggestions.append('🤖 Run LLM Visibility Check')
        
        if not self.context.get('recommendations'):
            suggestions.append('💡 Generate Recommendations')
        
        if not self.context.get('content_gaps'):
            suggestions.append('📝 Analyze Content Gaps')
        
        if not self.context.get('community_opportunities'):
            suggestions.append('👥 Find Community Opportunities')
        
        if not self.context.get('backlink_analysis'):
            suggestions.append('🔗 Analyze Backlink Strategy')
        
        # If we have visibility data, suggest improvements based on score
        visibility = self.context.get('llm_visibility', {})
        if visibility:
            score = visibility.get('overall_score', 0)
            if score < 50:
                suggestions.append('🚀 Quick wins to boost visibility')
            elif score < 75:
                suggestions.append('📈 Medium-priority improvements')
            else:
                suggestions.append('🎯 Advanced optimization tactics')
        
        # Always offer to show progress
        if self.context.get('total_audits', 0) > 1:
            suggestions.append('📊 Show improvement progress')
        
        return suggestions[:4]  # Top 4 suggestions

# Agent Factory (Dependency Inversion Principle)
class AgentFactory:
    """Factory for creating appropriate agent instances"""
    
    @staticmethod
    def create_agent(purpose: str, name: str, context: Dict[str, Any] = None) -> BaseAIAgent:
        agents = {
            'audit_assistant': SEOAuditAgent,
            'keyword_researcher': KeywordResearchAgent,
            'content_optimizer': ContentOptimizationAgent,
            'competitor_analyst': CompetitorAnalysisAgent,
            'llm_visibility_optimizer': LLMVisibilityAgent
        }
        
        agent_class = agents.get(purpose, SEOAuditAgent)
        return agent_class(name, purpose, context)
