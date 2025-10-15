"""
Background Tasks using RQ (Redis Queue)
Handles async processing for LLM visibility checks, audits, and maintenance tasks
"""
from redis import Redis
from rq import Queue
from core.config import get_settings
from core.database import get_database
import asyncio
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize Redis connection
redis_conn = Redis.from_url(settings.REDIS_URL)

# Create queues with different priorities
high_priority_queue = Queue('high', connection=redis_conn)
default_queue = Queue('default', connection=redis_conn)
low_priority_queue = Queue('low', connection=redis_conn)


# ==================== High Priority Tasks ====================

def run_llm_visibility_check(site_id: str, user_id: str, competitors: list = None):
    """
    Background task for LLM visibility check
    High priority - 8 credits
    """
    try:
        from services.llm_visibility_service import LLMVisibilityService
        
        async def _run():
            db = await get_database()
            
            # Get site info
            site = await db.sites.find_one(
                {'site_id': site_id, 'user_id': user_id},
                {'_id': 0}
            )
            
            if not site:
                return {'success': False, 'error': 'Site not found'}
            
            # Run visibility check
            service = LLMVisibilityService()
            domain = site['url'].replace('https://', '').replace('http://', '').split('/')[0]
            
            result = await service.check_visibility(
                domain=domain,
                competitors=competitors or []
            )
            
            # Save result to database
            if result.get('success'):
                result['site_id'] = site_id
                result['user_id'] = user_id
                result['created_at'] = datetime.now(timezone.utc).isoformat()
                await db.llm_visibility_checks.insert_one(result)
            
            return result
        
        return asyncio.run(_run())
        
    except Exception as e:
        logger.error(f"LLM visibility check error: {str(e)}")
        return {'success': False, 'error': str(e)}


def run_content_gap_analysis(site_id: str, user_id: str, competitors: list = None):
    """
    Background task for content gap analysis
    High priority - 6 credits
    """
    try:
        from services.content_intelligence import ContentIntelligenceService
        
        async def _run():
            db = await get_database()
            
            site = await db.sites.find_one(
                {'site_id': site_id, 'user_id': user_id},
                {'_id': 0}
            )
            
            if not site:
                return {'success': False, 'error': 'Site not found'}
            
            service = ContentIntelligenceService()
            result = await service.analyze_content_gaps(
                site_data=site,
                competitor_urls=competitors or []
            )
            
            if result.get('success'):
                result['site_id'] = site_id
                result['user_id'] = user_id
                result['created_at'] = datetime.now(timezone.utc).isoformat()
                await db.content_gap_analyses.insert_one(result)
            
            return result
        
        return asyncio.run(_run())
        
    except Exception as e:
        logger.error(f"Content gap analysis error: {str(e)}")
        return {'success': False, 'error': str(e)}


# ==================== Default Priority Tasks ====================

def run_deep_analysis(site_id: str, user_id: str):
    """
    Background task for deep SEO analysis
    Default priority - 10 credits
    """
    try:
        from services.advanced_crawler import AdvancedSEOCrawler
        
        async def _run():
            db = await get_database()
            
            site = await db.sites.find_one(
                {'site_id': site_id, 'user_id': user_id},
                {'_id': 0}
            )
            
            if not site:
                return {'success': False, 'error': 'Site not found'}
            
            crawler = AdvancedSEOCrawler()
            result = await crawler.deep_analyze(site['url'])
            
            if result.get('success'):
                result['site_id'] = site_id
                result['user_id'] = user_id
                result['created_at'] = datetime.now(timezone.utc).isoformat()
                await db.deep_analyses.insert_one(result)
            
            return result
        
        return asyncio.run(_run())
        
    except Exception as e:
        logger.error(f"Deep analysis error: {str(e)}")
        return {'success': False, 'error': str(e)}


def run_backlink_analysis(site_id: str, user_id: str):
    """
    Background task for backlink analysis
    Default priority - 5 credits
    """
    try:
        from services.backlink_strategy import BacklinkStrategyService
        
        async def _run():
            db = await get_database()
            
            site = await db.sites.find_one(
                {'site_id': site_id, 'user_id': user_id},
                {'_id': 0}
            )
            
            if not site:
                return {'success': False, 'error': 'Site not found'}
            
            service = BacklinkStrategyService()
            result = await service.analyze_backlinks(
                site_data=site,
                competitor_urls=[]
            )
            
            if result.get('success'):
                result['site_id'] = site_id
                result['user_id'] = user_id
                result['created_at'] = datetime.now(timezone.utc).isoformat()
                await db.backlink_analyses.insert_one(result)
            
            return result
        
        return asyncio.run(_run())
        
    except Exception as e:
        logger.error(f"Backlink analysis error: {str(e)}")
        return {'success': False, 'error': str(e)}


def generate_recommendations(site_id: str, user_id: str):
    """
    Background task for generating recommendations
    Default priority - Free
    """
    try:
        from services.recommendation_engine import RecommendationEngine
        
        async def _run():
            db = await get_database()
            
            site = await db.sites.find_one(
                {'site_id': site_id, 'user_id': user_id},
                {'_id': 0}
            )
            
            if not site:
                return {'success': False, 'error': 'Site not found'}
            
            # Get latest data
            audit = await db.audits.find_one(
                {'site_id': site_id},
                {'_id': 0},
                sort=[('created_at', -1)]
            )
            
            visibility = await db.llm_visibility_checks.find_one(
                {'site_id': site_id},
                {'_id': 0},
                sort=[('created_at', -1)]
            )
            
            engine = RecommendationEngine()
            result = await engine.generate_recommendations(
                site_data=site,
                audit_data=audit,
                visibility_data=visibility
            )
            
            if result.get('success'):
                import uuid
                rec_id = str(uuid.uuid4())
                rec_doc = {
                    'recommendation_id': rec_id,
                    'site_id': site_id,
                    'user_id': user_id,
                    **result,
                    'created_at': datetime.now(timezone.utc).isoformat()
                }
                await db.recommendations.insert_one(rec_doc)
            
            return result
        
        return asyncio.run(_run())
        
    except Exception as e:
        logger.error(f"Recommendations generation error: {str(e)}")
        return {'success': False, 'error': str(e)}


