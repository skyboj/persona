#!/usr/bin/env python3
"""
AI Persona Image Generator
Automates generation of unique, realistic images for organizational administrators.
"""

import json
import sqlite3
import requests
import base64
import os
import argparse
import time
from typing import Dict, Tuple, Optional
from openai import OpenAI
from PIL import Image
import io

# Import configuration
from config import (
    OPENAI_API_KEY, SD_API_URL, SD_MODEL_CHECKPOINT, INPUT_JSON_FILE, 
    OUTPUT_DIR, DATABASE_FILE, OPENAI_SETTINGS, PROCESSING_SETTINGS, 
    validate_config, get_sd_payload, set_sd_model, enable_adetailer
)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def setup_database() -> None:
    """Initialize SQLite database and create admin_profiles table."""
    print("Setting up database...")
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            json_source_file TEXT NOT NULL,
            category TEXT,
            subcategory TEXT,
            admin_id INTEGER UNIQUE,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            phone_number TEXT,
            organization_name TEXT,
            organization_town TEXT,
            languages TEXT,
            positive_prompt TEXT,
            negative_prompt TEXT,
            image_path TEXT,
            prompt_generated INTEGER DEFAULT 0,
            image_generated INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database '{DATABASE_FILE}' initialized successfully.")

def parse_json_to_db() -> None:
    """Parse JSON files from data directory and store administrator data in database."""
    print("Scanning data directory for JSON files...")
    
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"Error: {data_dir} directory not found!")
        print("Please create a 'data' directory with your JSON files organized by categories.")
        return
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    total_processed = 0
    total_skipped = 0
    files_processed = 0
    
    # Walk through the data directory
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                
                # Extract category and subcategory from path
                relative_path = os.path.relpath(file_path, data_dir)
                path_parts = relative_path.split(os.sep)
                
                print(f"DEBUG: relative_path = {relative_path}")
                print(f"DEBUG: path_parts = {path_parts}")
                
                if len(path_parts) >= 2:
                    category = path_parts[0]  # First directory is category
                    # If there's a filename, the second part is subcategory
                    if len(path_parts) >= 2:
                        subcategory = path_parts[1] if not path_parts[1].endswith('.json') else None
                    else:
                        subcategory = None
                else:
                    category = "uncategorized"
                    subcategory = None
                
                print(f"\nProcessing: {file_path}")
                print(f"Category: {category}, Subcategory: {subcategory}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if not isinstance(data, list):
                        print(f"Warning: {file_path} does not contain a list, skipping...")
                        continue
                    
                    file_processed = 0
                    file_skipped = 0
                    
                    for item in data:
                        try:
                            # Extract data from nested structure
                            prv = item.get('prv', {})
                            org = prv.get('org', {})
                            admin = org.get('admin', {})
                            contacts = admin.get('contacts', {})
                            org_contacts = org.get('contacts', {})
                            address = org_contacts.get('address', {})
                            
                            admin_id = admin.get('id')
                            if not admin_id:
                                continue
                            
                            # Check if admin already exists (considering category/subcategory)
                            cursor.execute("""
                                SELECT id FROM admin_profiles 
                                WHERE admin_id = ? AND category = ? AND subcategory = ?
                            """, (admin_id, category, subcategory))
                            
                            if cursor.fetchone():
                                file_skipped += 1
                                continue
                            
                            # Extract all required fields
                            first_name = admin.get('fname', '')
                            last_name = admin.get('sname', '')
                            email = contacts.get('email', '')
                            phone_number = contacts.get('phoneNumber', '')
                            organization_name = org.get('name', '')
                            organization_town = address.get('town', '')
                            
                            # Handle languages list
                            langs = org.get('langs', [])
                            languages = ", ".join(langs) if isinstance(langs, list) else str(langs)
                            
                            # Insert into database with category information
                            cursor.execute('''
                                INSERT INTO admin_profiles 
                                (json_source_file, category, subcategory, admin_id, first_name, last_name, 
                                 email, phone_number, organization_name, organization_town, languages)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (file_path, category, subcategory, admin_id, first_name, last_name, 
                                  email, phone_number, organization_name, organization_town, languages))
                            
                            file_processed += 1
                            
                        except Exception as e:
                            print(f"Error processing item in {file_path}: {e}")
                            continue
                    
                    total_processed += file_processed
                    total_skipped += file_skipped
                    files_processed += 1
                    
                    print(f"✓ Processed: {file_processed}, Skipped: {file_skipped}")
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON in {file_path}: {e}")
                    continue
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
                    continue
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*50}")
    print(f"JSON parsing complete!")
    print(f"Files processed: {files_processed}")
    print(f"Total profiles processed: {total_processed}")
    print(f"Total profiles skipped: {total_skipped}")
    print(f"{'='*50}")

def generate_openai_prompt(profile_data: Dict) -> Tuple[str, str]:
    """Generate positive and negative prompts using OpenAI."""
    
    system_prompt = """You are an expert prompt engineer specializing in Stable Diffusion, specifically for the realisticVisionV60B1_v51HyperVAE model. This model excels at creating highly realistic, professional portraits with exceptional detail and natural skin textures.

CRITICAL MODEL-SPECIFIC GUIDELINES:
- realisticVisionV60B1_v51HyperVAE is optimized for photorealistic human portraits
- Use RAW photo, photorealistic, masterpiece, high-detail, sharp focus, 8k uhd tags
- Include professional photography terms: studio lighting, crisp, ultra-detailed, Canon EOS R5
- Emphasize natural skin textures and realistic facial features
- Avoid over-processed or artificial-looking descriptions

STABLE DIFFUSION BEST PRACTICES:
- Start prompts with quality modifiers: (RAW photo, photorealistic, masterpiece, high-detail, sharp focus, 8k uhd:1.2)
- Use weighted terms with colons: (professional lighting:1.1), (natural skin texture:1.3)
- Include camera and lens specifications for realism
- Specify lighting conditions: natural lighting, studio lighting, soft lighting
- Add professional photography context: photographed by professional photographer

NEGATIVE PROMPT ESSENTIALS:
- Always include: (worst quality, low quality, normal quality:1.4)
- Exclude: (deformed, distorted, disfigured:1.3), ugly, blurry, bad anatomy
- Avoid: cartoon, anime, painting, illustration, drawing, sketch
- Prevent: (unrealistic, fake, artificial), (retouched, perfect skin, flawless)
- Block: text, signature, watermark, username, artist name

Your task is to create detailed Stable Diffusion prompts that will generate high-quality, realistic images of professional administrators in business or academic settings.

Focus on:
- Professional attire and demeanor appropriate for the organization type
- Realistic business or academic backgrounds
- High-quality photographic elements and lighting
- Natural, professional expressions
- Appropriate professional settings (modern office, university campus, clean workspace)

Output your response in exactly this format:
Positive Prompt: [Your detailed positive prompt here]
Negative Prompt: [Your detailed negative prompt here]"""

    user_message = f"""Create a Stable Diffusion prompt optimized for realisticVisionV60B1_v51HyperVAE model for a professional administrator portrait.

Administrator Details:
- Name: {profile_data.get('first_name', '')} {profile_data.get('last_name', '')}
- Organization: {profile_data.get('organization_name', '')}
- Location: {profile_data.get('organization_town', '')}
- Languages: {profile_data.get('languages', '')}

Generate a positive prompt that:
1. Starts with quality modifiers for realisticVisionV60B1_v51HyperVAE
2. Describes a professional-looking person in appropriate business attire
3. Includes realistic professional environment details
4. Uses professional photography terminology
5. Emphasizes natural, realistic appearance

Generate a negative prompt that excludes:
1. Common quality issues and artifacts
2. Inappropriate or unprofessional elements
3. Artificial or over-processed appearances
4. Cartoon/anime styles
5. Text, watermarks, and signatures"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_SETTINGS["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=OPENAI_SETTINGS["temperature"],
            max_tokens=OPENAI_SETTINGS["max_tokens"]
        )
        
        content = response.choices[0].message.content
        
        # Parse the response to extract positive and negative prompts
        lines = content.split('\n')
        positive_prompt = ""
        negative_prompt = ""
        
        for line in lines:
            if line.startswith("Positive Prompt:"):
                positive_prompt = line.replace("Positive Prompt:", "").strip()
            elif line.startswith("Negative Prompt:"):
                negative_prompt = line.replace("Negative Prompt:", "").strip()
        
        # Add model-specific quality enhancements to positive prompt
        if positive_prompt:
            # Don't add duplicate quality modifiers if they're already in the prompt
            if "RAW photo" not in positive_prompt:
                positive_prompt = "(RAW photo, photorealistic, masterpiece, high-detail, sharp focus, 8k uhd:1.2), " + positive_prompt
            
            if "studio lighting" not in positive_prompt:
                positive_prompt += ", studio lighting, crisp, 8k, ultra-detailed, Canon EOS R5, award-winning photography"
        
        # Add standard negative prompt elements if not already present
        if negative_prompt:
            if "worst quality" not in negative_prompt:
                negative_prompt += ", (worst quality, low quality, normal quality:1.4)"
            
            if "deformed" not in negative_prompt:
                negative_prompt += ", (deformed, distorted, disfigured:1.3), ugly, blurry, bad anatomy, mutation, extra limbs, out of frame"
            
            if "cartoon" not in negative_prompt:
                negative_prompt += ", plastic, 3d, cgi, render, octane render, cartoon, anime, painting, illustration, drawing, sketch"
            
            if "unrealistic" not in negative_prompt:
                negative_prompt += ", (unrealistic, fake, artificial), (retouched, perfect skin, flawless, smooth skin)"
            
            if "text" not in negative_prompt:
                negative_prompt += ", text, signature, watermark, username, artist name"
        
        return positive_prompt, negative_prompt
        
    except Exception as e:
        print(f"Error generating OpenAI prompt: {e}")
        return "", ""

def process_prompts_from_db(limit: Optional[int] = None, start_from: int = 1, dry_run: bool = False) -> None:
    """Generate prompts for all profiles that don't have prompts yet."""
    print("Generating prompts for profiles...")
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Get all profiles without prompts, starting from specified ID
    cursor.execute("""
        SELECT id, first_name, last_name, company_name, city
        FROM admin_profiles 
        WHERE prompt_generated = 0 AND id >= ?
        ORDER BY id
    """, (start_from,))
    
    profiles = cursor.fetchall()
    
    if limit:
        profiles = profiles[:limit]
        print(f"Found {len(profiles)} profiles needing prompts (limited to {limit})")
    else:
        print(f"Found {len(profiles)} profiles needing prompts")
    
    if dry_run:
        print("DRY RUN - Would generate prompts for:")
        for profile in profiles:
            profile_id, first_name, last_name, company_name, city = profile
            print(f"  ID {profile_id}: {first_name} {last_name} from {company_name}")
        return
    
    for profile in profiles:
        profile_id, first_name, last_name, company_name, city = profile
        
        print(f"Generating prompt for {first_name} {last_name} (ID: {profile_id})...")
        
        profile_data = {
            'first_name': first_name,
            'last_name': last_name,
            'organization_name': company_name,
            'organization_town': city
        }
        
        positive_prompt, negative_prompt = generate_openai_prompt(profile_data)
        
        if positive_prompt and negative_prompt:
            cursor.execute("""
                UPDATE admin_profiles 
                SET positive_prompt = ?, negative_prompt = ?, prompt_generated = 1
                WHERE id = ?
            """, (positive_prompt, negative_prompt, profile_id))
            
            print(f"✓ Prompt generated for {first_name} {last_name}")
        else:
            print(f"✗ Failed to generate prompt for {first_name} {last_name}")
        
        # Small delay to avoid rate limiting
        time.sleep(PROCESSING_SETTINGS["prompt_delay"])
    
    conn.commit()
    conn.close()
    print("Prompt generation complete.")

def generate_image_with_sd(positive_prompt: str, negative_prompt: str, output_path: str, sd_model_name: str) -> bool:
    """Generate image using Stable Diffusion API."""
    
    payload = get_sd_payload(positive_prompt, negative_prompt)
    
    try:
        response = requests.post(f"{SD_API_URL}/sdapi/v1/txt2img", json=payload, timeout=PROCESSING_SETTINGS["timeout"])
        response.raise_for_status()
        
        r = response.json()
        
        # Decode and save image
        image_data = base64.b64decode(r['images'][0])
        image = Image.open(io.BytesIO(image_data))
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save image to the specified path
        image.save(output_path)
        
        print(f"✓ Image saved: {output_path}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Stable Diffusion API: {e}")
        return False
    except Exception as e:
        print(f"Error generating image: {e}")
        return False

def process_images_from_db(limit: Optional[int] = None, start_from: int = 1, dry_run: bool = False) -> None:
    """Generate images for all profiles that have prompts but no images."""
    print("Generating images for profiles...")
    
    # Setup SD model and extensions
    print("Setting up Stable Diffusion...")
    if not set_sd_model():
        print("Warning: Could not set SD model, continuing with current model")
    
    enable_adetailer()
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Get all profiles with prompts but no images, starting from specified ID
    cursor.execute("""
        SELECT id, admin_id, first_name, last_name, positive_prompt, negative_prompt, category, subcategory
        FROM admin_profiles 
        WHERE prompt_generated = 1 AND image_generated = 0 AND id >= ?
        ORDER BY id
    """, (start_from,))
    
    profiles = cursor.fetchall()
    
    if limit:
        profiles = profiles[:limit]
        print(f"Found {len(profiles)} profiles needing images (limited to {limit})")
    else:
        print(f"Found {len(profiles)} profiles needing images")
    
    if dry_run:
        print("DRY RUN - Would generate images for:")
        for profile in profiles:
            profile_id, admin_id, first_name, last_name, positive_prompt, negative_prompt, category, subcategory = profile
            print(f"  ID {profile_id}: {first_name} {last_name} from {category}/{subcategory}")
        return
    
    for profile in profiles:
        profile_id, admin_id, first_name, last_name, positive_prompt, negative_prompt, category, subcategory = profile
        
        print(f"Generating image for {first_name} {last_name} (ID: {profile_id})...")
        
        # Create unique filename
        safe_first_name = "".join(c for c in first_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_last_name = "".join(c for c in last_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        output_filename = f"admin_{admin_id}_{safe_first_name}_{safe_last_name}.png"
        
        # New folder structure: generated_images/{category}/{subcategory}/
        subcat_folder = subcategory if subcategory else "no_subcategory"
        output_dir = os.path.join(OUTPUT_DIR, category, subcat_folder)
        output_path = os.path.join(output_dir, output_filename)
        
        success = generate_image_with_sd(
            positive_prompt, 
            negative_prompt, 
            output_path, 
            SD_MODEL_CHECKPOINT
        )
        
        if success:
            cursor.execute("""
                UPDATE admin_profiles 
                SET image_path = ?, image_generated = 1
                WHERE id = ?
            """, (output_path, profile_id))
            
            print(f"✓ Image generated for {first_name} {last_name}")
        else:
            print(f"✗ Failed to generate image for {first_name} {last_name}")
        
        # Small delay between generations
        time.sleep(PROCESSING_SETTINGS["image_delay"])
    
    conn.commit()
    conn.close()
    print("Image generation complete.")

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='AI Persona Image Generator')
    parser.add_argument('--parse-json', action='store_true', help='Just parse JSON into DB')
    parser.add_argument('--generate-prompts', action='store_true', help='Generate prompts for profiles without prompts')
    parser.add_argument('--generate-images', action='store_true', help='Generate images for profiles with prompts but no images')
    parser.add_argument('--all', action='store_true', help='Run all steps sequentially')
    parser.add_argument('--validate', action='store_true', help='Validate configuration')
    
    # New arguments for controlling generation count
    parser.add_argument('--limit-prompts', type=int, help='Limit number of prompts to generate')
    parser.add_argument('--limit-images', type=int, help='Limit number of images to generate')
    parser.add_argument('--start-from', type=int, default=1, help='Start from profile ID (default: 1)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be generated without actually doing it')
    
    args = parser.parse_args()
    
    if args.validate:
        if validate_config():
            print("Configuration is valid!")
        else:
            print("Configuration validation failed!")
        return
    
    if args.parse_json:
        setup_database()
        parse_json_to_db()
    elif args.generate_prompts:
        process_prompts_from_db(args.limit_prompts, args.start_from, args.dry_run)
    elif args.generate_images:
        process_images_from_db(args.limit_images, args.start_from, args.dry_run)
    elif args.all:
        print("Running complete AI Persona Image Generator pipeline...")
        setup_database()
        parse_json_to_db()
        process_prompts_from_db(args.limit_prompts, args.start_from, args.dry_run)
        process_images_from_db(args.limit_images, args.start_from, args.dry_run)
        print("Pipeline complete!")
    else:
        print("Please specify an action. Use --help for options.")

if __name__ == "__main__":
    main() 