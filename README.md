# RankForge - AI SEO Services Platform

## Overview
Production-ready, full-stack AI-powered SEO services platform built with **FastAPI**, **React**, **MongoDB**, **Redis**, and **RQ** (Redis Queue) for asynchronous processing.

## Architecture Highlights

### SOLID Principles Implementation

1. **Single Responsibility Principle**
   - Each module handles one concern (services, models, API routes, workers)
   - Separate services for SEO audits, keyword research, billing, and AI agents

2. **Open/Closed Principle**
   - Base analyzer classes that can be extended without modification
   - Plugin-style architecture for new SEO features

3. **Liskov Substitution**
   - Abstract base classes for analyzers and AI agents
   - All implementations can be used interchangeably

4. **Interface Segregation**
   - Focused interfaces for different SEO aspects (technical, on-page, off-page)
   - Separate services for distinct functionalities

5. **Dependency Inversion**
   - Dependencies injected through FastAPI's dependency injection
   - Services depend on abstractions, not concrete implementations

## Key Features

### 1. Scalability (10,000+ Users)
- **Redis + RQ**: Asynchronous job processing for SEO audits and keyword research
- **MongoDB**: NoSQL database optimized for high-volume operations
- **Connection pooling**: Efficient database and Redis connections
- **Rate limiting ready**: Infrastructure supports throttling

### 2. AI SEO Agents (Parlant.io-style)
- **Conversational AI assistants** specialized in:
  - SEO Audit Analysis
  - Keyword Research
  - Content Optimization
  - Competitor Analysis
- **Groq API integration** for fast LLM responses
- **Context-aware conversations** with history tracking
- **Persistent agent instances** for continuous interactions

### 3. Credit System
- **20 free credits** on signup
- **Credit costs** per feature:
  - Site Audit: 5 credits
  - Keyword Research: 2 credits
  - Content Optimization: 3 credits
  - AI Agent Chat: 1 credit per message
- **Automatic deduction** with transaction logging

### 4. PayPal Integration
- **Sandbox mode** for testing
- **Subscription plans**: Free, Starter ($49), Growth ($79), Professional ($149)
- **One-time credit purchases**
- **Webhook support** for payment confirmations

### 5. SEO Features
- **Comprehensive Site Audits**: Technical, On-Page, Off-Page analysis
- **Keyword Research**: AI-powered keyword discovery with intent analysis
- **Rank Tracking**: Monitor keyword positions
- **Competitor Analysis**: Compare with competitors
- **Automated Recommendations**: AI-generated action plans

### 6. Modern, Responsive UI
- **Glassmorphism effects** with backdrop blur
- **Gradient accents** (subtle, not overwhelming)
- **Custom fonts**: Space Grotesk (headings), Inter (body)
- **Smooth animations**: Fade-in, slide-in, scale effects
- **Mobile-responsive** with Tailwind CSS
- **Dark mode ready** architecture

## Tech Stack

### Backend
- **FastAPI**: High-performance async Python framework
- **MongoDB**: Document database with Motor (async driver)
- **Redis**: In-memory data store for job queues
- **RQ (Redis Queue)**: Distributed task queue
- **Groq**: Fast LLM inference for AI agents
- **PyJWT**: JWT authentication
- **Bcrypt**: Password hashing
- **Pydantic**: Data validation
- **httpx**: Async HTTP client

### Frontend
- **React 19**: UI library
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **Tailwind CSS**: Utility-first CSS
- **Shadcn/UI**: Component library
- **Recharts**: Data visualization
- **Sonner**: Toast notifications
- **Lucide React**: Icon library

## Project Structure

```
/app/
├── backend/
│   ├── server.py              # FastAPI application entry point
│   ├── core/
│   │   ├── config.py          # Settings and configuration
│   │   ├── security.py        # JWT, password hashing
│   │   ├── database.py        # MongoDB, Redis connections
│   │   └── dependencies.py    # FastAPI dependencies
│   ├── api/
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── sites.py           # Site management
│   │   ├── audits.py          # SEO audit endpoints
│   │   ├── keywords.py        # Keyword research
│   │   ├── agents.py          # AI agent management
│   │   └── billing.py         # PayPal integration
│   ├── services/
│   │   ├── seo_audit.py       # SEO analysis logic
│   │   ├── keyword_service.py # Keyword research service
│   │   ├── ai_agents.py       # AI agent implementations
│   │   └── billing.py         # Payment processing
│   ├── schemas/
│   │   └── schemas.py         # Pydantic models
│   ├── workers/
│   │   ├── worker.py          # RQ worker process
│   │   └── tasks.py           # Background job definitions
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.js             # Main application component
│   │   ├── contexts/
│   │   │   └── AuthContext.js # Authentication state
│   │   ├── pages/
│   │   │   ├── LandingPage.js
│   │   │   ├── Dashboard.js
│   │   │   ├── Sites.js
│   │   │   ├── Audits.js
│   │   │   ├── Keywords.js
│   │   │   ├── AIAgents.js
│   │   │   └── Billing.js
│   │   ├── components/ui/     # Shadcn components
│   │   ├── utils/api.js       # API client
│   │   ├── index.css          # Global styles
│   │   └── App.css            # Component styles
│   ├── package.json
│   └── .env
```

## Environment Variables

