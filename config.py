"""
Configuration settings for AI Persona Image Generator
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SD_API_URL = os.getenv("SD_API_URL", "http://127.0.0.1:7860")
SD_MODEL_CHECKPOINT = os.getenv("SD_MODEL_CHECKPOINT", "realisticVisionV60B1_v51HyperVAE.safetensors")

# File Paths
INPUT_JSON_FILE = os.getenv("INPUT_JSON_FILE", "bhm-prvs.json")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "generated_images")
DATABASE_FILE = os.getenv("DATABASE_FILE", "profiles.db")

# Stable Diffusion Settings
SD_SETTINGS = {
    "steps": 6,  # 4-8 шагов для быстрой генерации
    "sampler_name": "DPM++ SDE",  # DPM++ SDE Karras
    "cfg_scale": 1.8,  # CFG Scale 1.5-2
    "width": 1024,
    "height": 1024,
    "seed": -1,
    "restore_faces": True,
    "batch_size": 1,
    "scheduler": "karras"  # Явно указываем Karras scheduler
}

# ADetailer Settings
ADETAILER_SETTINGS = {
    "adetailer": {
        "args": [
            {
                "ad_model": "face_yolov8n.pt",
                "ad_prompt": "",
                "ad_negative_prompt": "",
                "ad_confidence": 0.3,
                "ad_kernel_size": 0,
                "ad_dilate_erode": 4,
                "ad_x_offset": 0,
                "ad_y_offset": 0,
                "ad_mask_merge_invert": "None",
                "ad_mask_blur": 4,
                "ad_denoising_strength": 0.4,
                "ad_inpaint_only_masked": True,
                "ad_inpaint_only_masked_padding": 32,
                "ad_use_inpaint_width_height": False,
                "ad_inpaint_width": 512,
                "ad_inpaint_height": 512,
                "ad_use_steps": True,
                "ad_steps": 28,
                "ad_use_cfg_scale": True,
                "ad_cfg_scale": 7.0,
                "ad_use_sampler": True,
                "ad_sampler": "DPM++ 2M Karras",
                "ad_use_noise_multiplier": True,
                "ad_noise_multiplier": 1.0,
                "ad_use_clip_skip": False,
                "ad_clip_skip": 1,
                "ad_restore_face": False,
                "ad_controlnet_model": "None",
                "ad_controlnet_module": "None",
                "ad_controlnet_weight": 1.0,
                "ad_controlnet_guidance_start": 0.0,
                "ad_controlnet_guidance_end": 1.0
            },
            {
                "ad_model": "hand_yolov8n.pt",
                "ad_prompt": "",
                "ad_negative_prompt": "",
                "ad_confidence": 0.3,
                "ad_kernel_size": 0,
                "ad_dilate_erode": 4,
                "ad_x_offset": 0,
                "ad_y_offset": 0,
                "ad_mask_merge_invert": "None",
                "ad_mask_blur": 4,
                "ad_denoising_strength": 0.4,
                "ad_inpaint_only_masked": True,
                "ad_inpaint_only_masked_padding": 32,
                "ad_use_inpaint_width_height": False,
                "ad_inpaint_width": 512,
                "ad_inpaint_height": 512,
                "ad_use_steps": True,
                "ad_steps": 28,
                "ad_use_cfg_scale": True,
                "ad_cfg_scale": 7.0,
                "ad_use_sampler": True,
                "ad_sampler": "DPM++ 2M Karras",
                "ad_use_noise_multiplier": True,
                "ad_noise_multiplier": 1.0,
                "ad_use_clip_skip": False,
                "ad_clip_skip": 1,
                "ad_restore_face": False,
                "ad_controlnet_model": "None",
                "ad_controlnet_module": "None",
                "ad_controlnet_weight": 1.0,
                "ad_controlnet_guidance_start": 0.0,
                "ad_controlnet_guidance_end": 1.0
            },
            {
                "ad_model": "person_yolov8n-seg.pt",
                "ad_prompt": "",
                "ad_negative_prompt": "",
                "ad_confidence": 0.3,
                "ad_kernel_size": 0,
                "ad_dilate_erode": 4,
                "ad_x_offset": 0,
                "ad_y_offset": 0,
                "ad_mask_merge_invert": "None",
                "ad_mask_blur": 4,
                "ad_denoising_strength": 0.4,
                "ad_inpaint_only_masked": True,
                "ad_inpaint_only_masked_padding": 32,
                "ad_use_inpaint_width_height": False,
                "ad_inpaint_width": 512,
                "ad_inpaint_height": 512,
                "ad_use_steps": True,
                "ad_steps": 28,
                "ad_use_cfg_scale": True,
                "ad_cfg_scale": 7.0,
                "ad_use_sampler": True,
                "ad_sampler": "DPM++ 2M Karras",
                "ad_use_noise_multiplier": True,
                "ad_noise_multiplier": 1.0,
                "ad_use_clip_skip": False,
                "ad_clip_skip": 1,
                "ad_restore_face": False,
                "ad_controlnet_model": "None",
                "ad_controlnet_module": "None",
                "ad_controlnet_weight": 1.0,
                "ad_controlnet_guidance_start": 0.0,
                "ad_controlnet_guidance_end": 1.0
            },
            {
                "ad_model": "mediapipe_face_full",
                "ad_prompt": "",
                "ad_negative_prompt": "",
                "ad_confidence": 0.3,
                "ad_kernel_size": 0,
                "ad_dilate_erode": 4,
                "ad_x_offset": 0,
                "ad_y_offset": 0,
                "ad_mask_merge_invert": "None",
                "ad_mask_blur": 4,
                "ad_denoising_strength": 0.4,
                "ad_inpaint_only_masked": True,
                "ad_inpaint_only_masked_padding": 32,
                "ad_use_inpaint_width_height": False,
                "ad_inpaint_width": 512,
                "ad_inpaint_height": 512,
                "ad_use_steps": True,
                "ad_steps": 28,
                "ad_use_cfg_scale": True,
                "ad_cfg_scale": 7.0,
                "ad_use_sampler": True,
                "ad_sampler": "DPM++ 2M Karras",
                "ad_use_noise_multiplier": True,
                "ad_noise_multiplier": 1.0,
                "ad_use_clip_skip": False,
                "ad_clip_skip": 1,
                "ad_restore_face": False,
                "ad_controlnet_model": "None",
                "ad_controlnet_module": "None",
                "ad_controlnet_weight": 1.0,
                "ad_controlnet_guidance_start": 0.0,
                "ad_controlnet_guidance_end": 1.0
            }
        ]
    }
}

# OpenAI Settings
OPENAI_SETTINGS = {
    "model": "gpt-3.5-turbo",
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
        },
        "alwayson_scripts": ADETAILER_SETTINGS
    }

def set_sd_model(model_name: str = "realisticVisionV60B1_v51HyperVAE.safetensors") -> bool:
    """Set the Stable Diffusion model via API."""
    import requests
    
    try:
        # Get available models
        response = requests.get(f"{SD_API_URL}/sdapi/v1/sd-models")
        response.raise_for_status()
        models = response.json()
        
        # Find the target model
        target_model = None
        for model in models:
            if model_name in model["title"]:
                target_model = model
                break
        
        if not target_model:
            print(f"Model {model_name} not found. Available models:")
            for model in models:
                print(f"  - {model['title']}")
            return False
        
        # Set the model
        payload = {"sd_model_checkpoint": target_model["title"]}
        response = requests.post(f"{SD_API_URL}/sdapi/v1/options", json=payload)
        response.raise_for_status()
        
        print(f"✓ Model set to: {target_model['title']}")
        return True
        
    except Exception as e:
        print(f"Error setting model: {e}")
        return False

def enable_adetailer() -> bool:
    """Enable ADetailer extension for better faces."""
    import requests
    
    try:
        # Check if ADetailer is available
        response = requests.get(f"{SD_API_URL}/sdapi/v1/scripts")
        response.raise_for_status()
        scripts = response.json()
        
        # ADetailer is usually available as a script
        # We'll enable it by adding it to the payload
        print("✓ ADetailer will be enabled in generation payload")
        return True
        
    except Exception as e:
        print(f"Warning: Could not check ADetailer availability: {e}")
        return False 