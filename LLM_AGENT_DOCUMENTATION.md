# 🚀 LLM Visibility Agent - Feature Documentation

## Overview

The **LLM Visibility Agent** is an AI-powered assistant that remembers website-specific context and helps users improve their SEO and LLM visibility. This agent is specifically designed for the RankForge platform and integrates deeply with all 8 core modules.

---

## Key Features

### 1. Website-Specific Context Memory
- **Persistent Context**: Agent remembers all audits, analyses, and recommendations for a specific website
- **Comprehensive Data Access**: Pulls data from:
  - Latest SEO audits
  - LLM visibility checks
  - Content gap analyses
  - Community opportunities
  - Backlink analyses
  - Generated recommendations
  - Historical audit count

### 2. Intelligent Recommendations
- **Context-Aware Suggestions**: Generates follow-up questions based on available data
- **Progress Tracking**: Can track improvements over time across multiple audits
- **Prioritization**: Suggests next steps based on what analyses have been run

### 3. Natural Conversation
- **Conversational History**: Maintains last 10 messages for context continuity
- **Follow-up Suggestions**: Provides 4 smart suggestions after each response
- **Data-Driven Responses**: All advice based on real website data

---

## API Endpoints

### Create Agent with Website
**POST** `/api/agents/`

**Request Body:**
```json
{
  "name": "My SEO Assistant",
  "purpose": "llm_visibility_optimizer",
  "website": "https://example.com",
  "context": {}  // Optional initial context
}
```

**Response:**
```json
{
  "agent_id": "uuid",
  "user_id": "uuid",
  "name": "My SEO Assistant",
  "purpose": "llm_visibility_optimizer",
  "website": "https://example.com",
  "site_id": "uuid",  // Automatically linked
  "context": {},
  "active": true,
  "created_at": "2025-10-14T..."
}
```

**Key Features:**
- Automatically matches website URL to user's sites
- Links agent to specific `site_id` for context retrieval
- Falls back to first available site if exact match not found

---

### Chat with Agent
**POST** `/api/agents/chat`

**Request Body:**
```json
{
  "agent_id": "uuid",
  "message": "What's my current LLM visibility score?"
}
```

**Response:**
```json
{
  "agent_id": "uuid",
  "message": "Your current LLM Visibility Score for https://example.com is 28.4/100...",
  "suggestions": [
    "📝 Analyze Content Gaps",
    "👥 Find Community Opportunities",
    "🔗 Analyze Backlink Strategy",
    "🚀 Quick wins to boost visibility"
  ]
}
```

**Context Loaded:**
- Latest SEO audit scores
- LLM visibility breakdown by AI (ChatGPT, Claude, Gemini, etc.)
- Top recommendations
- Content gaps
- Community opportunities
- Backlink opportunities
- Total audits performed

**Credit Cost:** 1 credit per chat message

---

### Get Agent Chat History
**GET** `/api/agents/{agent_id}/history?limit=50`

**Response:**
```json
{
  "history": [
    {
      "agent_id": "uuid",
      "user_id": "uuid",
      "site_id": "uuid",
      "user_message": "What's my score?",
      "agent_response": "Your LLM Visibility Score is...",
      "suggestions": ["...", "..."],
      "timestamp": "2025-10-14T..."
    }
  ]
}
```

---

### List All Agents
**GET** `/api/agents/`

Returns all agents for the current user with their website associations.

---

### Delete Agent
**DELETE** `/api/agents/{agent_id}`

Removes agent and clears from active memory.

---

## Agent Context Structure

When chatting with an LLM Visibility Agent, the following context is automatically loaded:

