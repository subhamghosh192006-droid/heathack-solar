"""
HeatHack Solar — FastAPI Backend Entrypoint
AI Rooftop Solar & Urban Cooling Planner
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import roof, solar, cooling, bill, chat

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Map-based AI Rooftop Solar & Urban Cooling Planner with zero-shot AI models, geospatial processing, and transparent calculations."
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(roof.router, prefix=settings.API_V1_STR)
app.include_router(solar.router, prefix=settings.API_V1_STR)
app.include_router(cooling.router, prefix=settings.API_V1_STR)
app.include_router(bill.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "project": "HeatHack Solar",
        "tagline": "Plan solar on your roof. Prioritise cooling in your neighbourhood.",
        "status": "online",
        "docs_url": "/docs",
        "version": settings.VERSION
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
