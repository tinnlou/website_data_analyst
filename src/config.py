"""
Configuration management module.
Loads environment variables and validates required settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Load .env file from project root
load_dotenv(PROJECT_ROOT / '.env')

# Google Credentials
GOOGLE_CREDENTIALS_PATH = os.getenv(
    'GOOGLE_APPLICATION_CREDENTIALS',
    str(PROJECT_ROOT / 'credentials' / 'google_service_account.json')
)

# GA4 Configuration
GA4_PROPERTY_ID = os.getenv('GA4_PROPERTY_ID', '')

# Search Console Configuration  
GSC_SITE_URL = os.getenv('GSC_SITE_URL', '')

# Gemini Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')

# Notion Configuration
NOTION_TOKEN = os.getenv('NOTION_TOKEN', '')
NOTION_PARENT_PAGE_ID = os.getenv('NOTION_PARENT_PAGE_ID', '')

# Report Configuration
REPORT_LANGUAGE = 'zh'  # Chinese
REPORT_DETAIL_LEVEL = 'detailed'  # detailed | concise


def validate_config() -> dict:
    """
    Validate all required configuration values are set.
    Returns a dict with validation results.
    """
    errors = []
    warnings = []
    
    # Check Google credentials
    if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
        errors.append(f"Google Service Account JSON not found at: {GOOGLE_CREDENTIALS_PATH}")
    
    # Check GA4 Property ID
    if not GA4_PROPERTY_ID:
        errors.append("GA4_PROPERTY_ID is not set")
    
    # Check Search Console Site URL
    if not GSC_SITE_URL:
        errors.append("GSC_SITE_URL is not set")
    
    # Check Gemini API Key
    if not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY is not set")
    
    # Check Notion configuration
    if not NOTION_TOKEN:
        errors.append("NOTION_TOKEN is not set")
    
    if not NOTION_PARENT_PAGE_ID:
        errors.append("NOTION_PARENT_PAGE_ID is not set")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def print_config_status():
    """Print current configuration status."""
    print("=" * 50)
    print("Configuration Status")
    print("=" * 50)
    
    result = validate_config()
    
    if result['valid']:
        print("✅ All configurations are valid!")
    else:
        print("❌ Configuration errors found:")
        for error in result['errors']:
            print(f"   - {error}")
    
    if result['warnings']:
        print("\n⚠️  Warnings:")
        for warning in result['warnings']:
            print(f"   - {warning}")
    
    print("=" * 50)
    return result['valid']


if __name__ == '__main__':
    print_config_status()