# ==================== Low Priority Tasks ====================

def cleanup_old_data(days: int = 30):
    """
    Background task for cleaning up old data
    Low priority - maintenance task
    """
    try:
        async def _run():
            db = await get_database()
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Clean up old chat sessions (keep last 30 days)
            result = await db.chat_sessions.delete_many({
                'timestamp': {'$lt': cutoff_date.isoformat()}
            })
            
            logger.info(f"Cleaned up {result.deleted_count} old chat sessions")
            
            return {
                'success': True,
                'chat_sessions_deleted': result.deleted_count,
                'cutoff_date': cutoff_date.isoformat()
            }
        
        return asyncio.run(_run())
        
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        return {'success': False, 'error': str(e)}


def send_weekly_report(user_id: str):
    """
    Background task for sending weekly reports
    Low priority - scheduled task
    """
    try:
        async def _run():
            db = await get_database()
            
            # Get user
            user = await db.users.find_one(
                {'user_id': user_id},
                {'_id': 0}
            )
            
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Get user's sites
            sites = await db.sites.find(
                {'user_id': user_id},
                {'_id': 0}
            ).to_list(10)
            
            # Generate report (placeholder - implement email sending)
            report = {
                'user_email': user['email'],
                'total_sites': len(sites),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Weekly report generated for user {user_id}")
            
            return {'success': True, 'report': report}
        
        return asyncio.run(_run())
        
    except Exception as e:
        logger.error(f"Weekly report error: {str(e)}")
        return {'success': False, 'error': str(e)}


# ==================== Helper Functions ====================

def enqueue_visibility_check(site_id: str, user_id: str, competitors: list = None):
    """Enqueue LLM visibility check (high priority)"""
    job = high_priority_queue.enqueue(
        run_llm_visibility_check,
        site_id,
        user_id,
        competitors,
        job_timeout='10m',
        result_ttl=3600  # Keep result for 1 hour
    )
    logger.info(f"Enqueued visibility check job: {job.id} for site {site_id}")
    return job.id


def enqueue_content_gap_analysis(site_id: str, user_id: str, competitors: list = None):
    """Enqueue content gap analysis (high priority)"""
    job = high_priority_queue.enqueue(
        run_content_gap_analysis,
        site_id,
        user_id,
        competitors,
        job_timeout='10m',
        result_ttl=3600
    )
    logger.info(f"Enqueued content gap analysis job: {job.id} for site {site_id}")
    return job.id


def enqueue_deep_analysis(site_id: str, user_id: str):
    """Enqueue deep analysis (default priority)"""
    job = default_queue.enqueue(
        run_deep_analysis,
        site_id,
        user_id,
        job_timeout='15m',
        result_ttl=3600
    )
    logger.info(f"Enqueued deep analysis job: {job.id} for site {site_id}")
    return job.id


def enqueue_backlink_analysis(site_id: str, user_id: str):
    """Enqueue backlink analysis (default priority)"""
    job = default_queue.enqueue(
        run_backlink_analysis,
        site_id,
        user_id,
        job_timeout='10m',
        result_ttl=3600
    )
    logger.info(f"Enqueued backlink analysis job: {job.id} for site {site_id}")
    return job.id


def enqueue_recommendations(site_id: str, user_id: str):
    """Enqueue recommendations generation (default priority)"""
    job = default_queue.enqueue(
        generate_recommendations,
        site_id,
        user_id,
        job_timeout='10m',
        result_ttl=3600
    )
    logger.info(f"Enqueued recommendations job: {job.id} for site {site_id}")
    return job.id


def enqueue_cleanup(days: int = 30):
    """Enqueue cleanup (low priority)"""
    job = low_priority_queue.enqueue(
        cleanup_old_data,
        days,
        job_timeout='30m',
        result_ttl=86400  # Keep result for 24 hours
    )
    logger.info(f"Enqueued cleanup job: {job.id}")
    return job.id


def enqueue_weekly_report(user_id: str):
    """Enqueue weekly report (low priority)"""
    job = low_priority_queue.enqueue(
        send_weekly_report,
        user_id,
        job_timeout='5m',
        result_ttl=86400
    )
    logger.info(f"Enqueued weekly report job: {job.id} for user {user_id}")
    return job.id


def get_job_status(job_id: str):
    """Get status of a job"""
    from rq.job import Job
    
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        return {
            'id': job.id,
            'status': job.get_status(),
            'result': job.result,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'ended_at': job.ended_at.isoformat() if job.ended_at else None,
            'exc_info': job.exc_info
        }
    except Exception as e:
        return {'error': str(e)}


def get_queue_stats():
    """Get statistics for all queues"""
    return {
        'high': {
            'count': len(high_priority_queue),
            'name': 'high'
        },
        'default': {
            'count': len(default_queue),
            'name': 'default'
        },
        'low': {
            'count': len(low_priority_queue),
            'name': 'low'
        }
    }
