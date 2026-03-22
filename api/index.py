import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import get_client
from api.routers import views, endpoints

# Configure high-level application logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application handling secure Motor instantiation."""
    try:
        db = get_client()
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Pool natively.")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
    
    yield  # The FastAPI instances serve robustly here
    
    try:
        db = get_client()
        db.close()
        logger.info("Successfully decoupled from MongoDB.")
    except Exception as e:
        logger.error(f"Error disconnecting from MongoDB Contexts: {e}")

# Instantiate the root execution instance
app = FastAPI(
    title="SkillTap Automation API",
    description="Industry-standard modular API serving execution contexts and configuration operations.",
    version="1.0.1",
    lifespan=lifespan
)

# Standard Security Configuration resolving frontend cross-domain requests internally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modular Route Injections mapping decoupled file architectures physically resolving dependencies automatically
app.include_router(views.router)
app.include_router(endpoints.router)