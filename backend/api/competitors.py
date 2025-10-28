"""
Competitor Analysis API Endpoints
Production-ready endpoints for comprehensive competitor analysis
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from core.database import get_database
from core.dependencies import get_current_user
from services.billing import CREDIT_COSTS
from services.competitor_discovery import CompetitorDiscoveryService
from services.competitor_backlink_analysis import CompetitorBacklinkService
from services.competitor_content_analysis import CompetitorContentService
from services.competitor_social_analysis import CompetitorSocialService
from services.comprehensive_competitor_analyzer import ComprehensiveCompetitorAnalyzer
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/competitors', tags=['Competitor Analysis'])


# Request Models
class DiscoverCompetitorsRequest(BaseModel):
    site_id: str
    keywords: List[str]
    industry: Optional[str] = None
    max_competitors: int = 20


class AnalyzeCompetitorBacklinksRequest(BaseModel):
    site_id: str
    competitor_domain: str


class AnalyzeCompetitorContentRequest(BaseModel):
    site_id: str
    competitor_domain: str
    keywords: List[str]


class AnalyzeCompetitorSocialRequest(BaseModel):
    competitor_domain: str
    brand_name: Optional[str] = None


class ComprehensiveAnalysisRequest(BaseModel):
    site_id: str
    keywords: List[str]
    industry: Optional[str] = None
    analyze_top_n: int = 5


# Endpoint 1: Discover Competitors
@router.post('/discover')
async def discover_competitors(
    request: DiscoverCompetitorsRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Discover competitors using search engines, Exa.ai, and web scraping
    
    **Cost**: 10 credits
    **Methods**: Google search scraping, Exa.ai semantic search, similar content discovery
    """
    db = await get_database()
    
    # Verify site ownership
    site = await db.sites.find_one(
        {'site_id': request.site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    )
    if not site:
        raise HTTPException(status_code=404, detail='Site not found')
    
    # Check credits
    cost = CREDIT_COSTS.get('competitor_discovery', 10)
    if current_user['credits'] < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. Need {cost} credits.'
        )
    
    # Run discovery
    service = CompetitorDiscoveryService()
    result = await service.discover_competitors(
        site['url'],
        request.keywords,
        request.industry,
        request.max_competitors
    )
    
    if result.get('success'):
        # Save to database
        discovery_data = {
            'site_id': request.site_id,
            'user_id': current_user['user_id'],
            'keywords': request.keywords,
            'industry': request.industry,
            'competitors': result.get('competitors', []),
            'total_found': result.get('total_found', 0),
            'discovery_methods': result.get('discovery_methods_used', {}),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.competitor_discoveries.insert_one(discovery_data)
        
        # Deduct credits
        await db.users.update_one(
            {'user_id': current_user['user_id']},
            {'$inc': {'credits': -cost}}
        )
        
        await db.credit_transactions.insert_one({
            'user_id': current_user['user_id'],
            'amount': -cost,
            'type': 'competitor_discovery',
            'description': f'Competitor discovery for {site["url"]}',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    return result


# Endpoint 2: Analyze Competitor Backlinks
@router.post('/analyze-backlinks')
async def analyze_competitor_backlinks(
    request: AnalyzeCompetitorBacklinksRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze competitor's backlink profile and find link gap opportunities
    
    **Cost**: 15 credits
    **Methods**: Exa.ai backlink discovery, web scraping, mention analysis
    **Returns**: Backlinks, metrics, opportunities, AI insights
    """
    db = await get_database()
    
    # Verify site ownership
    site = await db.sites.find_one(
        {'site_id': request.site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    )
    if not site:
        raise HTTPException(status_code=404, detail='Site not found')
    
    # Check credits
    cost = CREDIT_COSTS.get('competitor_backlink_analysis', 15)
    if current_user['credits'] < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. Need {cost} credits.'
        )
    
    # Extract domain
    your_domain = site['url'].replace('https://', '').replace('http://', '').split('/')[0]
    
    # Run analysis
    service = CompetitorBacklinkService()
    result = await service.analyze_competitor_backlinks(
        request.competitor_domain,
        your_domain
    )
    
    if result.get('success'):
        # Save to database
        analysis_data = {
            'site_id': request.site_id,
            'user_id': current_user['user_id'],
            'competitor_domain': request.competitor_domain,
            'your_domain': your_domain,
            'metrics': result.get('metrics', {}),
            'total_backlinks': result.get('total_backlinks', 0),
            'backlinks': result.get('backlinks', []),
            'categorized': result.get('categorized', {}),
            'opportunities': result.get('link_gap_opportunities', []),
            'insights': result.get('insights', {}),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.competitor_backlink_analyses.insert_one(analysis_data)
        
        # Deduct credits
        await db.users.update_one(
            {'user_id': current_user['user_id']},
            {'$inc': {'credits': -cost}}
        )
        
        await db.credit_transactions.insert_one({
            'user_id': current_user['user_id'],
            'amount': -cost,
            'type': 'competitor_backlink_analysis',
            'description': f'Backlink analysis for competitor {request.competitor_domain}',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    return result


# Endpoint 3: Analyze Competitor Content
@router.post('/analyze-content')
async def analyze_competitor_content(
    request: AnalyzeCompetitorContentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze competitor's content strategy and identify content gaps
    
    **Cost**: 12 credits
    **Methods**: Exa.ai content discovery, sitemap scraping, page analysis
    **Returns**: Top content, themes, gaps, quality metrics, schema analysis, AI insights
    """
    db = await get_database()
    
    # Verify site ownership
    site = await db.sites.find_one(
        {'site_id': request.site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    )
    if not site:
        raise HTTPException(status_code=404, detail='Site not found')
    
    # Check credits
    cost = CREDIT_COSTS.get('competitor_content_analysis', 12)
    if current_user['credits'] < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. Need {cost} credits.'
        )
    
    # Extract domain
    your_domain = site['url'].replace('https://', '').replace('http://', '').split('/')[0]
    
    # Run analysis
    service = CompetitorContentService()
    result = await service.analyze_competitor_content(
        request.competitor_domain,
        your_domain,
        request.keywords
    )
    
    if result.get('success'):
        # Save to database
        analysis_data = {
            'site_id': request.site_id,
            'user_id': current_user['user_id'],
            'competitor_domain': request.competitor_domain,
            'your_domain': your_domain,
            'keywords': request.keywords,
            'top_content': result.get('top_content', []),
            'content_themes': result.get('content_themes', {}),
            'content_gaps': result.get('content_gaps', []),
            'quality_metrics': result.get('quality_metrics', {}),
            'schema_analysis': result.get('schema_analysis', {}),
            'insights': result.get('insights', {}),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.competitor_content_analyses.insert_one(analysis_data)
        
        # Deduct credits
        await db.users.update_one(
            {'user_id': current_user['user_id']},
            {'$inc': {'credits': -cost}}
        )
        
        await db.credit_transactions.insert_one({
            'user_id': current_user['user_id'],
            'amount': -cost,
            'type': 'competitor_content_analysis',
            'description': f'Content analysis for competitor {request.competitor_domain}',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    return result


# Endpoint 4: Analyze Competitor Social Media
@router.post('/analyze-social')
async def analyze_competitor_social(
    request: AnalyzeCompetitorSocialRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze competitor's social media presence (Reddit, Twitter/X, Quora)
    
    **Cost**: 8 credits
    **Methods**: Reddit API, Twitter API, Quora scraping
    **Returns**: Platform analysis, metrics, insights
    """
    db = await get_database()
    
    # Check credits
    cost = CREDIT_COSTS.get('competitor_social_analysis', 8)
    if current_user['credits'] < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. Need {cost} credits.'
        )
    
    # Run analysis
    service = CompetitorSocialService()
    result = await service.analyze_competitor_social_presence(
        request.competitor_domain,
        request.brand_name
    )
    
    if result.get('success'):
        # Save to database
        analysis_data = {
            'user_id': current_user['user_id'],
            'competitor_domain': request.competitor_domain,
            'brand_name': request.brand_name or result.get('brand_name'),
            'reddit_analysis': result.get('reddit_analysis', {}),
            'twitter_analysis': result.get('twitter_analysis', {}),
            'quora_analysis': result.get('quora_analysis', {}),
            'social_metrics': result.get('social_metrics', {}),
            'insights': result.get('insights', {}),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.competitor_social_analyses.insert_one(analysis_data)
        
        # Deduct credits
        await db.users.update_one(
            {'user_id': current_user['user_id']},
            {'$inc': {'credits': -cost}}
        )
        
        await db.credit_transactions.insert_one({
            'user_id': current_user['user_id'],
            'amount': -cost,
            'type': 'competitor_social_analysis',
            'description': f'Social media analysis for competitor {request.competitor_domain}',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    return result


# Endpoint 5: Comprehensive Competitor Report
@router.post('/comprehensive-report')
async def comprehensive_competitor_report(
    request: ComprehensiveAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Run comprehensive competitor analysis (discover + analyze all aspects)
    
    **Cost**: 50 credits
    **Includes**: 
    - Competitor discovery
    - Backlink analysis for top competitors
    - Content analysis for top competitors
    - Social media analysis for top competitors
    - Cross-competitor insights
    - Actionable recommendations
    - Competitive landscape assessment
    
    **This is the MOST COMPREHENSIVE analysis available**
    """
    db = await get_database()
    
    # Verify site ownership
    site = await db.sites.find_one(
        {'site_id': request.site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    )
    if not site:
        raise HTTPException(status_code=404, detail='Site not found')
    
    # Check credits
    cost = CREDIT_COSTS.get('comprehensive_competitor_analysis', 50)
    if current_user['credits'] < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. Need {cost} credits.'
        )
    
    # Run comprehensive analysis
    service = ComprehensiveCompetitorAnalyzer()
    result = await service.comprehensive_analysis(
        site['url'],
        request.keywords,
        request.industry,
        request.analyze_top_n
    )
    
    if result.get('success'):
        # Save comprehensive report to database
        report_data = {
            'site_id': request.site_id,
            'user_id': current_user['user_id'],
            'your_domain': result.get('your_domain'),
            'keywords': request.keywords,
            'industry': request.industry,
            'competitors_analyzed': result.get('competitors_analyzed', 0),
            'competitors': result.get('competitors', []),
            'cross_competitor_insights': result.get('cross_competitor_insights', {}),
            'competitive_landscape': result.get('competitive_landscape', {}),
            'actionable_recommendations': result.get('actionable_recommendations', []),
            'executive_summary': result.get('executive_summary', {}),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.comprehensive_competitor_reports.insert_one(report_data)
        
        # Deduct credits
        await db.users.update_one(
            {'user_id': current_user['user_id']},
            {'$inc': {'credits': -cost}}
        )
        
        await db.credit_transactions.insert_one({
            'user_id': current_user['user_id'],
            'amount': -cost,
            'type': 'comprehensive_competitor_analysis',
            'description': f'Comprehensive competitor analysis for {site["url"]}',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    return result


# Endpoint 6: Get Historical Reports
@router.get('/{site_id}/reports')
async def get_competitor_reports(
    site_id: str,
    report_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get historical competitor analysis reports
    
    **Query Parameters**:
    - report_type: 'discovery', 'backlinks', 'content', 'social', 'comprehensive', or 'all'
    """
    db = await get_database()
    
    # Verify site ownership
    site = await db.sites.find_one(
        {'site_id': site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    )
    if not site:
        raise HTTPException(status_code=404, detail='Site not found')
    
    reports = {}
    
    # Fetch reports based on type
    if not report_type or report_type == 'all' or report_type == 'discovery':
        discoveries = await db.competitor_discoveries.find(
            {'site_id': site_id, 'user_id': current_user['user_id']},
            {'_id': 0}
        ).sort('created_at', -1).limit(10).to_list(length=10)
        reports['discoveries'] = discoveries
    
    if not report_type or report_type == 'all' or report_type == 'backlinks':
        backlink_analyses = await db.competitor_backlink_analyses.find(
            {'site_id': site_id, 'user_id': current_user['user_id']},
            {'_id': 0}
        ).sort('created_at', -1).limit(10).to_list(length=10)
        reports['backlink_analyses'] = backlink_analyses
    
    if not report_type or report_type == 'all' or report_type == 'content':
        content_analyses = await db.competitor_content_analyses.find(
            {'site_id': site_id, 'user_id': current_user['user_id']},
            {'_id': 0}
        ).sort('created_at', -1).limit(10).to_list(length=10)
        reports['content_analyses'] = content_analyses
    
    if not report_type or report_type == 'all' or report_type == 'comprehensive':
        comprehensive = await db.comprehensive_competitor_reports.find(
            {'site_id': site_id, 'user_id': current_user['user_id']},
            {'_id': 0}
        ).sort('created_at', -1).limit(5).to_list(length=5)
        reports['comprehensive_reports'] = comprehensive
    
    return {
        'success': True,
        'site_id': site_id,
        'reports': reports
    }
