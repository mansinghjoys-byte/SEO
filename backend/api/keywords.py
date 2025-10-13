from fastapi import APIRouter, Depends, HTTPException, status
from schemas.schemas import KeywordCreate, Keyword
from core.dependencies import get_current_user
from core.database import get_database
from services.keyword_service import KeywordService
from services.billing import CREDIT_COSTS
from datetime import datetime, timezone
import uuid
from typing import List

router = APIRouter(prefix='/keywords', tags=['Keywords'])

@router.post('/research')
async def research_keywords(seed_keyword: str, current_user: dict = Depends(get_current_user)):
    """Research keywords"""
    db = await get_database()
    
    # Check credits
    if current_user['credits'] < CREDIT_COSTS['keyword_research']:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail='Insufficient credits'
        )
    
    # Research keywords
    keyword_service = KeywordService()
    results = await keyword_service.research_keywords(seed_keyword)
    
    # Deduct credits
    await db.users.update_one(
        {'user_id': current_user['user_id']},
        {'$inc': {'credits': -CREDIT_COSTS['keyword_research']}}
    )
    
    # Log transaction
    await db.credit_transactions.insert_one({
        'user_id': current_user['user_id'],
        'amount': -CREDIT_COSTS['keyword_research'],
        'type': 'keyword_research',
        'description': f'Keyword research for: {seed_keyword}',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return {'keywords': results}

@router.post('/', response_model=Keyword)
async def track_keyword(keyword_data: KeywordCreate, current_user: dict = Depends(get_current_user)):
    """Add keyword to track"""
    db = await get_database()
    
    # Verify site ownership
    site = await db.sites.find_one({'site_id': keyword_data.site_id, 'user_id': current_user['user_id']})
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Site not found'
        )
    
    keyword_id = str(uuid.uuid4())
    keyword_doc = {
        'keyword_id': keyword_id,
        'site_id': keyword_data.site_id,
        'user_id': current_user['user_id'],
        'keyword': keyword_data.keyword,
        'target_url': keyword_data.target_url,
        'search_volume': None,
        'difficulty': None,
        'current_rank': None,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.keywords.insert_one(keyword_doc)
    
    return Keyword(**keyword_doc)

@router.get('/site/{site_id}', response_model=List[Keyword])
async def get_site_keywords(site_id: str, current_user: dict = Depends(get_current_user)):
    """Get all keywords for a site"""
    db = await get_database()
    
    keywords = await db.keywords.find(
        {'site_id': site_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    ).to_list(500)
    
    return [Keyword(**kw) for kw in keywords]

@router.delete('/{keyword_id}')
async def delete_keyword(keyword_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a tracked keyword"""
    db = await get_database()
    
    result = await db.keywords.delete_one({'keyword_id': keyword_id, 'user_id': current_user['user_id']})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Keyword not found'
        )
    
    return {'message': 'Keyword deleted successfully'}
