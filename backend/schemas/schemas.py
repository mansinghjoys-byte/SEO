from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# User Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra='ignore')
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    credits: int = 20
    plan: str = 'free'
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    credits: int
    plan: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: UserResponse

# Site Schemas
class SiteCreate(BaseModel):
    url: str
    name: Optional[str] = None

class Site(BaseModel):
    model_config = ConfigDict(extra='ignore')
    site_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    url: str
    name: Optional[str] = None
    last_audit: Optional[datetime] = None
    seo_score: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())

# Audit Schemas
class AuditCreate(BaseModel):
    site_id: str

class AuditIssue(BaseModel):
    category: str
    severity: str  # critical, high, medium, low
    title: str
    description: str
    fix: str
    impact_score: int

class AuditResult(BaseModel):
    model_config = ConfigDict(extra='ignore')
    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    site_id: str
    user_id: str
    seo_score: int
    technical_score: int
    onpage_score: int
    offpage_score: int
    issues: List[AuditIssue] = []
    recommendations: List[str] = []
    status: str = 'completed'
    created_at: datetime = Field(default_factory=lambda: datetime.now())

# Keyword Schemas
class KeywordCreate(BaseModel):
    site_id: str
    keyword: str
    target_url: Optional[str] = None

class Keyword(BaseModel):
    model_config = ConfigDict(extra='ignore')
    keyword_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    site_id: str
    user_id: str
    keyword: str
    target_url: Optional[str] = None
    search_volume: Optional[int] = None
    difficulty: Optional[int] = None
    current_rank: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())

# AI Agent Schemas
class AgentCreate(BaseModel):
    name: str
    purpose: str  # audit_assistant, keyword_researcher, content_optimizer
    context: Optional[Dict[str, Any]] = None

class Agent(BaseModel):
    model_config = ConfigDict(extra='ignore')
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    purpose: str
    context: Dict[str, Any] = {}
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class ChatMessage(BaseModel):
    role: str  # user or assistant
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now())

class ChatRequest(BaseModel):
    agent_id: str
    message: str

class ChatResponse(BaseModel):
    agent_id: str
    message: str
    suggestions: Optional[List[str]] = None

# Billing Schemas
class PlanUpgrade(BaseModel):
    plan: str  # starter, growth, professional, agency, enterprise

class CreditPurchase(BaseModel):
    credits: int
    payment_method: str = 'paypal'

class PayPalOrder(BaseModel):
    order_id: str
    status: str
    amount: float

# Competitor Schemas
class CompetitorCreate(BaseModel):
    site_id: str
    competitor_url: str

class Competitor(BaseModel):
    model_config = ConfigDict(extra='ignore')
    competitor_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    site_id: str
    user_id: str
    competitor_url: str
    domain_authority: Optional[int] = None
    backlinks: Optional[int] = None
    ranking_keywords: Optional[int] = None
    last_analyzed: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())

# Content Optimization Schemas
class ContentOptimizeRequest(BaseModel):
    content: str
    target_keyword: str
    url: Optional[str] = None

class ContentOptimizationResult(BaseModel):
    score: int
    keyword_density: float
    readability_score: int
    suggestions: List[str]
    optimized_title: str
    optimized_meta: str
    optimized_content: str
