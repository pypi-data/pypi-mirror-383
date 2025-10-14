"""Configuration module for DRF Postman Generator"""
from django.conf import settings

DEFAULT_CONFIG = {
    'COLLECTION_NAME': 'API Collection',
    'BASE_URL': '{{base_url}}',
    'OUTPUT_PATH': 'postman_collection.json',
}

def get_config():
    """
    Get configuration from Django settings with defaults.
    
    Users can override defaults in their settings.py:
    
    DRF_POSTMAN = {
        'COLLECTION_NAME': 'My API',
        'BASE_URL': 'https://api.example.com',
        'OUTPUT_PATH': 'postman_collection.json'
    }
    """
    user_config = getattr(settings, 'DRF_POSTMAN', {})
    config = DEFAULT_CONFIG.copy()
    config.update(user_config)
    return config