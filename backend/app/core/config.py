"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import List, Optional
from pathlib import Path


def find_project_root(start_path: Optional[Path] = None) -> Path:
    """Find project root by looking for .env file or .git directory."""
    if start_path is None:
        start_path = Path(__file__).resolve()
    
    current = start_path if start_path.is_file() else start_path.parent
    
    # Walk up the directory tree
    for parent in [current] + list(current.parents):
        # Check for .env file (project root marker)
        if (parent / ".env").exists():
            return parent
        # Or check for .git directory (also indicates project root)
        if (parent / ".git").exists():
            return parent
    
    # Fallback to current directory if nothing found
    return current


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/claim_agent"
    
    # Storage
    STORAGE_PATH: str = "storage"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    class Config:
        # Find project root and look for .env there
        project_root = find_project_root()
        env_file = str(project_root / ".env")
        case_sensitive = True


settings = Settings()