### Backend (.env)
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="seo_platform"
REDIS_URL="redis://localhost:6379/0"
JWT_SECRET="your-secret-key"
GROQ_API_KEY="gsk_..." # Provided
PAYPAL_CLIENT_ID="your-paypal-client-id"
PAYPAL_CLIENT_SECRET="your-paypal-secret"
PAYPAL_MODE="sandbox"
CORS_ORIGINS="*"
```

### Frontend (.env)
```bash
REACT_APP_BACKEND_URL=https://domain-insight-hub.preview.emergentagent.com
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user (20 free credits)
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Sites
- `POST /api/sites/` - Add new site
- `GET /api/sites/` - Get all sites
- `GET /api/sites/{id}` - Get site details
- `DELETE /api/sites/{id}` - Delete site

### Audits
- `POST /api/audits/` - Run SEO audit (costs 5 credits)
- `GET /api/audits/site/{site_id}` - Get site audits
- `GET /api/audits/{audit_id}` - Get audit details

### Keywords
- `POST /api/keywords/research` - Research keywords (costs 2 credits)
- `POST /api/keywords/` - Track keyword
- `GET /api/keywords/site/{site_id}` - Get site keywords

### AI Agents
- `POST /api/agents/` - Create AI agent
- `GET /api/agents/` - Get all agents
- `POST /api/agents/chat` - Chat with agent (costs 1 credit)
- `GET /api/agents/{id}/history` - Get chat history

### Billing
- `GET /api/billing/plans` - Get pricing plans
- `POST /api/billing/upgrade` - Upgrade plan
- `POST /api/billing/paypal/capture` - Capture PayPal payment
- `GET /api/billing/transactions` - Get transaction history

## Running the Application

### Services Status
```bash
sudo supervisorctl status
```

### Restart Services
```bash
# Backend
sudo supervisorctl restart backend

# Frontend
sudo supervisorctl restart frontend
```

### View Logs
```bash
# Backend logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/backend.out.log

# Frontend logs
tail -f /var/log/supervisor/frontend.err.log
tail -f /var/log/supervisor/frontend.out.log
```

## Database Collections

- **users**: User accounts, credits, plans
- **sites**: User websites
- **audits**: SEO audit results
- **keywords**: Tracked keywords
- **agents**: AI agent instances
- **chat_sessions**: Agent conversation history
- **credit_transactions**: Credit usage log
- **subscriptions**: Payment subscriptions

## Credit Costs Reference

| Feature | Cost |
|---------|------|
| Site Audit | 5 credits |
| Keyword Research | 2 credits |
| Content Optimization | 3 credits |
| Competitor Analysis | 4 credits |
| Rank Tracking | 1 credit |
| AI Agent Chat | 1 credit/message |

## Pricing Plans

| Plan | Price | Credits/Month | Features |
|------|-------|---------------|----------|
| Free | $0 | 20 | 1 site, monthly audits, 10 keywords |
| Starter | $49 | 100 | 3 sites, weekly audits, 50 keywords |
| Growth | $79 | 200 | 5 sites, daily audits, 100 keywords, AI agents |
| Professional | $149 | 500 | 10 sites, real-time monitoring, 500 keywords |
| Agency | $399 | 2000 | 50 sites, unlimited audits, 2500 keywords |
| Enterprise | $999 | 10000 | Custom features |

## Testing

### Test User Registration
```bash
curl -X POST https://domain-insight-hub.preview.emergentagent.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'
```

### Test Login
```bash
curl -X POST https://domain-insight-hub.preview.emergentagent.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

## Production Deployment Notes

### Security
1. **Change JWT_SECRET** to a strong random value
2. **Use environment-specific CORS origins**
3. **Enable HTTPS** for all endpoints
4. **Implement rate limiting** on sensitive endpoints
5. **Add request validation** middleware
6. **Enable Redis password** authentication

### Scalability
1. **Scale RQ workers** horizontally for more throughput
2. **Use Redis Cluster** for high availability
3. **Implement caching** for frequently accessed data
4. **Add load balancer** for multiple backend instances
5. **Use CDN** for frontend assets
6. **MongoDB replica set** for redundancy

### Monitoring
1. **Set up logging** aggregation (ELK stack)
2. **Monitor Redis** queue length
3. **Track API response** times
4. **Alert on high error** rates
5. **Monitor credit** usage patterns

## Known Limitations

1. **Redis not installed**: RQ workers won't function without Redis. Install with `apt install redis-server`
2. **PayPal sandbox**: Requires PayPal developer account credentials
3. **SEO data**: Uses simulated metrics (integrate with real SEO APIs in production)
4. **Rate limiting**: Not implemented (add middleware)

## Future Enhancements

1. **Real SEO APIs**: Integrate with Ahrefs, SEMrush, Moz
2. **WebSocket support**: Real-time audit progress
3. **Email notifications**: Alert users on issues
4. **White-label**: Allow agencies to rebrand
5. **Mobile apps**: Native iOS/Android apps
6. **Advanced analytics**: Custom reports, exports
7. **Team collaboration**: Multi-user workspaces
8. **Automated fixes**: One-click SEO improvements

## Support & Documentation

For issues or questions:
- Check logs: `/var/log/supervisor/`
- API docs: `https://domain-insight-hub.preview.emergentagent.com/api/docs`
- Test endpoints: Use Postman or curl

## License

Proprietary - All rights reserved

---

**Built with ❤️ using SOLID principles, modern architecture, and scalable design**
