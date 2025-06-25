#!/usr/bin/env python3
"""
Django Project Dependency Checker
Run this script in your project root directory to analyze your dependencies
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements_file():
    """Check if requirements.txt exists and show its contents"""
    req_file = Path("requirements.txt")
    
    print("=" * 50)
    print("CHECKING REQUIREMENTS.TXT")
    print("=" * 50)
    
    if req_file.exists():
        print("✅ requirements.txt found!")
        print("\nCurrent dependencies:")
        print("-" * 30)
        with open(req_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    print(f"{line_num:2}. {line}")
        return True
    else:
        print("❌ requirements.txt not found!")
        return False

def check_installed_packages():
    """Check what's actually installed in the current environment"""
    print("\n" + "=" * 50)
    print("CHECKING INSTALLED PACKAGES")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            print(f"✅ Found {len(lines)-2} installed packages:")  # -2 for header lines
            print("\nDjango-related packages:")
            print("-" * 30)
            
            django_packages = []
            for line in lines[2:]:  # Skip header lines
                if 'django' in line.lower() or any(pkg in line.lower() for pkg in 
                    ['psycopg', 'pillow', 'gunicorn', 'whitenoise', 'decouple', 'htmx']):
                    django_packages.append(line)
            
            if django_packages:
                for pkg in django_packages:
                    print(f"  📦 {pkg}")
            else:
                print("  ❌ No Django-related packages found")
                
        else:
            print("❌ Error checking installed packages")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def check_project_structure():
    """Check basic Django project structure"""
    print("\n" + "=" * 50)
    print("CHECKING PROJECT STRUCTURE")
    print("=" * 50)
    
    # Check for common Django files
    important_files = [
        'manage.py',
        'settings.py',
        '.env',
        'db.sqlite3'
    ]
    
    print("Essential files:")
    print("-" * 20)
    for file in important_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            # Check in subdirectories for settings.py
            if file == 'settings.py':
                found = False
                for item in Path('.').iterdir():
                    if item.is_dir() and (item / 'settings.py').exists():
                        print(f"✅ {file} (found in {item}/)")
                        found = True
                        break
                if not found:
                    print(f"❌ {file}")
            else:
                print(f"❌ {file}")

def check_django_apps():
    """Try to detect Django apps in the project"""
    print("\nDjango apps detected:")
    print("-" * 20)
    
    app_count = 0
    for item in Path('.').iterdir():
        if item.is_dir() and (item / 'models.py').exists():
            print(f"📁 {item.name}/")
            app_count += 1
    
    if app_count == 0:
        print("❌ No Django apps detected")
    else:
        print(f"\n✅ Found {app_count} potential Django app(s)")

def main():
    print("🔍 DJANGO PROJECT ANALYSIS")
    print("This script will check your project dependencies and structure")
    print("\nCurrent directory:", os.getcwd())
    
    # Step 1: Check requirements
    has_requirements = check_requirements_file()
    
    # Step 2: Check installed packages
    check_installed_packages()
    
    # Step 3: Check project structure
    check_project_structure()
    
    print("\n" + "=" * 50)
    print("ANALYSIS COMPLETE")
    print("=" * 50)
    
    if not has_requirements:
        print("\n💡 TIP: Create requirements.txt by running:")
        print("   pip freeze > requirements.txt")

if __name__ == "__main__":
    main()
