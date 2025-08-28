import os
from dataclasses import dataclass
from typing import Dict, Any
import streamlit as st

@dataclass
class Config:
    """Configuration settings for MIMÉTICA MVP"""
    
    # API Keys
    OPENAI_API_KEY: str = st.secrets["OPENAI_API_KEY"]
    PINECONE_API_KEY: str = st.secrets["PINECONE_API_KEY"]
    PINECONE_ENVIRONMENT: str = st.secrets["PINECONE_ENVIRONMENT"]
    SERPER_API_KEY: str = st.secrets["SERPER_API_KEY"]
    
    # Application Settings
    APP_TITLE: str = "MIMÉTICA MVP 1.0"
    APP_DESCRIPTION: str = "AI-Powered Strategic Decision Support System"
    
    # Security
    DEFAULT_PASSWORD: str = os.getenv("APP_PASSWORD", "mimetica2025")
    SESSION_TIMEOUT: int = 3600  # 1 hour
    
    # File Settings
    MAX_FILE_SIZE: int = 200 * 1024 * 1024  # 200MB
    ALLOWED_EXTENSIONS: tuple = (".pdf", ".docx", ".doc", ".csv", ".xlsx", ".xls")
    
    # Paths
    DATA_DIR: str = "data"
    OUTPUTS_DIR: str = "outputs"
    TEMP_DIR: str = "temp"
    
    # Vector Store Settings
    VECTOR_COLLECTION: str = "mimetica"
    VECTOR_SIZE: int = 1536  # OpenAI embedding size
    
    # Agent Settings
    MAX_ITERATIONS: int = 5
    TEMPERATURE: float = 0.7
    
    # Simulation Settings
    MONTE_CARLO_RUNS: int = 1000
    
    @classmethod
    def validate(cls) -> bool:
        """Validate essential configuration"""
        config = cls()
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        return True

# Global config instance
config = Config()
