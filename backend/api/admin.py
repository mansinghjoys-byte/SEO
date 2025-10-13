from fastapi import APIRouter, Depends, HTTPException, status
from core.database import get_database
from core.dependencies import get_admin_user
from core.security import create_access_token, verify_password
from core.config import get_settings
from schemas.schemas import (
    AdminLogin, TokenResponse, UserResponse,
    SEOSettings, SEOSettingsUpdate,
    PricingPlan, PricingPlanCreate, PricingPlanUpdate,
    UserManagement, UserCreditsUpdate, SystemStats
)
from datetime import datetime
from typing import List

router = APIRouter(prefix='/admin', tags=['admin'])
settings = get_settings()

@router.post('/login')
async def admin_login(login_data: AdminLogin):
    """Admin login endpoint"""
    if login_data.email != settings.SUPER_ADMIN_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid admin credentials'
        )
    
    if login_data.password != settings.SUPER_ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid admin credentials'
        )
    
    # Create admin token with special flag
    token = create_access_token({
        'sub': 'admin',
        'email': settings.SUPER_ADMIN_EMAIL,
        'is_admin': True
    })
    
    return TokenResponse(
        access_token=token,
        token_type='bearer',
        user=UserResponse(
            user_id='admin',
            email=settings.SUPER_ADMIN_EMAIL,
            full_name='Super Administrator',
            credits=999999,
            plan='admin'
        )
    )

# ==================== SEO Settings Management ====================

@router.get('/seo-settings', response_model=SEOSettings)
async def get_seo_settings(
    admin=Depends(get_admin_user),
    db=Depends(get_database)
):
    """Get global SEO settings"""
    settings = await db.seo_settings.find_one({}, {'_id': 0})
    
    if not settings:
        # Create default settings
        default_settings = SEOSettings().model_dump()
        await db.seo_settings.insert_one(default_settings)
        return SEOSettings(**default_settings)
    
    return SEOSettings(**settings)

@router.put('/seo-settings', response_model=SEOSettings)
async def update_seo_settings(
    updates: SEOSettingsUpdate,
    admin=Depends(get_admin_user),
    db=Depends(get_database)
):
    """Update global SEO settings"""
    # Get current settings
    current = await db.seo_settings.find_one({}, {'_id': 0})
    
    if not current:
        # Create default if not exists
        current = SEOSettings().model_dump()
        await db.seo_settings.insert_one(current)
    
    # Update only provided fields
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    update_data['updated_at'] = datetime.now()
    
    await db.seo_settings.update_one(
        {'setting_id': current['setting_id']},
        {'$set': update_data}
    )
    
    updated = await db.seo_settings.find_one({'setting_id': current['setting_id']}, {'_id': 0})
    return SEOSettings(**updated)

# ==================== Pricing Plans Management ====================

@router.get('/plans', response_model=List[PricingPlan])
async def get_all_plans(
    admin=Depends(get_admin_user),
    db=Depends(get_database)
):
    """Get all pricing plans"""
    plans = await db.pricing_plans.find({}, {'_id': 0}).to_list(100)
    return [PricingPlan(**plan) for plan in plans]

@router.post('/plans', response_model=PricingPlan, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: PricingPlanCreate,
    admin=Depends(get_admin_user),
    db=Depends(get_database)
):
    """Create new pricing plan"""
    plan = PricingPlan(**plan_data.model_dump())
    await db.pricing_plans.insert_one(plan.model_dump())
    return plan

@router.get('/plans/{plan_id}', response_model=PricingPlan)
async def get_plan(
    plan_id: str,
    admin=Depends(get_admin_user),
    db=Depends(get_database)
):
    """Get specific plan"""
    plan = await db.pricing_plans.find_one({'plan_id': plan_id}, {'_id': 0})
    if not plan:
        raise HTTPException(status_code=404, detail='Plan not found')
    return PricingPlan(**plan)

@router.put('/plans/{plan_id}', response_model=PricingPlan)
async def update_plan(
    plan_id: str,
    updates: PricingPlanUpdate,
    admin=Depends(get_admin_user),
    db=Depends(get_database)
):
    """Update pricing plan"""
    plan = await db.pricing_plans.find_one({'plan_id': plan_id})
    if not plan:
        raise HTTPException(status_code=404, detail='Plan not found')
    
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    update_data['updated_at'] = datetime.now()
    
    await db.pricing_plans.update_one(
        {'plan_id': plan_id},
        {'$set': update_data}
    )
    
    updated = await db.pricing_plans.find_one({'plan_id': plan_id}, {'_id': 0})
    return PricingPlan(**updated)

