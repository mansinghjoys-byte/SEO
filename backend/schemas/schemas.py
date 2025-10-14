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
    purpose: str  # audit_assistant, keyword_researcher, content_optimizer, llm_visibility_optimizer
    website: Optional[str] = None  # Specific website URL for website-specific agents
    context: Optional[Dict[str, Any]] = None

class Agent(BaseModel):
    model_config = ConfigDict(extra='ignore')
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    purpose: str
    website: Optional[str] = None
    site_id: Optional[str] = None  # Linked site ID for context retrieval
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

# Admin Schemas
class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class SEOSettings(BaseModel):
    model_config = ConfigDict(extra='ignore')
    setting_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "RankForge - AI-Powered SEO Platform"
    description: str = "Advanced AI-powered SEO analysis and optimization platform"
    keywords: List[str] = ["SEO", "AI", "website optimization", "search engine"]
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    twitter_card: str = "summary_large_image"
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    canonical_url: str = "https://rankforge.com"
    json_ld: Dict[str, Any] = {}
    robots: str = "index, follow"
    updated_at: datetime = Field(default_factory=lambda: datetime.now())

class SEOSettingsUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    twitter_card: Optional[str] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    canonical_url: Optional[str] = None
    json_ld: Optional[Dict[str, Any]] = None
    robots: Optional[str] = None

class PricingPlan(BaseModel):
    model_config = ConfigDict(extra='ignore')
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    price: float
    credits: int
    features: List[str]
    max_sites: int
    max_keywords: int
    audit_frequency: str  # monthly, weekly, daily
    ai_agents: bool = False
    priority_support: bool = False
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())

class PricingPlanCreate(BaseModel):
    name: str
    price: float
    credits: int
    features: List[str]
    max_sites: int
    max_keywords: int
    audit_frequency: str
    ai_agents: bool = False
    priority_support: bool = False

class PricingPlanUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    credits: Optional[int] = None
    features: Optional[List[str]] = None
    max_sites: Optional[int] = None
    max_keywords: Optional[int] = None
    audit_frequency: Optional[str] = None
    ai_agents: Optional[bool] = None
    priority_support: Optional[bool] = None
    active: Optional[bool] = None

class UserManagement(BaseModel):
    user_id: str
    email: str
    full_name: str
    credits: int
    plan: str
    created_at: datetime
    total_sites: int = 0
    total_audits: int = 0
    last_login: Optional[datetime] = None

class UserCreditsUpdate(BaseModel):
    credits: int
    action: str  # add, subtract, set

class SystemStats(BaseModel):
    total_users: int
    total_sites: int
    total_audits: int
    total_keywords: int
    active_agents: int
    credits_consumed: int
    revenue: float
    new_users_today: int
    audits_today: int
