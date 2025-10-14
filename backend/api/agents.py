from fastapi import APIRouter, Depends, HTTPException, status
from schemas.schemas import AgentCreate, Agent, ChatRequest, ChatResponse
from core.dependencies import get_current_user
from core.database import get_database
from services.ai_agents import AgentFactory
from services.billing import CREDIT_COSTS
from datetime import datetime, timezone
import uuid
from typing import List

router = APIRouter(prefix='/agents', tags=['AI Agents'])

# Store active agents in memory (in production, use Redis)
active_agents = {}

@router.post('/', response_model=Agent)
async def create_agent(agent_data: AgentCreate, current_user: dict = Depends(get_current_user)):
    """Create a new AI agent with optional website-specific context"""
    db = await get_database()
    
    agent_id = str(uuid.uuid4())
    site_id = None
    
    # If website is provided, find the matching site
    if agent_data.website:
        site = await db.sites.find_one({
            'user_id': current_user['user_id'],
            'url': {'$regex': agent_data.website, '$options': 'i'}
        }, {'_id': 0})
        
        if not site:
            # Try to find by partial match
            site = await db.sites.find_one({
                'user_id': current_user['user_id']
            }, {'_id': 0})
        
        if site:
            site_id = site['site_id']
    
    agent_doc = {
        'agent_id': agent_id,
        'user_id': current_user['user_id'],
        'name': agent_data.name,
        'purpose': agent_data.purpose,
        'website': agent_data.website,
        'site_id': site_id,
        'context': agent_data.context or {},
        'active': True,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.agents.insert_one(agent_doc)
    
    # Initialize agent instance with context
    initial_context = agent_data.context or {}
    if site_id and agent_data.website:
        initial_context['website_url'] = agent_data.website
        initial_context['site_id'] = site_id
    
    agent_instance = AgentFactory.create_agent(
        agent_data.purpose,
        agent_data.name,
        initial_context
    )
    active_agents[agent_id] = agent_instance
    
    return Agent(**agent_doc)

@router.get('/', response_model=List[Agent])
async def get_agents(current_user: dict = Depends(get_current_user)):
    """Get all agents for current user"""
    db = await get_database()
    
    agents = await db.agents.find(
        {'user_id': current_user['user_id']},
        {'_id': 0}
    ).to_list(50)
    
    return [Agent(**agent) for agent in agents]

@router.post('/chat', response_model=ChatResponse)
async def chat_with_agent(chat_data: ChatRequest, current_user: dict = Depends(get_current_user)):
    """Chat with an AI agent with comprehensive context"""
    db = await get_database()
    
    # Check credits
    if current_user['credits'] < CREDIT_COSTS['ai_agent_chat']:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail='Insufficient credits'
        )
    
    # Get agent
    agent_doc = await db.agents.find_one({
        'agent_id': chat_data.agent_id,
        'user_id': current_user['user_id']
    })
    
    if not agent_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Agent not found'
        )
    
    # Build comprehensive context based on agent type
    context = agent_doc.get('context', {})
    site_id = agent_doc.get('site_id')
    
    # Load website-specific context for LLM Visibility Agent
    if agent_doc['purpose'] == 'llm_visibility_optimizer' and site_id:
        # Get site info
        site = await db.sites.find_one(
            {'site_id': site_id, 'user_id': current_user['user_id']},
            {'_id': 0}
        )
        
        if site:
            context['website_url'] = site.get('url')
            context['site_id'] = site_id
            
            # Get latest audit
            latest_audit = await db.audits.find_one(
                {'site_id': site_id, 'user_id': current_user['user_id']},
                {'_id': 0},
                sort=[('created_at', -1)]
            )
            if latest_audit:
                context['latest_audit'] = {
                    'seo_score': latest_audit.get('seo_score'),
                    'technical_score': latest_audit.get('technical_score'),
                    'onpage_score': latest_audit.get('onpage_score'),
                    'offpage_score': latest_audit.get('offpage_score'),
                    'issues': latest_audit.get('issues', [])
                }
            
            # Get latest LLM visibility check
            visibility_check = await db.llm_visibility_checks.find_one(
                {'site_id': site_id, 'user_id': current_user['user_id']},
                {'_id': 0},
                sort=[('created_at', -1)]
            )
            if visibility_check:
                context['llm_visibility'] = {
                    'overall_score': visibility_check.get('overall_score'),
                    'visibility_by_llm': visibility_check.get('visibility_by_llm', {}),
                    'recommendations': visibility_check.get('recommendations', [])
                }
            
            # Get latest recommendations
            recommendations = await db.recommendations.find_one(
                {'site_id': site_id, 'user_id': current_user['user_id']},
                {'_id': 0},
                sort=[('created_at', -1)]
            )
            if recommendations:
                context['recommendations'] = {
                    'total_recommendations': recommendations.get('total_recommendations', 0),
                    'high_priority': recommendations.get('high_priority', []),
                    'quick_wins': recommendations.get('quick_wins', [])
                }
            
            # Get latest content gap analysis
            content_gaps = await db.content_gap_analyses.find_one(
                {'site_id': site_id, 'user_id': current_user['user_id']},
                {'_id': 0},
                sort=[('created_at', -1)]
            )
            if content_gaps:
                context['content_gaps'] = {
                    'gaps': content_gaps.get('gaps', []),
                    'opportunities': content_gaps.get('opportunities', [])
                }
            
            # Get latest community opportunities
            community = await db.community_opportunities.find_one(
                {'site_id': site_id, 'user_id': current_user['user_id']},
                {'_id': 0},
                sort=[('created_at', -1)]
            )
            if community:
                context['community_opportunities'] = {
                    'total_opportunities': community.get('total_opportunities', 0),
                    'opportunities': community.get('opportunities', [])[:5]  # Top 5
                }
            
            # Get latest backlink analysis
            backlinks = await db.backlink_analyses.find_one(
                {'site_id': site_id, 'user_id': current_user['user_id']},
                {'_id': 0},
                sort=[('created_at', -1)]
            )
            if backlinks:
                context['backlink_analysis'] = {
                    'total_opportunities': backlinks.get('total_opportunities', 0),
                    'opportunities': backlinks.get('opportunities', [])[:5]
                }
            
            # Count total audits for this website
            total_audits = await db.audits.count_documents({
                'site_id': site_id,
                'user_id': current_user['user_id']
            })
            context['total_audits'] = total_audits
    
    # Legacy support for audit_assistant
    elif agent_doc['purpose'] == 'audit_assistant':
        # Get user's sites
        sites = await db.sites.find({'user_id': current_user['user_id']}, {'_id': 0}).to_list(10)
        
        if sites:
            # Use site_id if available, otherwise use first site
            target_site_id = site_id or sites[0]['site_id']
            
            # Get latest audit
            latest_audit = await db.audits.find_one(
                {'user_id': current_user['user_id'], 'site_id': target_site_id},
                {'_id': 0},
                sort=[('created_at', -1)]
            )
            
            if latest_audit:
                # Update agent context with real data
                context = {
                    'latest_audit': {
                        'seo_score': latest_audit.get('seo_score'),
                        'technical_score': latest_audit.get('technical_score'),
                        'onpage_score': latest_audit.get('onpage_score'),
                        'offpage_score': latest_audit.get('offpage_score'),
                        'issues': latest_audit.get('issues', [])
                    },
                    'crawl_data': latest_audit.get('crawl_data', {}),
                    'site_url': [s for s in sites if s['site_id'] == target_site_id][0].get('url')
                }
    
    # Get or create agent instance
    if chat_data.agent_id not in active_agents:
        agent_instance = AgentFactory.create_agent(
            agent_doc['purpose'],
            agent_doc['name'],
            context
        )
        active_agents[chat_data.agent_id] = agent_instance
    else:
        agent_instance = active_agents[chat_data.agent_id]
        # Update context with latest data
        agent_instance.context = context
    
    # Process message
    response = await agent_instance.process_message(chat_data.message)
    
    # Save chat session
    await db.chat_sessions.insert_one({
        'agent_id': chat_data.agent_id,
        'user_id': current_user['user_id'],
        'site_id': site_id,
        'user_message': chat_data.message,
        'agent_response': response['response'],
        'suggestions': response.get('suggestions', []),
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    # Deduct credits
    await db.users.update_one(
        {'user_id': current_user['user_id']},
        {'$inc': {'credits': -CREDIT_COSTS['ai_agent_chat']}}
    )
    
    # Log transaction
    await db.credit_transactions.insert_one({
        'user_id': current_user['user_id'],
        'amount': -CREDIT_COSTS['ai_agent_chat'],
        'type': 'ai_agent_chat',
        'description': f'Chat with {agent_doc["name"]}',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    
    return ChatResponse(
        agent_id=chat_data.agent_id,
        message=response['response'],
        suggestions=response.get('suggestions')
    )

@router.get('/{agent_id}/history')
async def get_agent_history(agent_id: str, limit: int = 50, current_user: dict = Depends(get_current_user)):
    """Get chat history for an agent"""
    db = await get_database()
    
    history = await db.chat_sessions.find(
        {'agent_id': agent_id, 'user_id': current_user['user_id']},
        {'_id': 0}
    ).sort('timestamp', -1).limit(limit).to_list(limit)
    
    return {'history': list(reversed(history))}

@router.delete('/{agent_id}')
async def delete_agent(agent_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an agent"""
    db = await get_database()
    
    result = await db.agents.delete_one({'agent_id': agent_id, 'user_id': current_user['user_id']})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Agent not found'
        )
    
    # Remove from active agents
    if agent_id in active_agents:
        del active_agents[agent_id]
    
    return {'message': 'Agent deleted successfully'}
