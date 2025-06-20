"""
Configuration settings for AI Persona Image Generator
"""

import os
from typing import Optional

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
SD_API_URL = os.getenv("SD_API_URL", "http://127.0.0.1:7860")
SD_MODEL_CHECKPOINT = os.getenv("SD_MODEL_CHECKPOINT", "your_model_name.safetensors")

# File Paths
INPUT_JSON_FILE = os.getenv("INPUT_JSON_FILE", "bhm-prvs.json")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "generated_images")
DATABASE_FILE = os.getenv("DATABASE_FILE", "profiles.db")

# Stable Diffusion Settings
SD_SETTINGS = {
    "steps": 30,
    "sampler_name": "DPM++ 2M Karras",
    "cfg_scale": 7,
    "width": 1024,
    "height": 1024,
    "seed": -1,
    "restore_faces": True,
    "batch_size": 1
}

# OpenAI Settings
OPENAI_SETTINGS = {
    "model": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 1000
}

# Processing Settings
PROCESSING_SETTINGS = {
    "prompt_delay": 1,  # seconds between prompt generations
    "image_delay": 2,   # seconds between image generations
    "timeout": 300      # seconds for API requests
}

def validate_config() -> bool:
    """Validate configuration settings."""
    errors = []
    
    if OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
        errors.append("OPENAI_API_KEY not set - please update config.py or set environment variable")
    
    if SD_MODEL_CHECKPOINT == "your_model_name.safetensors":
        errors.append("SD_MODEL_CHECKPOINT not set - please update with your actual model filename")
    
    if not os.path.exists(INPUT_JSON_FILE):
        errors.append(f"Input JSON file not found: {INPUT_JSON_FILE}")
    
    if errors:
        print("Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

def get_sd_payload(positive_prompt: str, negative_prompt: str) -> dict:
    """Generate Stable Diffusion API payload with current settings."""
    return {
        "prompt": positive_prompt,
        "negative_prompt": negative_prompt,
        **SD_SETTINGS,
        "override_settings": {
            "sd_model_checkpoint": SD_MODEL_CHECKPOINT
        }
    } 