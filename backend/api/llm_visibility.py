"""
LLM Visibility API Endpoints
Provides endpoints for LLM visibility checking, recommendations, content intelligence, etc.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from core.dependencies import get_current_user
from core.database import get_database
from services.billing import CREDIT_COSTS
from services.llm_visibility_service import LLMVisibilityService
from services.recommendation_engine import RecommendationEngine
from services.content_intelligence import ContentIntelligenceService
from services.community_hub import CommunityHubService
from services.backlink_strategy import BacklinkStrategyService
from services.analytics_service import AnalyticsService
from services.learning_center import LearningCenterService
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix='/llm', tags=['LLM Visibility'])


# Request models
class VisibilityCheckRequest(BaseModel):
    site_id: str
    competitors: Optional[List[str]] = None


class RecommendationRequest(BaseModel):
    site_id: str


class ContentGapRequest(BaseModel):
    site_id: str
    competitors: Optional[List[str]] = None


class ContentOutlineRequest(BaseModel):
    topic: str
    content_type: str = 'guide'
    target_length: int = 2000


class ContentEnhanceRequest(BaseModel):
    content: str
    goals: List[str]


class SchemaGenerateRequest(BaseModel):
    schema_type: str
    data: Dict[str, Any]


class CommunityOpportunitiesRequest(BaseModel):
    site_id: str
    platforms: Optional[List[str]] = None


class ResponseGenerateRequest(BaseModel):
    opportunity: Dict[str, Any]
    site_id: str


class BacklinkAnalysisRequest(BaseModel):
    site_id: str
    competitors: List[str]


class OutreachEmailRequest(BaseModel):
    opportunity: Dict[str, Any]
    site_id: str


class AIAssistantRequest(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = None


# LLM Visibility Endpoints
@router.post('/visibility/check')
async def check_llm_visibility(
    request: VisibilityCheckRequest,
    current_user: dict = Depends(get_current_user)
):
    """Check LLM visibility for a site"""
    db = await get_database()
    
    # Check credits
    cost = CREDIT_COSTS['llm_visibility_check']
    if current_user['credits'] < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. This feature requires {cost} credits.'
        )
    
    # Get site
    site = await db.sites.find_one(
        {'site_id': request.site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    )
    if not site:
        raise HTTPException(status_code=404, detail='Site not found')
    
    # Get business info from latest audit
    audit = await db.audits.find_one(
        {'site_id': request.site_id},
        {'_id': 0},
        sort=[('created_at', -1)]
    )
    
    business_info = {
        'category': site.get('category', 'software'),
        'industry': site.get('industry', 'technology'),
        'content_quality_estimate': audit.get('seo_score', 60) if audit else 60,
        'technical_seo_score': audit.get('technical_score', 70) if audit else 70
    }
    
    # Run visibility check
    visibility_service = LLMVisibilityService()
    result = await visibility_service.check_visibility(
        site['url'],
        business_info,
        request.competitors
    )
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error', 'Check failed'))
    
    # Save result
    check_id = str(uuid.uuid4())
    check_doc = {
        'check_id': check_id,
        'site_id': request.site_id,
        'user_id': current_user['user_id'],
        **result,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    await db.llm_visibility_checks.insert_one(check_doc)
    
    # Deduct credits
    await db.users.update_one(
        {'user_id': current_user['user_id']},
        {'$inc': {'credits': -cost}}
    )
    
    # Log transaction
    await db.credit_transactions.insert_one({
        'user_id': current_user['user_id'],
        'amount': -cost,
        'type': 'llm_visibility_check',
        'description': f'LLM visibility check for {site["url"]}',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return result


@router.get('/visibility/history/{site_id}')
async def get_visibility_history(
    site_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get historical visibility checks"""
    db = await get_database()
    
    checks = await db.llm_visibility_checks.find(
        {'site_id': site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    ).sort('created_at', -1).limit(10).to_list(10)
    
    return {'success': True, 'checks': checks}


# Recommendations Endpoints
@router.post('/recommendations/generate')
async def generate_recommendations(
    request: RecommendationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate actionable recommendations"""
    db = await get_database()
    
    # Get site
    site = await db.sites.find_one(
        {'site_id': request.site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    )
    if not site:
        raise HTTPException(status_code=404, detail='Site not found')
    
    # Get latest data
    audit = await db.audits.find_one(
        {'site_id': request.site_id},
        {'_id': 0},
        sort=[('created_at', -1)]
    )
    
    visibility = await db.llm_visibility_checks.find_one(
        {'site_id': request.site_id},
        {'_id': 0},
        sort=[('created_at', -1)]
    )
    
    # Generate recommendations
    engine = RecommendationEngine()
    result = await engine.generate_recommendations(
        site_data=site,
        audit_data=audit,
        visibility_data=visibility
    )
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error'))
    
    # Save recommendations
    rec_id = str(uuid.uuid4())
    rec_doc = {
        'recommendation_id': rec_id,
        'site_id': request.site_id,
        'user_id': current_user['user_id'],
        **result,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    await db.recommendations.insert_one(rec_doc)
    
    return result


# Content Intelligence Endpoints
@router.post('/content/gap-analysis')
async def content_gap_analysis(
    request: ContentGapRequest,
    current_user: dict = Depends(get_current_user)
):
    """Analyze content gaps"""
    db = await get_database()
    
    # Check credits
    cost = CREDIT_COSTS['content_gap_analysis']
    if current_user['credits'] < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. Need {cost} credits.'
        )
    
    # Get site and audit data
    site = await db.sites.find_one(
        {'site_id': request.site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    )
    if not site:
        raise HTTPException(status_code=404, detail='Site not found')
    
    audit = await db.audits.find_one(
        {'site_id': request.site_id},
        {'_id': 0},
        sort=[('created_at', -1)]
    )
    
    site_content = audit.get('crawl_data', {}).get('content', {}) if audit else {}
    
    # Analyze gaps
    service = ContentIntelligenceService()
    result = await service.analyze_content_gaps(
        site['url'],
        site_content,
        request.competitors
    )
    
    # Deduct credits
    await db.users.update_one(
        {'user_id': current_user['user_id']},
        {'$inc': {'credits': -cost}}
    )
    
    await db.credit_transactions.insert_one({
        'user_id': current_user['user_id'],
        'amount': -cost,
        'type': 'content_gap_analysis',
        'description': f'Content gap analysis for {site["url"]}',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return result


@router.post('/content/generate-outline')
async def generate_content_outline(
    request: ContentOutlineRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate AI content outline"""
    db = await get_database()
    
    # Check credits
    cost = CREDIT_COSTS['content_generation']
    if current_user['credits'] < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. Need {cost} credits.'
        )
    
    service = ContentIntelligenceService()
    result = await service.generate_content_outline(
        request.topic,
        request.content_type,
        request.target_length
    )
    
    # Deduct credits
    await db.users.update_one(
        {'user_id': current_user['user_id']},
        {'$inc': {'credits': -cost}}
    )
    
    await db.credit_transactions.insert_one({
        'user_id': current_user['user_id'],
        'amount': -cost,
        'type': 'content_generation',
        'description': f'Generated outline for: {request.topic}',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return result


@router.post('/content/enhance')
async def enhance_content(
    request: ContentEnhanceRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get content enhancement suggestions"""
    db = await get_database()
    
    # Check credits
    cost = CREDIT_COSTS['content_enhancement']
    if current_user['credits'] < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. Need {cost} credits.'
        )
    
    service = ContentIntelligenceService()
    result = await service.enhance_existing_content(
        request.content,
        request.goals
    )
    
    # Deduct credits
    await db.users.update_one(
        {'user_id': current_user['user_id']},
        {'$inc': {'credits': -cost}}
    )
    
    await db.credit_transactions.insert_one({
        'user_id': current_user['user_id'],
        'amount': -cost,
        'type': 'content_enhancement',
        'description': 'Content enhancement',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return result


@router.post('/content/generate-schema')
async def generate_schema(
    request: SchemaGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate schema markup"""
    db = await get_database()
    
    # Check credits
    cost = CREDIT_COSTS['schema_generation']
    if current_user['credits'] < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. Need {cost} credits.'
        )
    
    service = ContentIntelligenceService()
    result = service.generate_schema_markup(
        request.schema_type,
        request.data
    )
    
    # Deduct credits
    await db.users.update_one(
        {'user_id': current_user['user_id']},
        {'$inc': {'credits': -cost}}
    )
    
    await db.credit_transactions.insert_one({
        'user_id': current_user['user_id'],
        'amount': -cost,
        'type': 'schema_generation',
        'description': f'Generated {request.schema_type} schema',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return result


# Community Hub Endpoints
@router.post('/community/opportunities')
async def find_community_opportunities(
    request: CommunityOpportunitiesRequest,
    current_user: dict = Depends(get_current_user)
):
    """Find community engagement opportunities"""
    db = await get_database()
    
    # Check credits
    cost = CREDIT_COSTS['community_opportunities']
    if current_user['credits'] < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. Need {cost} credits.'
        )
    
    # Get site
    site = await db.sites.find_one(
        {'site_id': request.site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    )
    if not site:
        raise HTTPException(status_code=404, detail='Site not found')
    
    business_info = {
        'name': site.get('name', site['url']),
        'category': site.get('category', 'software'),
        'keywords': site.get('keywords', [])
    }
    
    service = CommunityHubService()
    result = await service.find_opportunities(
        business_info,
        request.platforms
    )
    
    # Deduct credits
    await db.users.update_one(
        {'user_id': current_user['user_id']},
        {'$inc': {'credits': -cost}}
    )
    
    await db.credit_transactions.insert_one({
        'user_id': current_user['user_id'],
        'amount': -cost,
        'type': 'community_opportunities',
        'description': 'Community opportunities search',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return result


@router.post('/community/generate-response')
async def generate_community_response(
    request: ResponseGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate response for community opportunity"""
    db = await get_database()
    
    # Check credits
    cost = CREDIT_COSTS['response_generation']
    if current_user['credits'] < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. Need {cost} credits.'
        )
    
    # Get site
    site = await db.sites.find_one(
        {'site_id': request.site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    )
    if not site:
        raise HTTPException(status_code=404, detail='Site not found')
    
    business_info = {
        'name': site.get('name', site['url']),
        'description': site.get('description', '')
    }
    
    service = CommunityHubService()
    result = await service.generate_response(
        request.opportunity,
        business_info
    )
    
    # Deduct credits
    await db.users.update_one(
        {'user_id': current_user['user_id']},
        {'$inc': {'credits': -cost}}
    )
    
    await db.credit_transactions.insert_one({
        'user_id': current_user['user_id'],
        'amount': -cost,
        'type': 'response_generation',
        'description': 'Community response generated',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return result


# Backlink Strategy Endpoints
@router.post('/backlinks/analyze')
async def analyze_backlinks(
    request: BacklinkAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Analyze backlink gaps"""
    db = await get_database()
    
    # Check credits
    cost = CREDIT_COSTS['backlink_analysis']
    if current_user['credits'] < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. Need {cost} credits.'
        )
    
    # Get site
    site = await db.sites.find_one(
        {'site_id': request.site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    )
    if not site:
        raise HTTPException(status_code=404, detail='Site not found')
    
    service = BacklinkStrategyService()
    result = await service.analyze_link_gap(
        site['url'],
        request.competitors
    )
    
    # Deduct credits
    await db.users.update_one(
        {'user_id': current_user['user_id']},
        {'$inc': {'credits': -cost}}
    )
    
    await db.credit_transactions.insert_one({
        'user_id': current_user['user_id'],
        'amount': -cost,
        'type': 'backlink_analysis',
        'description': f'Backlink analysis for {site["url"]}',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return result


@router.post('/backlinks/generate-outreach')
async def generate_outreach_email(
    request: OutreachEmailRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate outreach email"""
    db = await get_database()
    
    # Check credits
    cost = CREDIT_COSTS['outreach_email']
    if current_user['credits'] < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. Need {cost} credits.'
        )
    
    # Get site
    site = await db.sites.find_one(
        {'site_id': request.site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    )
    if not site:
        raise HTTPException(status_code=404, detail='Site not found')
    
    your_info = {
        'name': site.get('name', 'Company'),
        'url': site['url']
    }
    
    service = BacklinkStrategyService()
    result = await service.generate_outreach_email(
        request.opportunity,
        your_info
    )
    
    # Deduct credits
    await db.users.update_one(
        {'user_id': current_user['user_id']},
        {'$inc': {'credits': -cost}}
    )
    
    await db.credit_transactions.insert_one({
        'user_id': current_user['user_id']},
        'amount': -cost,
        'type': 'outreach_email',
        'description': 'Outreach email generated',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return result


# Learning Center Endpoints
@router.get('/learning/knowledge-base')
async def get_knowledge_base(current_user: dict = Depends(get_current_user)):
    """Get knowledge base articles"""
    service = LearningCenterService()
    return service.get_knowledge_base()


@router.get('/learning/tutorials')
async def get_tutorials(current_user: dict = Depends(get_current_user)):
    """Get tutorials"""
    service = LearningCenterService()
    return service.get_tutorials()


@router.get('/learning/faq')
async def get_faq(current_user: dict = Depends(get_current_user)):
    """Get FAQ"""
    service = LearningCenterService()
    return service.get_faq()


@router.post('/learning/ai-assistant')
async def ask_ai_assistant(
    request: AIAssistantRequest,
    current_user: dict = Depends(get_current_user)
):
    """Ask AI assistant"""
    service = LearningCenterService()
    result = await service.ai_assistant(
        request.question,
        request.context
    )
    return result
