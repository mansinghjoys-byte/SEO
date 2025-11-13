from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from schemas.schemas import AuditCreate, AuditResult
from core.dependencies import get_current_user
from core.database import get_database
from services.billing import CREDIT_COSTS
from services.seo_audit import SEOAuditService
from services.advanced_crawler import AdvancedSEOCrawler
from services.comprehensive_seo_auditor import ComprehensiveSEOAuditor
from datetime import datetime, timezone
import uuid
from typing import List, Dict, Any

router = APIRouter(prefix='/audits', tags=['Audits'])

@router.post('/', response_model=AuditResult)
async def create_audit(audit_data: AuditCreate, current_user: dict = Depends(get_current_user)):
    """Run SEO audit on a site"""
    db = await get_database()
    
    # Check credits
    if current_user['credits'] < CREDIT_COSTS['site_audit']:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail='Insufficient credits'
        )
    
    # Get site
    site = await db.sites.find_one({'site_id': audit_data.site_id, 'user_id': current_user['user_id']}, {'_id': 0})
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Site not found'
        )
    
    # Run audit
    audit_service = SEOAuditService()
    result = await audit_service.run_audit(site['url'])
    
    # Save audit result
    audit_id = str(uuid.uuid4())
    audit_doc = {
        'audit_id': audit_id,
        'site_id': audit_data.site_id,
        'user_id': current_user['user_id'],
        'seo_score': result['seo_score'],
        'technical_score': result['technical_score'],
        'onpage_score': result['onpage_score'],
        'offpage_score': result['offpage_score'],
        'issues': [issue.dict() for issue in result['issues']],
        'recommendations': result['recommendations'],
        'crawl_data': result.get('crawl_data', {}),  # Store crawl data
        'status': 'completed',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.audits.insert_one(audit_doc)
    
    # Update site
    await db.sites.update_one(
        {'site_id': audit_data.site_id},
        {'$set': {'last_audit': datetime.now(timezone.utc).isoformat(), 'seo_score': result['seo_score']}}
    )
    
    # Deduct credits
    await db.users.update_one(
        {'user_id': current_user['user_id']},
        {'$inc': {'credits': -CREDIT_COSTS['site_audit']}}
    )
    
    # Log transaction
    await db.credit_transactions.insert_one({
        'user_id': current_user['user_id'],
        'amount': -CREDIT_COSTS['site_audit'],
        'type': 'site_audit',
        'description': f'SEO audit for {site["url"]}',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return AuditResult(**audit_doc)

@router.get('/site/{site_id}', response_model=List[AuditResult])
async def get_site_audits(site_id: str, current_user: dict = Depends(get_current_user)):
    """Get all audits for a site"""
    db = await get_database()
    
    audits = await db.audits.find(
        {'site_id': site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    ).sort('created_at', -1).to_list(50)
    
    return [AuditResult(**audit) for audit in audits]

@router.get('/{audit_id}', response_model=AuditResult)
async def get_audit(audit_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific audit"""
    db = await get_database()
    
    audit = await db.audits.find_one({'audit_id': audit_id, 'user_id': current_user['user_id']}, {'_id': 0})
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Audit not found'
        )
    
    return AuditResult(**audit)

@router.post('/deep-analysis/{site_id}')
async def deep_analysis(site_id: str, current_user: dict = Depends(get_current_user)):
    """
    Perform comprehensive AI-powered deep analysis
    Includes: content quality, backlinks, domain authority, competitors, recommendations
    """
    db = await get_database()
    
    # Check credits (costs more for deep analysis)
    deep_analysis_cost = 10  # 10 credits for deep analysis
    if current_user['credits'] < deep_analysis_cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail='Insufficient credits. Deep analysis requires 10 credits.'
        )
    
    # Get site
    site = await db.sites.find_one({'site_id': site_id, 'user_id': current_user['user_id']}, {'_id': 0})
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Site not found'
        )
    
    # Run deep analysis
    crawler = AdvancedSEOCrawler()
    analysis = await crawler.deep_analyze(site['url'])
    
    if not analysis.get('success'):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {analysis.get('error', 'Unknown error')}"
        )
    
    # Save deep analysis result
    analysis_id = str(uuid.uuid4())
    analysis_doc = {
        'analysis_id': analysis_id,
        'site_id': site_id,
        'user_id': current_user['user_id'],
        'url': site['url'],
        'analysis_type': 'deep',
        'results': analysis,
        'created_at': datetime.now(timezone.utc)
    }
    
    await db.deep_analyses.insert_one(analysis_doc)
    
    # Update site with latest analysis
    await db.sites.update_one(
        {'site_id': site_id},
        {'$set': {
            'last_deep_analysis': datetime.now(timezone.utc),
            'domain_authority': analysis.get('domain_authority', {}).get('domain_authority', 0)
        }}
    )
    
    # Deduct credits
    await db.users.update_one(
        {'user_id': current_user['user_id']},
        {'$inc': {'credits': -deep_analysis_cost}}
    )
    
    # Log transaction
    await db.credit_transactions.insert_one({
        'transaction_id': str(uuid.uuid4()),
        'user_id': current_user['user_id'],
        'amount': -deep_analysis_cost,
        'type': 'deep_analysis',
        'description': f'Deep SEO analysis for {site["url"]}',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {
        'analysis_id': analysis_id,
        'message': 'Deep analysis completed successfully',
        'credits_used': deep_analysis_cost,
        'results': analysis
    }

@router.get('/deep-analysis/{site_id}/latest')
async def get_latest_deep_analysis(site_id: str, current_user: dict = Depends(get_current_user)):
    """Get the latest deep analysis for a site"""
    db = await get_database()
    
    analysis = await db.deep_analyses.find_one(
        {'site_id': site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    , sort=[('created_at', -1)])
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No deep analysis found for this site'
        )
    
    return analysis



@router.post('/comprehensive/{site_id}')
async def comprehensive_audit(site_id: str, current_user: dict = Depends(get_current_user)):
    """
    Run COMPREHENSIVE Production-Ready SEO Audit (60+ checks)
    Matches SAPRO audit standard with detailed findings and explanations
    
    Covers:
    - Technical SEO (15+ checks)
    - Core Web Vitals & Performance (10+ checks)
    - On-Page SEO (20+ checks)
    - Website Content (5+ checks)
    - Social Media (3+ checks)
    - Off-Page SEO (8+ checks)
    - GEO & AEO (5+ checks)
    - Analytics & Reporting (4+ checks)
    
    Returns detailed findings with:
    - Issue title and examples
    - Importance explanation
    - Actionable solutions
    - Impact scores
    - Severity levels
    """
    db = await get_database()
    
    # Check credits (comprehensive audit costs more)
    comprehensive_cost = 15  # 15 credits for comprehensive audit
    if current_user['credits'] < comprehensive_cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f'Insufficient credits. Comprehensive audit requires {comprehensive_cost} credits.'
        )
    
    # Get site
    site = await db.sites.find_one({'site_id': site_id, 'user_id': current_user['user_id']}, {'_id': 0})
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Site not found'
        )
    
    # Run comprehensive audit
    auditor = ComprehensiveSEOAuditor()
    audit_result = await auditor.run_comprehensive_audit(site['url'])
    
    if not audit_result.get('success'):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comprehensive audit failed: {audit_result.get('error', 'Unknown error')}"
        )
    
    # Save comprehensive audit
    audit_id = str(uuid.uuid4())
    audit_doc = {
        'audit_id': audit_id,
        'audit_type': 'comprehensive',
        'site_id': site_id,
        'user_id': current_user['user_id'],
        'url': site['url'],
        
        # Scores
        'overall_score': audit_result['scores']['overall_score'],
        'category_scores': audit_result['scores']['category_scores'],
        'severity_counts': audit_result['scores']['severity_counts'],
        
        # Findings
        'total_issues': audit_result['summary']['total_issues'],
        'critical_issues': audit_result['summary']['critical_issues'],
        'important_issues': audit_result['summary']['important_issues'],
        'minor_issues': audit_result['summary']['minor_issues'],
        
        'findings': audit_result['findings'],
        'findings_by_category': audit_result['findings_by_category'],
        'findings_by_severity': audit_result['findings_by_severity'],
        
        # AI Insights
        'ai_insights': audit_result.get('ai_insights', {}),
        
        # Raw data
        'crawl_data': audit_result.get('crawl_data', {}),
        'report_metadata': audit_result.get('report_metadata', {}),
        
        'status': 'completed',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.comprehensive_audits.insert_one(audit_doc)
    
    # Update site with latest comprehensive audit
    await db.sites.update_one(
        {'site_id': site_id},
        {'$set': {
            'last_comprehensive_audit': datetime.now(timezone.utc).isoformat(),
            'comprehensive_score': audit_result['scores']['overall_score']
        }}
    )
    
    # Deduct credits
    await db.users.update_one(
        {'user_id': current_user['user_id']},
        {'$inc': {'credits': -comprehensive_cost}}
    )
    
    # Log transaction
    await db.credit_transactions.insert_one({
        'transaction_id': str(uuid.uuid4()),
        'user_id': current_user['user_id'],
        'amount': -comprehensive_cost,
        'type': 'comprehensive_audit',
        'description': f'Comprehensive SEO audit for {site["url"]}',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {
        'audit_id': audit_id,
        'message': 'Comprehensive audit completed successfully',
        'credits_used': comprehensive_cost,
        'summary': audit_result['summary'],
        'scores': audit_result['scores'],
        'findings_count': len(audit_result['findings']),
        'ai_insights': audit_result.get('ai_insights', {}),
        'full_results': audit_result
    }


@router.get('/comprehensive/{site_id}/latest')
async def get_latest_comprehensive_audit(site_id: str, current_user: dict = Depends(get_current_user)):
    """Get the latest comprehensive audit for a site"""
    db = await get_database()
    
    audit = await db.comprehensive_audits.find_one(
        {'site_id': site_id, 'user_id': current_user['user_id']},
        {'_id': 0},
        sort=[('created_at', -1)]
    )
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No comprehensive audit found for this site. Run a comprehensive audit first.'
        )
    
    return audit


@router.get('/comprehensive/history')
async def get_comprehensive_audit_history(current_user: dict = Depends(get_current_user)):
    """Get all comprehensive audits for the user"""
    db = await get_database()
    
    audits = await db.comprehensive_audits.find(
        {'user_id': current_user['user_id']},
        {'_id': 0},
        sort=[('created_at', -1)]
    ).to_list(100)
    
    return {
        'total_audits': len(audits),
        'audits': audits
    }
