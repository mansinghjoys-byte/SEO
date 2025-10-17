from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from schemas.schemas import SiteCreate, Site
from core.dependencies import get_current_user
from core.database import get_database, get_queue
from datetime import datetime, timezone
import uuid
from typing import List
from workers.tasks import process_site_audit

router = APIRouter(prefix='/sites', tags=['Sites'])

@router.post('/', response_model=Site)
async def create_site(site_data: SiteCreate, current_user: dict = Depends(get_current_user)):
    """Add a new site"""
    db = await get_database()
    
    # Check if site already exists for user
    existing = await db.sites.find_one({'user_id': current_user['user_id'], 'url': site_data.url})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Site already added'
        )
    
    site_id = str(uuid.uuid4())
    site_doc = {
        'site_id': site_id,
        'user_id': current_user['user_id'],
        'url': site_data.url,
        'name': site_data.name or site_data.url,
        'last_audit': None,
        'seo_score': None,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.sites.insert_one(site_doc)
    
    return Site(**site_doc)

@router.get('', response_model=List[Site])
@router.get('/', response_model=List[Site])
async def get_sites(current_user: dict = Depends(get_current_user)):
    """Get all sites for current user"""
    db = await get_database()
    sites = await db.sites.find({'user_id': current_user['user_id']}, {'_id': 0}).to_list(100)
    return [Site(**site) for site in sites]

@router.get('/{site_id}', response_model=Site)
async def get_site(site_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific site"""
    db = await get_database()
    site = await db.sites.find_one({'site_id': site_id, 'user_id': current_user['user_id']}, {'_id': 0})
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Site not found'
        )
    
    return Site(**site)

@router.delete('/{site_id}')
async def delete_site(site_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a site"""
    db = await get_database()
    
    result = await db.sites.delete_one({'site_id': site_id, 'user_id': current_user['user_id']})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Site not found'
        )
    
    return {'message': 'Site deleted successfully'}
