import os
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Config:
    """Configuration settings for MIMÉTICA MVP"""
    
    # API Keys - initialize with fallbacks for when streamlit is not available
    OPENAI_API_KEY: str = field(default="")
    ANTHROPIC_API_KEY: str = field(default="")
    PINECONE_API_KEY: str = field(default="")
    PINECONE_ENVIRONMENT: str = field(default="")
    SERPER_API_KEY: str = field(default="")
    
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
    
    # Model Configuration
    # Default model for the application - lightweight yet effective for strategic analysis
    DEFAULT_MODEL: str = "gpt-4o-mini"
    
    # Available models for strategic analysis - will be initialized in __post_init__
    AVAILABLE_MODELS: dict = field(default_factory=dict)
    
    # Simulation Settings
    MONTE_CARLO_RUNS: int = 1000
    
    # Rate Limiting Settings by Provider
    RATE_LIMITS: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize AVAILABLE_MODELS and secrets after dataclass initialization"""
        # Initialize secrets from streamlit if available
        try:
            import streamlit as st
            if hasattr(st, 'secrets'):
                self.OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
                self.ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY", "")
                self.PINECONE_API_KEY = st.secrets.get("PINECONE_API_KEY", "")
                self.PINECONE_ENVIRONMENT = st.secrets.get("PINECONE_ENVIRONMENT", "")
                self.SERPER_API_KEY = st.secrets.get("SERPER_API_KEY", "")
        except (ImportError, AttributeError, KeyError):
            # Fallback to environment variables if streamlit secrets not available
            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
            self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
            self.PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
            self.PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")
            self.SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
        
        # Initialize AVAILABLE_MODELS if not already done
        if not self.AVAILABLE_MODELS:  # Check if empty dict instead of None
            self.AVAILABLE_MODELS = {
                # OpenAI Models - optimized for strategic analysis
                "gpt-4o-mini": {
                    "provider": "openai",
                    "name": "GPT-4o Mini",
                    "description": "Fast, cost-effective model ideal for analysis and reasoning",
                    "max_tokens": 128000,
                    "good_for": "Strategic analysis, document processing, general reasoning",
                    "tpm_limit": 200000,
                    "rpm_limit": 10000
                },
                "gpt-4o": {
                    "provider": "openai", 
                    "name": "GPT-4o",
                    "description": "Advanced model with superior reasoning for complex analysis",
                    "max_tokens": 128000,
                    "good_for": "Complex strategic decisions, detailed analysis, multi-step reasoning",
                    "tpm_limit": 300000,
                    "rpm_limit": 10000
                },
                "gpt-4-turbo": {
                    "provider": "openai",
                    "name": "GPT-4 Turbo", 
                    "description": "High-performance model for comprehensive strategic work",
                    "max_tokens": 128000,
                    "good_for": "Comprehensive reports, complex problem solving, strategic planning",
                    "tpm_limit": 300000,
                    "rpm_limit": 10000
                },
                
                # Anthropic Models - excellent for analysis and reasoning
                "claude-3-7-sonnet-latest": {
                    "provider": "anthropic",
                    "name": "Claude 3.7 Sonnet",
                    "description": "Latest fast model for quick analysis and insights",
                    "max_tokens": 200000,
                    "good_for": "Quick analysis, document summarization, rapid insights",
                    "tpm_limit": 20000,  # Anthropic's strict limit
                    "rpm_limit": 1000
                },
                "claude-sonnet-4-20250514": {
                    "provider": "anthropic",
                    "name": "Claude Sonnet 4",
                    "description": "Latest high-performance model with exceptional reasoning",
                    "max_tokens": 200000,
                    "good_for": "Complex strategic analysis, advanced reasoning, high-performance tasks",
                    "tpm_limit": 20000,  # Anthropic's strict limit
                    "rpm_limit": 1000
                },
                "claude-opus-4-20250514": {
                    "provider": "anthropic",
                    "name": "Claude 4 Opus",
                    "description": "Most capable model for complex strategic challenges",
                    "max_tokens": 200000,
                    "good_for": "Complex strategic planning, comprehensive analysis, sophisticated reasoning",
                    "tpm_limit": 20000,  # Anthropic's strict limit
                    "rpm_limit": 1000
                }
            }
        
        # Initialize rate limit settings
        if not self.RATE_LIMITS:
            self.RATE_LIMITS = {
                "anthropic": {
                    "tokens_per_minute": 20000,
                    "requests_per_minute": 1000,
                    "safety_margin": 0.75,  # Conservative for Anthropic
                    "inter_phase_delay": 15,
                    "max_retries": 3,
                    "retry_delay": 30
                },
                "openai": {
                    "tokens_per_minute": 200000,  # Default for most OpenAI models
                    "requests_per_minute": 10000,
                    "safety_margin": 0.85,  # More aggressive for OpenAI
                    "inter_phase_delay": 5,
                    "max_retries": 2,
                    "retry_delay": 15
                }
            }
    
    @classmethod
    def validate(cls) -> bool:
        """Validate essential configuration"""
        config = cls()
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        if not config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required")
        return True
    
    def get_current_model_config(self) -> dict:
        """Get configuration for currently selected model"""
        try:
            import streamlit as st
            # Get selected model from session state, fallback to default
            selected_model = st.session_state.get('selected_model', self.DEFAULT_MODEL)
        except:
            selected_model = self.DEFAULT_MODEL
        
        # Ensure AVAILABLE_MODELS is initialized
        if not self.AVAILABLE_MODELS:
            self.__post_init__()
        
        # Use self to access AVAILABLE_MODELS
        return self.AVAILABLE_MODELS.get(selected_model, self.AVAILABLE_MODELS[self.DEFAULT_MODEL])
    
    def get_model_provider(self, model_name: str = None) -> str:
        """Get the provider for a specific model"""
        # Ensure AVAILABLE_MODELS is initialized
        if not self.AVAILABLE_MODELS:
            self.__post_init__()
            
        if model_name is None:
            import streamlit as st
            model_name = st.session_state.get('selected_model', self.DEFAULT_MODEL)
        
        # Use self to access AVAILABLE_MODELS
        model_config = self.AVAILABLE_MODELS.get(model_name, self.AVAILABLE_MODELS[self.DEFAULT_MODEL])
        return model_config.get('provider', 'openai')
    
    def get_rate_limit_settings(self, model_name: str = None) -> dict:
        """Get rate limiting settings for a specific model or current model"""
        if model_name is None:
            try:
                import streamlit as st
                model_name = st.session_state.get('selected_model', self.DEFAULT_MODEL)
            except:
                model_name = self.DEFAULT_MODEL
        
        # Ensure models and rate limits are initialized
        if not self.AVAILABLE_MODELS:
            self.__post_init__()
        
        model_config = self.AVAILABLE_MODELS.get(model_name, self.AVAILABLE_MODELS[self.DEFAULT_MODEL])
        provider = model_config.get('provider', 'openai')
        
        # Get base rate limit settings for provider
        provider_settings = self.RATE_LIMITS.get(provider, self.RATE_LIMITS['openai']).copy()
        
        # Override with model-specific limits if available
        if 'tpm_limit' in model_config:
            provider_settings['tokens_per_minute'] = model_config['tpm_limit']
        if 'rpm_limit' in model_config:
            provider_settings['requests_per_minute'] = model_config['rpm_limit']
        
        return provider_settings
    
    def validate_and_fix_selected_model(self) -> str:
        """Validate the selected model and fix if outdated or invalid"""
        try:
            import streamlit as st
            # Get currently selected model
            selected_model = st.session_state.get('selected_model', self.DEFAULT_MODEL)
        except:
            # Fallback when Streamlit is not available
            selected_model = self.DEFAULT_MODEL
        
        # Ensure AVAILABLE_MODELS is initialized
        if not self.AVAILABLE_MODELS:
            self.__post_init__()
        
        # Model migration mapping for outdated model names
        model_migrations = {
            # Old incorrect model names to correct ones
            'claude-3-5-sonnet-latest': 'claude-3-7-sonnet-latest',     # Fix the non-existent model name
            'claude-3-5-sonnet-20241022': 'claude-3-7-sonnet-latest',  # Fix the incorrect model name
            'claude-3-sonnet-20240229': 'claude-3-7-sonnet-latest',    # Migrate old sonnet to newest
            'claude-3-sonnet': 'claude-3-7-sonnet-latest',             # Generic name to specific
            'claude-3-5-sonnet': 'claude-3-7-sonnet-latest',           # Version upgrade
        }
        
        # Check if model exists in current configuration
        if selected_model not in self.AVAILABLE_MODELS:
            # Check if there's a migration for this model
            if selected_model in model_migrations:
                new_model = model_migrations[selected_model]
                try:
                    import streamlit as st
                    st.session_state['selected_model'] = new_model
                    st.warning(f"Model '{selected_model}' has been updated to '{new_model}' (newer version)")
                except:
                    pass  # Streamlit not available
                return new_model
            else:
                # Fall back to default model
                try:
                    import streamlit as st
                    st.session_state['selected_model'] = self.DEFAULT_MODEL
                    st.warning(f"Model '{selected_model}' is not available. Using default model '{self.DEFAULT_MODEL}'")
                except:
                    pass  # Streamlit not available
                return self.DEFAULT_MODEL
        
        return selected_model

# Global config instance
config = Config()
