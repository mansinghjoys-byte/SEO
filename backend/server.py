from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import get_settings
from core.database import mongo_client
import logging

# Import routers
from api import auth, sites, audits, keywords, agents, billing, admin

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title='AI SEO Platform',
    description='Production-ready AI-powered SEO services platform',
    version='1.0.0'
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(','),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Include routers with /api prefix
app.include_router(auth.router, prefix='/api')
app.include_router(sites.router, prefix='/api')
app.include_router(audits.router, prefix='/api')
app.include_router(keywords.router, prefix='/api')
app.include_router(agents.router, prefix='/api')
app.include_router(billing.router, prefix='/api')

# Root endpoint
@app.get('/api/')
async def root():
    return {
        'message': 'AI SEO Platform API',
        'version': '1.0.0',
        'status': 'operational'
    }

# Health check
@app.get('/api/health')
async def health_check():
    return {'status': 'healthy'}

# Startup event
@app.on_event('startup')
async def startup_event():
    logging.info('Starting AI SEO Platform...')
    logging.info(f'MongoDB connected: {settings.MONGO_URL}')
    logging.info(f'Redis URL: {settings.REDIS_URL}')

# Shutdown event
@app.on_event('shutdown')
async def shutdown_event():
    mongo_client.close()
    logging.info('AI SEO Platform shut down')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
