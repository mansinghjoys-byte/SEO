import httpx
from typing import Dict, Any
from core.config import get_settings
import json
import base64

settings = get_settings()

class PayPalService:
    """Service for PayPal payment processing"""
    
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.mode = settings.PAYPAL_MODE
        
        if self.mode == 'sandbox':
            self.base_url = 'https://api-m.sandbox.paypal.com'
        else:
            self.base_url = 'https://api-m.paypal.com'
    
    async def get_access_token(self) -> str:
        """Get PayPal OAuth access token"""
        auth = base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode()).decode()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.base_url}/v1/oauth2/token',
                headers={
                    'Authorization': f'Basic {auth}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data='grant_type=client_credentials'
            )
            
            result = response.json()
            return result['access_token']
    
    async def create_order(self, amount: float, currency: str = 'USD', description: str = '') -> Dict[str, Any]:
        """Create PayPal order"""
        access_token = await self.get_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.base_url}/v2/checkout/orders',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json={
                    'intent': 'CAPTURE',
                    'purchase_units': [
                        {
                            'amount': {
                                'currency_code': currency,
                                'value': str(amount)
                            },
                            'description': description
                        }
                    ],
                    'application_context': {
                        'return_url': 'https://yoursite.com/payment/success',
                        'cancel_url': 'https://yoursite.com/payment/cancel'
                    }
                }
            )
            
            return response.json()
    
    async def capture_order(self, order_id: str) -> Dict[str, Any]:
        """Capture PayPal order after approval"""
        access_token = await self.get_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.base_url}/v2/checkout/orders/{order_id}/capture',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
            )
            
            return response.json()
    
    async def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Get PayPal order details"""
        access_token = await self.get_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.base_url}/v2/checkout/orders/{order_id}',
                headers={
                    'Authorization': f'Bearer {access_token}'
                }
            )
            
            return response.json()

# Pricing plans
PRICING_PLANS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'credits_per_month': 20,
        'features': [
            '1 website',
            'Monthly site audits',
            '10 keyword tracking',
            'Basic recommendations',
            'LLM visibility check (1/month)',
            'Community support',
            'Learning center access'
        ],
        'limits': {
            'sites': 1,
            'audits_per_month': 4,
            'llm_checks': 1,
            'content_generation': 0
        }
    },
    'starter': {
        'name': 'Starter',
        'price': 49,
        'credits_per_month': 100,
        'features': [
            '3 websites',
            'Weekly site audits',
            '50 keywords tracked',
            'LLM visibility tracking',
            'Content gap analysis',
            'AI content outlines (3/month)',
            'Schema markup generator',
            'Community opportunities',
            'Priority support'
        ],
        'limits': {
            'sites': 3,
            'audits_per_month': 12,
            'llm_checks': 4,
            'content_generation': 3
        }
    },
    'growth': {
        'name': 'Growth',
        'price': 79,
        'credits_per_month': 200,
        'features': [
            '5 websites',
            'Daily site audits',
            '100 keywords tracked',
            'Competitor tracking (3)',
            'AI SEO agents',
            'White-label reports'
        ]
    },
    'professional': {
        'name': 'Professional',
        'price': 149,
        'credits_per_month': 500,
        'features': [
            '10 websites',
            'Real-time monitoring',
            '500 keywords tracked',
            'Competitor tracking (5)',
            'API access',
            'Link building tools',
            'Dedicated support'
        ]
    },
    'agency': {
        'name': 'Agency',
        'price': 399,
        'credits_per_month': 2000,
        'features': [
            '50 websites',
            'Unlimited audits',
            '2,500 keywords tracked',
            'Competitor tracking (10)',
            'Client portal access',
            'Team collaboration',
            'Account manager'
        ]
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 999,
        'credits_per_month': 10000,
        'features': [
            'Unlimited websites',
            'Custom crawl frequency',
            'Unlimited keywords',
            'Custom ML models',
            'SSO integration',
            'White-label platform',
            'Dedicated infrastructure'
        ]
    }
}

CREDIT_COSTS = {
    # Existing features
    'site_audit': 5,
    'keyword_research': 2,
    'content_optimization': 3,
    'competitor_analysis': 4,
    'rank_tracking': 1,
    'ai_agent_chat': 1,
    
    # New LLM Visibility Optimizer features
    'deep_analysis': 10,
    'llm_visibility_check': 8,
    'content_gap_analysis': 6,
    'content_generation': 4,
    'content_enhancement': 3,
    'schema_generation': 2,
    'community_opportunities': 3,
    'response_generation': 2,
    'backlink_analysis': 5,
    'outreach_email': 1,
    'weekly_report': 2
}