```python
{
  'website_url': 'https://example.com',
  'site_id': 'uuid',
  
  # Latest Audit Data
  'latest_audit': {
    'seo_score': 75,
    'technical_score': 80,
    'onpage_score': 70,
    'offpage_score': 65,
    'issues': [...]
  },
  
  # LLM Visibility Data
  'llm_visibility': {
    'overall_score': 28.4,
    'visibility_by_llm': {
      'ChatGPT': 32,
      'Claude': 28,
      'Gemini': 25,
      'Perplexity': 30,
      'Bing Chat': 27
    },
    'recommendations': [...]
  },
  
  # Generated Recommendations
  'recommendations': {
    'total_recommendations': 2,
    'high_priority': [...],
    'quick_wins': [...]
  },
  
  # Content Intelligence
  'content_gaps': {
    'gaps': [...],
    'opportunities': [...]
  },
  
  # Community Data
  'community_opportunities': {
    'total_opportunities': 8,
    'opportunities': [...]  // Top 5
  },
  
  # Backlink Data
  'backlink_analysis': {
    'total_opportunities': 6,
    'opportunities': [...]  // Top 5
  },
  
  # Historical Data
  'total_audits': 3
}
```

---

## Conversation Examples

### Example 1: Getting Started
**User:** "What's the current status of my website?"
**Agent:** "Your website https://example.com has an LLM Visibility Score of 28.4/100, which indicates significant room for improvement. Your SEO fundamentals are decent with a 75/100 score, but you're not being recommended by AI assistants yet. I've identified 2 high-priority actions..."

**Suggestions:**
- 📝 Analyze Content Gaps
- 👥 Find Community Opportunities
- 🔗 Analyze Backlink Strategy

---

### Example 2: Action Planning
**User:** "What should I do first?"
**Agent:** "Based on your data, here's what I recommend:

1. **Create Comprehensive Guide Content** (High Priority)
   - Expected Impact: +15 visibility points
   - Time: 6-8 hours
   - Why: LLMs frequently reference comprehensive guides...

2. **Optimize Meta Tags and Schema** (High Priority)
   - Expected Impact: +10 visibility points
   - Time: 2-3 hours
   - Why: Structured data helps LLMs understand..."

**Suggestions:**
- 🚀 Quick wins to boost visibility
- 📊 Show improvement progress

---

### Example 3: Progress Tracking
**User:** "How am I doing compared to last month?"
**Agent:** "You've made excellent progress! Looking at your 3 total audits:
- Audit 1: 28.4/100 visibility score
- Current: Still at baseline, but you've now identified key gaps

What's changed:
- ✅ Ran comprehensive visibility check
- ✅ Generated 2 prioritized recommendations
- ⏳ Ready to implement improvements

Next steps: Let's start with the quick wins I identified..."

---

## Smart Suggestions Logic

The agent generates context-aware suggestions based on what data is available:

| Data Available | Suggestion |
|----------------|------------|
| No LLM visibility check | 🤖 Run LLM Visibility Check |
| No recommendations | 💡 Generate Recommendations |
| No content gaps | 📝 Analyze Content Gaps |
| No community data | 👥 Find Community Opportunities |
| No backlink data | 🔗 Analyze Backlink Strategy |
| Score < 50 | 🚀 Quick wins to boost visibility |
| Score 50-75 | 📈 Medium-priority improvements |
| Score > 75 | 🎯 Advanced optimization tactics |
| Multiple audits | 📊 Show improvement progress |

---

## Agent Purposes

The system supports multiple agent types:

| Purpose | Description | Use Case |
|---------|-------------|----------|
| `llm_visibility_optimizer` | **NEW** - Website-specific LLM visibility expert | Improving AI discoverability |
| `audit_assistant` | SEO audit specialist | Understanding SEO issues |
| `keyword_researcher` | Keyword research expert | Finding profitable keywords |
| `content_optimizer` | Content optimization specialist | Improving content quality |
| `competitor_analyst` | Competitive analysis expert | Understanding competition |

---

## Integration with Other Modules

The LLM Visibility Agent seamlessly integrates with all 8 core modules:

### Module 1: Intelligent Website Crawler
- Accesses latest crawl data
- References technical scores

### Module 2: LLM Visibility Scorecard
- Shows per-LLM breakdown
- Tracks score improvements

### Module 3: Recommendation Engine
- Presents prioritized recommendations
- Explains impact and effort

### Module 4: Content Intelligence
- References content gaps
- Suggests outline improvements

### Module 5: Community Action Hub
- Highlights opportunities
- Recommends engagement strategies

### Module 6: Backlink Strategy
- Shows backlink opportunities
- Guides outreach efforts

### Module 7: Progress Tracking & Analytics
- Tracks historical performance
- Compares audit results

