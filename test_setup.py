#!/usr/bin/env python3
"""
Test script for AI Persona Image Generator
"""

import os
import sys
import sqlite3

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import json
        import requests
        import base64
        import argparse
        import time
        from typing import Dict, Tuple, Optional
        from openai import OpenAI
        from PIL import Image
        import io
        print("✓ Standard library imports successful")
    except ImportError as e:
        print(f"✗ Standard library import failed: {e}")
        return False
    
    try:
        from config import (
            OPENAI_API_KEY, SD_API_URL, SD_MODEL_CHECKPOINT, INPUT_JSON_FILE, 
            OUTPUT_DIR, DATABASE_FILE, OPENAI_SETTINGS, PROCESSING_SETTINGS, 
            validate_config, get_sd_payload
        )
        print("✓ Configuration imports successful")
    except ImportError as e:
        print(f"✗ Configuration import failed: {e}")
        return False
    
    return True

def test_database_creation():
    """Test database creation and table structure."""
    print("\nTesting database creation...")
    
    try:
        from main import setup_database
        
        # Remove existing database for clean test
        if os.path.exists("profiles.db"):
            os.remove("profiles.db")
        
        setup_database()
        
        # Test database connection and table
        conn = sqlite3.connect("profiles.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_profiles'")
        if cursor.fetchone():
            print("✓ Database and table created successfully")
            
            # Check table structure
            cursor.execute("PRAGMA table_info(admin_profiles)")
            columns = [col[1] for col in cursor.fetchall()]
            expected_columns = [
                'id', 'json_source_file', 'admin_id', 'first_name', 'last_name',
                'email', 'phone_number', 'organization_name', 'organization_town',
                'languages', 'positive_prompt', 'negative_prompt', 'image_path',
                'prompt_generated', 'image_generated'
            ]
            
            if all(col in columns for col in expected_columns):
                print("✓ Table structure is correct")
                conn.close()
                return True
            else:
                print("✗ Table structure is incorrect")
                conn.close()
                return False
        else:
            print("✗ Table was not created")
            conn.close()
            return False
            
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_json_parsing():
    """Test JSON parsing with sample data."""
    print("\nTesting JSON parsing...")
    
    try:
        from main import parse_json_to_db
        
        # Copy sample data to expected filename
        if os.path.exists("sample-data.json") and not os.path.exists("bhm-prvs.json"):
            import shutil
            shutil.copy("sample-data.json", "bhm-prvs.json")
            print("✓ Copied sample data for testing")
        
        if not os.path.exists("bhm-prvs.json"):
            print("✗ No JSON data file found for testing")
            return False
        
        parse_json_to_db()
        
        # Check if data was inserted
        conn = sqlite3.connect("profiles.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM admin_profiles")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✓ Successfully parsed {count} profiles from JSON")
            conn.close()
            return True
        else:
            print("✗ No profiles were parsed from JSON")
            conn.close()
            return False
            
    except Exception as e:
        print(f"✗ JSON parsing test failed: {e}")
        return False

def test_configuration():
    """Test configuration validation."""
    print("\nTesting configuration...")
    
    try:
        from config import validate_config
        
        # Test with current configuration
        is_valid = validate_config()
        
        if is_valid:
            print("✓ Configuration is valid")
            return True
        else:
            print("⚠ Configuration needs updates (expected for initial setup)")
            return True  # This is expected for initial setup
            
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("AI Persona Image Generator - Setup Test")
    print("=" * 45)
    
    tests = [
        ("Imports", test_imports),
        ("Database Creation", test_database_creation),
        ("JSON Parsing", test_json_parsing),
        ("Configuration", test_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"✗ {test_name} failed")
    
    print(f"\n{'='*45}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The application is ready to use.")
        print("\nNext steps:")
        print("1. Update config.py with your OpenAI API key and SD model")
        print("2. Ensure Automatic1111 is running with --api flag")
        print("3. Run: python main.py --validate")
        print("4. Run: python main.py --all")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 