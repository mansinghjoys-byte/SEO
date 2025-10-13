from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from schemas.schemas import AuditCreate, AuditResult
from core.dependencies import get_current_user
from core.database import get_database
from services.billing import CREDIT_COSTS
from services.seo_audit import SEOAuditService
from services.advanced_crawler import AdvancedSEOCrawler
from datetime import datetime, timezone
import uuid
from typing import List

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
