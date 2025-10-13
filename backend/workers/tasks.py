from services.seo_audit import SEOAuditService
from services.keyword_service import KeywordService
from core.database import db
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def process_site_audit(site_id: str, user_id: str, url: str):
    """Background job for processing site audits"""
    logger.info(f'Starting audit for site {site_id}')
    
    try:
        audit_service = SEOAuditService()
        result = await audit_service.run_audit(url)
        
        audit_data = {
            'site_id': site_id,
            'user_id': user_id,
            'seo_score': result['seo_score'],
            'technical_score': result['technical_score'],
            'onpage_score': result['onpage_score'],
            'offpage_score': result['offpage_score'],
            'issues': [issue.dict() for issue in result['issues']],
            'recommendations': result['recommendations'],
            'status': 'completed',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        await db.audits.insert_one(audit_data)
        await db.sites.update_one(
            {'site_id': site_id},
            {'$set': {'last_audit': datetime.now(timezone.utc).isoformat(), 'seo_score': result['seo_score']}}
        )
        
        logger.info(f'Audit completed for site {site_id}')
        return audit_data
    except Exception as e:
        logger.error(f'Audit failed for site {site_id}: {str(e)}')
        raise

async def process_keyword_research(user_id: str, site_id: str, seed_keyword: str):
    """Background job for keyword research"""
    logger.info(f'Starting keyword research for: {seed_keyword}')
    
    try:
        keyword_service = KeywordService()
        results = await keyword_service.research_keywords(seed_keyword)
        
        # Store keywords in database
        for keyword_data in results:
            keyword_doc = {
                'user_id': user_id,
                'site_id': site_id,
                'keyword': keyword_data['keyword'],
                'search_volume': keyword_data['search_volume'],
                'difficulty': keyword_data['difficulty'],
                'intent': keyword_data['intent'],
                'opportunity_score': keyword_data['opportunity_score'],
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            await db.keywords.insert_one(keyword_doc)
        
        logger.info(f'Keyword research completed: {len(results)} keywords found')
        return results
    except Exception as e:
        logger.error(f'Keyword research failed: {str(e)}')
        raise
