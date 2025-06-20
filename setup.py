#!/usr/bin/env python3
"""
Setup script for AI Persona Image Generator
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required Python packages."""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False
    return True

def create_directories():
    """Create necessary directories."""
    print("Creating directories...")
    directories = ["generated_images"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory already exists: {directory}")

def check_configuration():
    """Check if configuration needs to be updated."""
    print("\nConfiguration Check:")
    print("=" * 30)
    
    # Check if config.py exists
    if not os.path.exists("config.py"):
        print("✗ config.py not found!")
        return False
    
    # Import and check configuration
    try:
        from config import OPENAI_API_KEY, SD_MODEL_CHECKPOINT, INPUT_JSON_FILE
        from config import validate_config
        
        print(f"OpenAI API Key: {'✓ Set' if OPENAI_API_KEY != 'YOUR_OPENAI_API_KEY' else '✗ Not set'}")
        print(f"SD Model: {'✓ Set' if SD_MODEL_CHECKPOINT != 'your_model_name.safetensors' else '✗ Not set'}")
        print(f"Input JSON: {'✓ Found' if os.path.exists(INPUT_JSON_FILE) else '✗ Not found'}")
        
        if validate_config():
            print("✓ Configuration is valid!")
            return True
        else:
            print("✗ Configuration needs to be updated.")
            return False
            
    except ImportError as e:
        print(f"✗ Error importing configuration: {e}")
        return False

def main():
    """Main setup function."""
    print("AI Persona Image Generator Setup")
    print("=" * 40)
    
    # Install dependencies
    if not install_dependencies():
        print("Setup failed at dependency installation.")
        return
    
    # Create directories
    create_directories()
    
    # Check configuration
    config_ok = check_configuration()
    
    print("\nSetup Summary:")
    print("=" * 20)
    if config_ok:
        print("✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Ensure Automatic1111 is running with --api flag")
        print("2. Run: python main.py --validate")
        print("3. Run: python main.py --parse-json")
        print("4. Run: python main.py --generate-prompts")
        print("5. Run: python main.py --generate-images")
    else:
        print("✗ Setup completed with configuration issues.")
        print("\nPlease update config.py with your settings:")
        print("- Set your OpenAI API key")
        print("- Set your Stable Diffusion model filename")
        print("- Ensure bhm-prvs.json is in the root directory")

if __name__ == "__main__":
    main() 