from fastapi import APIRouter, Depends, HTTPException, status
from schemas.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from core.security import hash_password, verify_password, create_access_token
from core.database import get_database
from core.config import get_settings
from core.dependencies import get_current_user
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix='/auth', tags=['Authentication'])
settings = get_settings()

@router.post('/register', response_model=TokenResponse)
async def register(user_data: UserRegister):
    """Register new user with free credits"""
    db = await get_database()
    
    # Check if user exists
    existing_user = await db.users.find_one({'email': user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already registered'
        )
    
    # Create user
    user_id = str(uuid.uuid4())
    user_doc = {
        'user_id': user_id,
        'email': user_data.email,
        'password': hash_password(user_data.password),
        'full_name': user_data.full_name,
        'credits': settings.FREE_SIGNUP_CREDITS,
        'plan': 'free',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    
    # Create access token
    token = create_access_token({'sub': user_id, 'email': user_data.email})
    
    # Log credit transaction
    await db.credit_transactions.insert_one({
        'user_id': user_id,
        'amount': settings.FREE_SIGNUP_CREDITS,
        'type': 'signup_bonus',
        'description': 'Welcome bonus credits',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            user_id=user_id,
            email=user_data.email,
            full_name=user_data.full_name,
            credits=settings.FREE_SIGNUP_CREDITS,
            plan='free'
        )
    )

@router.post('/login', response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user"""
    db = await get_database()
    
    # Find user
    user = await db.users.find_one({'email': credentials.email})
    if not user or not verify_password(credentials.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password'
        )
    
    # Create access token
    token = create_access_token({'sub': user['user_id'], 'email': user['email']})
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            user_id=user['user_id'],
            email=user['email'],
            full_name=user['full_name'],
            credits=user.get('credits', 0),
            plan=user.get('plan', 'free')
        )
    )

@router.get('/me', response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse(
        user_id=current_user['user_id'],
        email=current_user['email'],
        full_name=current_user['full_name'],
        credits=current_user.get('credits', 0),
        plan=current_user.get('plan', 'free')
    )
