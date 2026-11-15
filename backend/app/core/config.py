import os
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "HeatHack Solar API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*"
    ]
    
    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Solar Planning Defaults
    DEFAULT_PANEL_WATTAGE: int = int(os.getenv("DEFAULT_PANEL_WATTAGE", 500))
    DEFAULT_PANEL_LENGTH_M: float = float(os.getenv("DEFAULT_PANEL_LENGTH_M", 2.0))
    DEFAULT_PANEL_WIDTH_M: float = float(os.getenv("DEFAULT_PANEL_WIDTH_M", 1.05))
    DEFAULT_MONTHLY_YIELD_KWH: float = float(os.getenv("DEFAULT_MONTHLY_YIELD_KWH_PER_KW", 120.0))
    DEFAULT_COST_PER_KW: float = float(os.getenv("DEFAULT_BENCHMARK_COST_PER_KW", 60000.0))
    
    # Cooling Planning Defaults
    DEFAULT_COOL_ROOF_RATE_PER_SQM: float = float(os.getenv("DEFAULT_COOL_ROOF_RATE_PER_SQM", 100.0))
    DEFAULT_SURFACE_PREP_COST: float = float(os.getenv("DEFAULT_SURFACE_PREP_COST", 1000.0))

settings = Settings()
