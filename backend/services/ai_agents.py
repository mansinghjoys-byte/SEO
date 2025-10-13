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
    
    async def call_groq(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Call Groq API with messages"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {settings.GROQ_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': settings.GROQ_MODEL,
                    'messages': messages,
                    'temperature': temperature,
                    'max_tokens': 2000
                },
                timeout=60.0
            )
            result = response.json()
            return result['choices'][0]['message']['content']

class SEOAuditAgent(BaseAIAgent):
    """AI Agent specialized in SEO audits and recommendations"""
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        system_prompt = f"""
You are an expert SEO audit assistant named {self.name}. Your purpose is to help users understand and fix SEO issues on their websites.

Context: {json.dumps(self.context, indent=2)}

Provide clear, actionable SEO advice. Break down technical concepts into simple terms. 
Always prioritize recommendations by impact and ease of implementation.
"""
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            *self.conversation_history[-5:],  # Last 5 messages for context
            {'role': 'user', 'content': message}
        ]
        
        response = await self.call_groq(messages)
        
        # Update conversation history
        self.conversation_history.append({'role': 'user', 'content': message})
        self.conversation_history.append({'role': 'assistant', 'content': response})
        
        # Generate suggestions
        suggestions = await self._generate_suggestions(message, response)
        
        return {
            'response': response,
            'suggestions': suggestions
        }
    
    async def _generate_suggestions(self, user_message: str, agent_response: str) -> List[str]:
        """Generate follow-up suggestions based on conversation"""
        suggestions = []
        
        if 'technical' in user_message.lower():
            suggestions.extend([
                'Analyze page speed issues',
                'Check mobile responsiveness',
                'Review structured data'
            ])
        elif 'keyword' in user_message.lower():
            suggestions.extend([
                'Find related keywords',
                'Analyze keyword difficulty',
                'Check search intent'
            ])
        elif 'content' in user_message.lower():
            suggestions.extend([
                'Optimize existing content',
                'Find content gaps',
                'Review readability'
            ])
        else:
            suggestions.extend([
                'Run full site audit',
                'Analyze top competitors',
                'Review backlink profile'
            ])
        
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
        
        response = await self.call_groq(messages)
        
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
        
        response = await self.call_groq(messages)
        
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
        
        response = await self.call_groq(messages)
        
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

# Agent Factory (Dependency Inversion Principle)
class AgentFactory:
    """Factory for creating appropriate agent instances"""
    
    @staticmethod
    def create_agent(purpose: str, name: str, context: Dict[str, Any] = None) -> BaseAIAgent:
        agents = {
            'audit_assistant': SEOAuditAgent,
            'keyword_researcher': KeywordResearchAgent,
            'content_optimizer': ContentOptimizationAgent,
            'competitor_analyst': CompetitorAnalysisAgent
        }
        
        agent_class = agents.get(purpose, SEOAuditAgent)
        return agent_class(name, purpose, context)
