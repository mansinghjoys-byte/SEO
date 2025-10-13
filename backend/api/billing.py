from fastapi import APIRouter, Depends, HTTPException, status
from schemas.schemas import PlanUpgrade, CreditPurchase, PayPalOrder
from core.dependencies import get_current_user
from core.database import get_database
from services.billing import PayPalService, PRICING_PLANS
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix='/billing', tags=['Billing'])

@router.get('/plans')
async def get_plans():
    """Get all pricing plans"""
    return {'plans': PRICING_PLANS}

@router.post('/upgrade')
async def upgrade_plan(upgrade_data: PlanUpgrade, current_user: dict = Depends(get_current_user)):
    """Upgrade to a paid plan"""
    db = await get_database()
    
    if upgrade_data.plan not in PRICING_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid plan'
        )
    
    plan_info = PRICING_PLANS[upgrade_data.plan]
    
    if plan_info['price'] == 0:
        # Free plan - direct upgrade
        await db.users.update_one(
            {'user_id': current_user['user_id']},
            {'$set': {'plan': upgrade_data.plan}}
        )
        return {'message': 'Plan updated successfully'}
    
    # For paid plans, create PayPal order
    paypal_service = PayPalService()
    order = await paypal_service.create_order(
        amount=plan_info['price'],
        description=f"{plan_info['name']} Plan - Monthly Subscription"
    )
    
    # Save pending subscription
    await db.subscriptions.insert_one({
        'user_id': current_user['user_id'],
        'plan': upgrade_data.plan,
        'order_id': order.get('id'),
        'status': 'pending',
        'amount': plan_info['price'],
        'created_at': datetime.now(timezone.utc).isoformat()
    })
    
    return {
        'order': order,
        'approve_url': next((link['href'] for link in order.get('links', []) if link['rel'] == 'approve'), None)
    }

@router.post('/paypal/capture')
async def capture_paypal_payment(order_data: PayPalOrder, current_user: dict = Depends(get_current_user)):
    """Capture PayPal payment after approval"""
    db = await get_database()
    
    paypal_service = PayPalService()
    result = await paypal_service.capture_order(order_data.order_id)
    
    if result.get('status') == 'COMPLETED':
        # Find subscription
        subscription = await db.subscriptions.find_one({'order_id': order_data.order_id})
        
        if subscription:
            # Update user plan and add credits
            plan_info = PRICING_PLANS[subscription['plan']]
            
            await db.users.update_one(
                {'user_id': current_user['user_id']},
                {
                    '$set': {'plan': subscription['plan']},
                    '$inc': {'credits': plan_info['credits_per_month']}
                }
            )
            
            # Update subscription status
            await db.subscriptions.update_one(
                {'order_id': order_data.order_id},
                {'$set': {'status': 'completed', 'completed_at': datetime.now(timezone.utc).isoformat()}}
            )
            
            # Log transaction
            await db.credit_transactions.insert_one({
                'user_id': current_user['user_id'],
                'amount': plan_info['credits_per_month'],
                'type': 'plan_purchase',
                'description': f"Purchased {plan_info['name']} plan",
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            return {'message': 'Payment successful', 'plan': subscription['plan']}
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Payment capture failed'
    )

@router.post('/credits/purchase')
async def purchase_credits(purchase_data: CreditPurchase, current_user: dict = Depends(get_current_user)):
    """Purchase additional credits"""
    db = await get_database()
    
    # $1 = 10 credits
    amount = purchase_data.credits / 10
    
    paypal_service = PayPalService()
    order = await paypal_service.create_order(
        amount=amount,
        description=f"Purchase {purchase_data.credits} SEO credits"
    )
    
    # Save pending credit purchase
    await db.credit_purchases.insert_one({
        'user_id': current_user['user_id'],
        'credits': purchase_data.credits,
        'order_id': order.get('id'),
        'status': 'pending',
        'amount': amount,
        'created_at': datetime.now(timezone.utc).isoformat()
    })
    
    return {
        'order': order,
        'approve_url': next((link['href'] for link in order.get('links', []) if link['rel'] == 'approve'), None)
    }

@router.get('/transactions')
async def get_transactions(limit: int = 50, current_user: dict = Depends(get_current_user)):
    """Get credit transaction history"""
    db = await get_database()
    
    transactions = await db.credit_transactions.find(
        {'user_id': current_user['user_id']},
        {'_id': 0}
    ).sort('timestamp', -1).limit(limit).to_list(limit)
    
    return {'transactions': transactions}
