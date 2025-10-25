#!/usr/bin/env python

import os
import sys
from pathlib import Path

# Add the project to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lannister_news_api.settings')

print("=== Environment Variables ===")
for key in ['USE_SQLITE', 'MYSQL_DB', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_HOST', 'MYSQL_PORT']:
    print(f"{key}: {os.getenv(key)}")

print("\n=== Settings Debug ===")
try:
    import django
    django.setup()
    
    from django.conf import settings
    
    print(f"Settings module: {settings.SETTINGS_MODULE}")
    
    if hasattr(settings, 'DATABASES'):
        print("DATABASES setting exists")
        print(f"DATABASES keys: {list(settings.DATABASES.keys())}")
        
        if 'default' in settings.DATABASES:
            db_config = settings.DATABASES['default']
            print(f"Default database ENGINE: {db_config.get('ENGINE', 'NOT SET')}")
            print(f"Default database NAME: {db_config.get('NAME', 'NOT SET')}")
            print(f"Default database HOST: {db_config.get('HOST', 'NOT SET')}")
            print(f"Default database USER: {db_config.get('USER', 'NOT SET')}")
        else:
            print("No 'default' database configured")
    else:
        print("DATABASES setting does not exist")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()