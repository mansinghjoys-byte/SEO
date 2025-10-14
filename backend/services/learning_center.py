"""
Learning Center & Support Service
Provides tutorials, knowledge base, and AI assistance
"""
from typing import Dict, List, Any, Optional
from groq import AsyncGroq
from core.config import get_settings
import logging
import json

logger = logging.getLogger(__name__)
settings = get_settings()


class LearningCenterService:
    """Service for learning resources and support"""
    
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    
    def get_knowledge_base(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get knowledge base articles
        """
        return {
            'getting_started': [
                {
                    'title': 'How LLMs Work (Simplified)',
                    'category': 'basics',
                    'content': 'LLMs (Large Language Models) like ChatGPT, Claude, and Gemini are AI systems that can understand and generate human-like text. They learn from vast amounts of web content and provide answers to questions. To appear in LLM responses, your website needs high-quality, authoritative content that these AI systems can reference.',
                    'read_time': '3 min'
                },
                {
                    'title': 'First 5 Things to Do',
                    'category': 'quick_start',
                    'content': '''1. Add your website and run initial audit\n2. Check your LLM visibility score\n3. Review top 3 quick-win recommendations\n4. Add FAQ schema to your homepage\n5. Create one comprehensive guide article''',
                    'read_time': '5 min'
                },
                {
                    'title': 'Understanding Your Visibility Score',
                    'category': 'basics',
                    'content': 'Your LLM visibility score (0-100) measures how likely AI assistants are to recommend your business. It factors in: mention frequency (30%), position ranking (25%), content authority (20%), digital footprint (15%), and technical readiness (10%).',
                    'read_time': '4 min'
                }
            ],
            'best_practices': [
                {
                    'title': 'Content Best Practices',
                    'category': 'content',
                    'content': 'Create comprehensive, well-structured content that directly answers questions. Use clear headings, include examples, cite sources, and maintain E-E-A-T (Experience, Expertise, Authoritativeness, Trust) signals. Aim for depth over breadth.',
                    'read_time': '6 min'
                },
                {
                    'title': 'Technical SEO Essentials',
                    'category': 'technical',
                    'content': 'Ensure HTTPS, fast load times (<3s), mobile responsiveness, canonical tags, and proper meta descriptions. Use schema markup (JSON-LD) for structured data. These technical factors help LLMs understand and trust your content.',
                    'read_time': '7 min'
                },
                {
                    'title': 'Community Engagement Guide',
                    'category': 'marketing',
                    'content': 'Be genuinely helpful first on Reddit, Quora, and forums. Answer questions thoroughly, share experience, provide value without being salesy. Only mention your product naturally when relevant. Build reputation before promoting.',
                    'read_time': '8 min'
                }
            ],
            'advanced': [
                {
                    'title': 'Schema Markup Deep Dive',
                    'category': 'technical',
                    'content': 'Implement multiple schema types: Organization, Product, FAQ, HowTo, Article, and Breadcrumb. Use Google\'s Structured Data Testing Tool to validate. Schema helps LLMs extract and cite specific information from your site.',
                    'read_time': '10 min'
                },
                {
                    'title': 'Advanced Link Building',
                    'category': 'marketing',
                    'content': 'Focus on authoritative backlinks from industry-specific sites. Guest posting, broken link building, and resource page inclusions are most effective. Quality matters more than quantity - one high-authority link beats 100 low-quality ones.',
                    'read_time': '12 min'
                }
            ],
            'case_studies': [
                {
                    'title': 'From 0 to 70+ Visibility Score in 90 Days',
                    'category': 'case_study',
                    'content': 'SaaS company increased LLM visibility by: (1) Creating 8 comprehensive guides, (2) Adding schema markup, (3) Engaging on 3 subreddits weekly, (4) Building 15 high-quality backlinks. Result: Mentioned in 67% of relevant LLM queries.',
                    'read_time': '8 min'
                }
            ]
        }
    
    def get_tutorials(self) -> List[Dict[str, Any]]:
        """
        Get interactive tutorials
        """
        return [
            {
                'id': 'tutorial_1',
                'title': 'Setting Up Your First Site Audit',
                'duration': '5 minutes',
                'difficulty': 'beginner',
                'steps': [
                    {'step': 1, 'title': 'Add Your Website', 'description': 'Click "Add Site" and enter your URL'},
                    {'step': 2, 'title': 'Run Initial Audit', 'description': 'Click "Run Audit" to analyze your site'},
                    {'step': 3, 'title': 'Review Results', 'description': 'Check your SEO score and identified issues'},
                    {'step': 4, 'title': 'Check Visibility', 'description': 'Run LLM visibility check'},
                    {'step': 5, 'title': 'Start with Quick Wins', 'description': 'Implement top 3 quick-win recommendations'}
                ]
            },
            {
                'id': 'tutorial_2',
                'title': 'Adding Schema Markup',
                'duration': '15 minutes',
                'difficulty': 'intermediate',
                'steps': [
                    {'step': 1, 'title': 'Choose Schema Type', 'description': 'Select FAQ, Product, or Article schema'},
                    {'step': 2, 'title': 'Generate Code', 'description': 'Use our schema generator tool'},
                    {'step': 3, 'title': 'Add to Website', 'description': 'Paste code in <head> section'},
                    {'step': 4, 'title': 'Validate', 'description': 'Test with Google Rich Results Test'},
                    {'step': 5, 'title': 'Monitor', 'description': 'Wait 2-3 weeks and check visibility improvement'}
                ]
            },
            {
                'id': 'tutorial_3',
                'title': 'Engaging on Reddit Effectively',
                'duration': '20 minutes',
                'difficulty': 'intermediate',
                'steps': [
                    {'step': 1, 'title': 'Find Opportunities', 'description': 'Use Community Hub to find relevant discussions'},
                    {'step': 2, 'title': 'Read Community Rules', 'description': 'Check subreddit rules before posting'},
                    {'step': 3, 'title': 'Craft Response', 'description': 'Use AI assistant to generate helpful response'},
                    {'step': 4, 'title': 'Post Authentically', 'description': 'Review, personalize, and post'},
                    {'step': 5, 'title': 'Track Engagement', 'description': 'Monitor upvotes and replies'}
                ]
            }
        ]
    
    async def ai_assistant(
        self,
        user_question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        AI-powered support assistant
        """
        try:
            context_str = ''
            if context:
                context_str = f"\nUser Context: {json.dumps(context)}"
            
            prompt = f"""You are a helpful LLM visibility optimization expert. Answer this user question:

Question: {user_question}{context_str}

Provide a clear, concise, actionable answer. Include specific steps if applicable."""

            response = await self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert assistant helping users improve their LLM visibility. Be helpful, clear, and specific."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            answer = response.choices[0].message.content
            
            return {
                'success': True,
                'answer': answer,
                'related_articles': self._find_related_articles(user_question)
            }
            
        except Exception as e:
            logger.error(f'AI assistant error: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def _find_related_articles(self, question: str) -> List[str]:
        """
        Find related knowledge base articles
        """
        question_lower = question.lower()
        related = []
        
        if any(word in question_lower for word in ['schema', 'markup', 'structured']):
            related.append('Schema Markup Deep Dive')
        
        if any(word in question_lower for word in ['content', 'write', 'article']):
            related.append('Content Best Practices')
        
        if any(word in question_lower for word in ['reddit', 'quora', 'community']):
            related.append('Community Engagement Guide')
        
        if any(word in question_lower for word in ['backlink', 'link', 'guest post']):
            related.append('Advanced Link Building')
        
        return related[:3]  # Return top 3
    
    def get_faq(self) -> List[Dict[str, str]]:
        """
        Get frequently asked questions
        """
        return [
            {
                'question': 'How long does it take to see results?',
                'answer': 'Most users see initial improvements in 4-6 weeks. Significant visibility gains typically occur within 90 days of consistent implementation. Quick wins like adding schema markup can show results in 2-3 weeks.'
            },
            {
                'question': 'Do I need technical knowledge?',
                'answer': 'No! Our platform provides step-by-step instructions for every task. For technical changes like schema markup, we provide copy-paste code snippets. If you can use WordPress or Shopify, you can use our platform.'
            },
            {
                'question': 'How is this different from traditional SEO?',
                'answer': 'Traditional SEO focuses on Google search rankings. LLM visibility optimization focuses on being recommended by AI assistants like ChatGPT, Claude, and Gemini. Both are important, and many tactics overlap, but LLM optimization emphasizes comprehensive content, clear structure, and authoritative references.'
            },
            {
                'question': 'Which plan should I choose?',
                'answer': 'Start with Starter plan if you have 1-3 websites and want weekly audits. Upgrade to Growth for daily audits and AI agents. Professional plan is for businesses with 5-10 sites needing real-time monitoring. Agency plan is for managing multiple client sites.'
            },
            {
                'question': 'Can I cancel anytime?',
                'answer': 'Yes, you can cancel your subscription at any time. Your access will continue until the end of your billing period. Unused credits do not roll over after cancellation.'
            }
        ]