@router.delete('/plans/{plan_id}')
async def delete_plan(
    plan_id: str,
    admin=Depends(get_admin_user),
    db=Depends(get_database)
):
    """Delete pricing plan"""
    result = await db.pricing_plans.delete_one({'plan_id': plan_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Plan not found')
    return {'message': 'Plan deleted successfully'}

# ==================== User Management ====================

@router.get('/users', response_model=List[UserManagement])
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    admin=Depends(get_admin_user),
    db=Depends(get_database)
):
    """Get all users with statistics"""
    users = await db.users.find({}, {'_id': 0, 'password': 0}).skip(skip).limit(limit).to_list(limit)
    
    user_list = []
    for user in users:
        # Get user stats
        sites_count = await db.sites.count_documents({'user_id': user['user_id']})
        audits_count = await db.audits.count_documents({'user_id': user['user_id']})
        
        user_list.append(UserManagement(
            user_id=user['user_id'],
            email=user['email'],
            full_name=user['full_name'],
            credits=user.get('credits', 0),
            plan=user.get('plan', 'free'),
            created_at=user.get('created_at', datetime.now()),
            total_sites=sites_count,
            total_audits=audits_count,
            last_login=user.get('last_login')
        ))
    
    return user_list

@router.get('/users/{user_id}', response_model=UserManagement)
async def get_user(
    user_id: str,
    admin=Depends(get_admin_user),
    db=Depends(get_database)
):
    """Get specific user details"""
    user = await db.users.find_one({'user_id': user_id}, {'_id': 0, 'password': 0})
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    sites_count = await db.sites.count_documents({'user_id': user_id})
    audits_count = await db.audits.count_documents({'user_id': user_id})
    
    return UserManagement(
        user_id=user['user_id'],
        email=user['email'],
        full_name=user['full_name'],
        credits=user.get('credits', 0),
        plan=user.get('plan', 'free'),
        created_at=user.get('created_at', datetime.now()),
        total_sites=sites_count,
        total_audits=audits_count,
        last_login=user.get('last_login')
    )

@router.put('/users/{user_id}/credits')
async def update_user_credits(
    user_id: str,
    credits_update: UserCreditsUpdate,
    admin=Depends(get_admin_user),
    db=Depends(get_database)
):
    """Update user credits"""
    user = await db.users.find_one({'user_id': user_id})
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    current_credits = user.get('credits', 0)
    
    if credits_update.action == 'add':
        new_credits = current_credits + credits_update.credits
    elif credits_update.action == 'subtract':
        new_credits = max(0, current_credits - credits_update.credits)
    elif credits_update.action == 'set':
        new_credits = credits_update.credits
    else:
        raise HTTPException(status_code=400, detail='Invalid action')
    
    await db.users.update_one(
        {'user_id': user_id},
        {'$set': {'credits': new_credits}}
    )
    
    return {'message': 'Credits updated successfully', 'new_credits': new_credits}

@router.put('/users/{user_id}/plan')
async def update_user_plan(
    user_id: str,
    plan: str,
    admin=Depends(get_admin_user),
    db=Depends(get_database)
):
    """Update user plan"""
    user = await db.users.find_one({'user_id': user_id})
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    await db.users.update_one(
        {'user_id': user_id},
        {'$set': {'plan': plan}}
    )
    
    return {'message': 'Plan updated successfully', 'new_plan': plan}

@router.delete('/users/{user_id}')
async def delete_user(
    user_id: str,
    admin=Depends(get_admin_user),
    db=Depends(get_database)
):
    """Delete user and all associated data"""
    user = await db.users.find_one({'user_id': user_id})
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    # Delete user and all related data
    await db.users.delete_one({'user_id': user_id})
    await db.sites.delete_many({'user_id': user_id})
    await db.audits.delete_many({'user_id': user_id})
    await db.keywords.delete_many({'user_id': user_id})
    await db.agents.delete_many({'user_id': user_id})
    await db.chat_sessions.delete_many({'user_id': user_id})
    await db.credit_transactions.delete_many({'user_id': user_id})
    
    return {'message': 'User and all associated data deleted successfully'}

# ==================== System Monitoring ====================

@router.get('/stats', response_model=SystemStats)
async def get_system_stats(
    admin=Depends(get_admin_user),
    db=Depends(get_database)
):
    """Get system-wide statistics"""
    from datetime import datetime, timedelta
    
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Count totals
    total_users = await db.users.count_documents({})
    total_sites = await db.sites.count_documents({})
    total_audits = await db.audits.count_documents({})
    total_keywords = await db.keywords.count_documents({})
    active_agents = await db.agents.count_documents({'active': True})
    
    # Today's stats
    new_users_today = await db.users.count_documents({
        'created_at': {'$gte': today_start}
    })
    audits_today = await db.audits.count_documents({
        'created_at': {'$gte': today_start}
    })
    
    # Calculate credits consumed (simulate from transactions)
    transactions = await db.credit_transactions.find({}).to_list(None)
    credits_consumed = sum(t.get('amount', 0) for t in transactions if t.get('type') == 'debit')
    
    # Calculate revenue (simulate)
    revenue = 0.0
    subscriptions = await db.subscriptions.find({}).to_list(None)
    for sub in subscriptions:
        revenue += sub.get('amount', 0)
    
    return SystemStats(
        total_users=total_users,
        total_sites=total_sites,
        total_audits=total_audits,
        total_keywords=total_keywords,
        active_agents=active_agents,
        credits_consumed=credits_consumed,
        revenue=revenue,
        new_users_today=new_users_today,
        audits_today=audits_today
    )

@router.get('/recent-activities')
async def get_recent_activities(
    limit: int = 20,
    admin=Depends(get_admin_user),
    db=Depends(get_database)
):
    """Get recent system activities"""
    from datetime import datetime, timedelta
    
    # Get recent audits
    recent_audits = await db.audits.find({}).sort('created_at', -1).limit(limit).to_list(limit)
    
    # Get recent users
    recent_users = await db.users.find({}, {'_id': 0, 'password': 0}).sort('created_at', -1).limit(limit).to_list(limit)
    
    # Get recent transactions
    recent_transactions = await db.credit_transactions.find({}).sort('created_at', -1).limit(limit).to_list(limit)
    
    return {
        'recent_audits': recent_audits,
        'recent_users': recent_users,
        'recent_transactions': recent_transactions
    }