### Module 8: Learning Center
- Can reference knowledge base
- Provides educational content

---

## Production Deployment Checklist

### Backend ✅
- [x] Agent creation with website field
- [x] Website-to-site_id matching
- [x] Comprehensive context loading
- [x] LLMVisibilityAgent implementation
- [x] Chat history storage with site_id
- [x] Credit deduction per message
- [x] Error handling

### Database Schema
Collections used:
- `agents` - Agent definitions (includes `website` and `site_id`)
- `chat_sessions` - Conversation history (includes `site_id`)
- `sites` - User websites
- `audits` - SEO audit data
- `llm_visibility_checks` - Visibility data
- `recommendations` - Generated recommendations
- `content_gap_analyses` - Content gaps
- `community_opportunities` - Community data
- `backlink_analyses` - Backlink data

### Frontend (To Do)
- [ ] Agent creation UI with website selector
- [ ] Chat interface for agents
- [ ] Context visualization (show what data agent knows)
- [ ] Suggestion buttons for quick actions
- [ ] History view
- [ ] Agent management (list, delete)

---

## Testing Results

### Comprehensive Test: ✅ PASSED

```
✅ Login: PASSED
✅ Site retrieval: PASSED
✅ Context population: PASSED (LLM visibility + recommendations)
✅ Agent creation with website: PASSED
✅ Chat with context: PASSED (4 messages)
✅ Context persistence: PASSED
✅ Chat history: PASSED (4 messages stored)
✅ Agent listing: PASSED

🎉 All core functionality working!
```

### Example Chat Results:

**Q: "What's the current LLM visibility score?"**
✅ Agent correctly retrieved 28.4/100 score

**Q: "What are top 3 improvements?"**
✅ Agent prioritized recommendations from context

**Q: "Explain content gaps"**
✅ Agent referenced available data and suggested running analysis

**Q: "Track my progress"**
✅ Agent reported 1 audit completed

---

## Performance Considerations

### Memory Usage
- Active agents stored in memory dictionary
- Consider Redis for production scale (1000+ users)
- Context loaded fresh on each chat (ensures up-to-date data)

### Credit Management
- 1 credit per chat message
- User notified when insufficient credits
- All chats logged for auditing

### Database Queries
- Optimized with indexes on:
  - `site_id` + `user_id`
  - `created_at` (for latest data)
- Limits results (Top 5 opportunities)

---

## Security

### Authentication
- All endpoints protected with JWT
- Agents owned by specific users
- Site-level access control

### Data Privacy
- Users only see their own agents
- Context limited to their sites
- Chat history private per user

---

## Future Enhancements

### Planned Features
1. **Multi-Website Agents**: Agent that tracks multiple websites
2. **Automated Actions**: Agent can trigger audits/analyses
3. **Scheduled Reports**: Weekly summary from agent
4. **Voice Mode**: Voice chat with agent
5. **Comparison Mode**: Compare multiple websites
6. **Alert System**: Agent proactively notifies about issues
7. **Team Collaboration**: Share agent with team members
8. **Export Reports**: PDF/CSV exports of recommendations

### Integration Opportunities
- Slack/Discord bot integration
- Email digest from agent
- API webhooks for automation
- Zapier integration

---

## Support & Troubleshooting

### Common Issues

**Q: Agent not showing context**
A: Ensure audits/analyses have been run first. Agent needs data to reference.

**Q: Insufficient credits error**
A: Each chat message costs 1 credit. Upgrade plan or purchase credits.

**Q: Agent giving generic advice**
A: Run more analyses to populate context. Agent's quality improves with more data.

**Q: Context not updating**
A: Context is loaded fresh on each chat. Run new analyses and they'll appear immediately.

---

## API Rate Limits

- **Agent Creation**: 10 per hour per user
- **Chat Messages**: 100 per hour per user
- **History Retrieval**: 50 requests per hour

---

## Conclusion

The LLM Visibility Agent is a powerful, context-aware assistant that helps users improve their website's visibility in AI-powered search engines. With comprehensive memory of website-specific data across all 8 modules, it provides personalized, actionable advice that improves over time.

**Status**: ✅ Production Ready
**Version**: 1.0
**Last Updated**: October 14, 2025
