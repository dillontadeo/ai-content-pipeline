"""
Configuration management for the AI Content Pipeline.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration class for the pipeline."""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # HubSpot Configuration
    HUBSPOT_API_KEY = os.getenv('HUBSPOT_API_KEY')
    HUBSPOT_ACCOUNT_ID = os.getenv('HUBSPOT_ACCOUNT_ID')
    
    # Content Configuration
    BLOG_MIN_WORDS = int(os.getenv('BLOG_MIN_WORDS', 400))
    BLOG_MAX_WORDS = int(os.getenv('BLOG_MAX_WORDS', 600))
    NEWSLETTER_MAX_WORDS = int(os.getenv('NEWSLETTER_MAX_WORDS', 250))
    
    # Email Configuration
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'marketing@novamind.ai')
    SENDER_NAME = os.getenv('SENDER_NAME', 'NovaMind Team')
    
    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/pipeline.db')
    
    # Flask Configuration
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # Persona Definitions
    PERSONAS = {
        'founders': {
            'name': 'Founders / Decision-Makers',
            'focus': 'ROI, growth, efficiency',
            'tone': 'strategic and results-oriented'
        },
        'creatives': {
            'name': 'Creative Professionals',
            'focus': 'inspiration, time-saving tools',
            'tone': 'inspiring and innovative'
        },
        'operations': {
            'name': 'Operations Managers',
            'focus': 'workflows, integrations, reliability',
            'tone': 'practical and detail-oriented'
        }
    }
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        required = ['OPENAI_API_KEY']
        missing = [key for key in required if not getattr(cls, key)]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True

