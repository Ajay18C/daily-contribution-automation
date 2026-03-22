import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import get_client
from api.routers import views, endpoints

# Configure high-level application logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instantiate the root execution instance strictly without ASGI lifespans since Vercel Lambda does not support uvicorn events natively
app = FastAPI(
    title="SkillTap Automation API",
    description="Industry-standard modular API serving execution contexts and configuration operations.",
    version="1.0.1"
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