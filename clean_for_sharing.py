"""
Clean project for sharing - removes all sensitive data.
Run this script before sharing the project with others.
"""

import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Files and folders to remove
SENSITIVE_ITEMS = [
    # Environment file with API keys
    '.env',
    
    # Credentials folder contents (keep .gitkeep)
    'credentials/google_service_account.json',
    'credentials/elecbee-data-analyst-97e26d3e6b17.json',
    
    # Data folder (contains analytics data)
    'data',
    
    # Generated reports
    '# 网站运营分析报告.txt',
    '# 网站运营分析报告-月度.txt',
    'test_report.txt',
    
    # Python virtual environment
    'venv',
    
    # Python cache
    '__pycache__',
    'src/__pycache__',
    'src/fetchers/__pycache__',
    'src/analyzers/__pycache__',
    'src/publishers/__pycache__',
]

def clean_project():
    """Remove all sensitive files and folders."""
    print("🧹 Cleaning project for sharing...\n")
    
    removed_count = 0
    
    for item in SENSITIVE_ITEMS:
        path = PROJECT_ROOT / item
        
        if path.exists():
            if path.is_file():
                path.unlink()
                print(f"  ✅ Removed file: {item}")
                removed_count += 1
            elif path.is_dir():
                shutil.rmtree(path)
                print(f"  ✅ Removed folder: {item}")
                removed_count += 1
        else:
            print(f"  ⏭️  Not found: {item}")
    
    # Recreate empty data folder with .gitkeep
    data_dir = PROJECT_ROOT / 'data'
    data_dir.mkdir(exist_ok=True)
    (data_dir / '.gitkeep').write_text('# This folder stores raw API data (not committed)\n')
    print(f"  📁 Recreated empty data/ folder")
    
    print(f"\n✅ Cleanup complete! Removed {removed_count} items.")
    print("\n📋 Next steps:")
    print("  1. Verify .env.example has all required variables")
    print("  2. Update README.md if needed")
    print("  3. Share via GitHub or zip file")
    print("\n⚠️  Your friend will need to:")
    print("  - Create their own .env file from .env.example")
    print("  - Add their own Google service account JSON")
    print("  - Configure their own GA4, GSC, Gemini, and Notion credentials")

if __name__ == '__main__':
    confirm = input("This will remove all sensitive data. Continue? (y/N): ")
    if confirm.lower() == 'y':
        clean_project()
    else:
        print("Cancelled.")
