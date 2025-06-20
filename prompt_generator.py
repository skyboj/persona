#!/usr/bin/env python3
"""
Prompt generator for AI Persona Image Generator
Uses OpenAI GPT API to generate personalized prompts based on profile data
"""

import os
import sqlite3
import openai
from typing import List, Tuple, Dict, Any, Optional
import json
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_FILE = "profiles.db"

# Prompt templates
POSITIVE_PROMPT_TEMPLATE = """(RAW photo, photorealistic, masterpiece, high-detail, sharp focus, 8k uhd:1.2), (photographed by a professional photographer), (natural skin texture),
{professional photo|shot on iphone|selfie|{old|vintage|faded} selfie}, a portrait of a {18-25|24-35|30-40|40-50|50-60} year old woman, ({smile|slight smile|serious expression|tired expression}:1.1),
(natural lighting), (subtle background)"""

NEGATIVE_PROMPT_TEMPLATE = """(worst quality, low quality, normal quality:1.4), (monochrome, grayscale), (deformed, distorted, disfigured:1.3), ugly, blurry, bad anatomy, mutation, extra limbs, out of frame, plastic, 3d, cgi, render, octane render, cartoon, anime, painting, illustration, drawing, sketch, (unrealistic, fake, artificial), (retouched, perfect skin, flawless, smooth skin), (glamour, fashion, makeup, jewelry), text, signature, watermark, username, artist name"""

def setup_openai_api() -> None:
    """Setup OpenAI API key from environment variable."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    openai.api_key = api_key

def get_profile_data(profile_id: int) -> Optional[Dict[str, Any]]:
    """Get profile data from database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, company_id, company_name, admin_id, first_name, last_name, 
               city, category, subcategory
        FROM admin_profiles 
        WHERE id = ?
    """, (profile_id,))
    
    profile = cursor.fetchone()
    conn.close()
    
    if not profile:
        return None
    
    return {
        'id': profile[0],
        'company_id': profile[1],
        'company_name': profile[2],
        'admin_id': profile[3],
        'first_name': profile[4],
        'last_name': profile[5],
        'city': profile[6],
        'category': profile[7],
        'subcategory': profile[8]
    }

def generate_prompt_with_gpt(profile_data: Dict[str, Any]) -> Tuple[str, str]:
    """Generate personalized prompts using GPT API."""
    
    # Create context for GPT
    context = f"""
    Generate a personalized Stable Diffusion prompt for a professional portrait photo.
    
    Profile Information:
    - Name: {profile_data['first_name']} {profile_data['last_name']}
    - Company: {profile_data['company_name']}
    - City: {profile_data['city']}
    - Category: {profile_data['category']}
    - Subcategory: {profile_data['subcategory']}
    
    Base Positive Prompt Template:
    {POSITIVE_PROMPT_TEMPLATE}
    
    Base Negative Prompt Template:
    {NEGATIVE_PROMPT_TEMPLATE}
    
    Instructions:
    1. For the positive prompt, replace the placeholders in curly braces with appropriate choices based on the profile context
    2. Choose age range that fits the professional context (likely 24-35 or 30-40 for business professionals)
    3. Choose expression that fits the professional context (likely slight smile or serious expression)
    4. Choose photo style that fits the professional context (likely professional photo)
    5. The negative prompt should remain exactly as provided - do not modify it
    6. Return only the final prompts, no explanations
    
    Return the prompts in this exact format:
    POSITIVE: [your positive prompt here]
    NEGATIVE: [your negative prompt here]
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional prompt engineer for Stable Diffusion. You create precise, effective prompts for generating realistic professional portraits."},
                {"role": "user", "content": context}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse the response
        lines = result.split('\n')
        positive_prompt = ""
        negative_prompt = ""
        
        for line in lines:
            if line.startswith('POSITIVE:'):
                positive_prompt = line.replace('POSITIVE:', '').strip()
            elif line.startswith('NEGATIVE:'):
                negative_prompt = line.replace('NEGATIVE:', '').strip()
        
        if not positive_prompt or not negative_prompt:
            # Fallback to template if parsing fails
            positive_prompt = POSITIVE_PROMPT_TEMPLATE.replace('{professional photo|shot on iphone|selfie|{old|vintage|faded} selfie}', 'professional photo').replace('{18-25|24-35|30-40|40-50|50-60}', '24-35').replace('{smile|slight smile|serious expression|tired expression}', 'slight smile')
            negative_prompt = NEGATIVE_PROMPT_TEMPLATE
        
        return positive_prompt, negative_prompt
        
    except Exception as e:
        print(f"Error generating prompt with GPT: {e}")
        # Fallback to template
        positive_prompt = POSITIVE_PROMPT_TEMPLATE.replace('{professional photo|shot on iphone|selfie|{old|vintage|faded} selfie}', 'professional photo').replace('{18-25|24-35|30-40|40-50|50-60}', '24-35').replace('{smile|slight smile|serious expression|tired expression}', 'slight smile')
        negative_prompt = NEGATIVE_PROMPT_TEMPLATE
        return positive_prompt, negative_prompt

def save_prompts_to_database(profile_id: int, positive_prompt: str, negative_prompt: str) -> bool:
    """Save generated prompts to database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE admin_profiles 
            SET positive_prompt = ?, negative_prompt = ?, prompt_generated = 1, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (positive_prompt, negative_prompt, profile_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
        
    except Exception as e:
        print(f"Error saving prompts to database: {e}")
        conn.close()
        return False

def generate_prompts_for_profile(profile_id: int) -> bool:
    """Generate prompts for a specific profile."""
    print(f"Generating prompts for profile ID: {profile_id}")
    
    # Get profile data
    profile_data = get_profile_data(profile_id)
    if not profile_data:
        print(f"Profile with ID {profile_id} not found.")
        return False
    
    print(f"Processing: {profile_data['first_name']} {profile_data['last_name']} from {profile_data['company_name']}")
    
    # Generate prompts
    positive_prompt, negative_prompt = generate_prompt_with_gpt(profile_data)
    
    # Save to database
    success = save_prompts_to_database(profile_id, positive_prompt, negative_prompt)
    
    if success:
        print(f"✓ Prompts generated and saved for {profile_data['first_name']} {profile_data['last_name']}")
        print(f"  Positive: {positive_prompt[:100]}...")
        print(f"  Negative: {negative_prompt[:100]}...")
    else:
        print(f"✗ Failed to save prompts for {profile_data['first_name']} {profile_data['last_name']}")
    
    return success

def generate_prompts_for_category(category: str, subcategory: str = None) -> None:
    """Generate prompts for all profiles in a category/subcategory."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    if subcategory:
        cursor.execute("""
            SELECT id FROM admin_profiles 
            WHERE category = ? AND subcategory = ? AND prompt_generated = 0
            ORDER BY id
        """, (category, subcategory))
        filter_desc = f"Category: {category}, Subcategory: {subcategory}"
    else:
        cursor.execute("""
            SELECT id FROM admin_profiles 
            WHERE category = ? AND prompt_generated = 0
            ORDER BY id
        """, (category,))
        filter_desc = f"Category: {category}"
    
    profile_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not profile_ids:
        print(f"No profiles found for {filter_desc} that need prompts.")
        return
    
    print(f"Found {len(profile_ids)} profiles for {filter_desc} that need prompts.")
    
    success_count = 0
    for i, profile_id in enumerate(profile_ids, 1):
        print(f"\n[{i}/{len(profile_ids)}] ", end="")
        if generate_prompts_for_profile(profile_id):
            success_count += 1
        
        # Add delay to avoid rate limiting
        if i < len(profile_ids):
            time.sleep(1)
    
    print(f"\nCompleted! {success_count}/{len(profile_ids)} prompts generated successfully.")

def generate_prompts_for_all() -> None:
    """Generate prompts for all profiles that don't have them."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id FROM admin_profiles 
        WHERE prompt_generated = 0
        ORDER BY category, subcategory, id
    """)
    
    profile_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not profile_ids:
        print("No profiles found that need prompts.")
        return
    
    print(f"Found {len(profile_ids)} profiles that need prompts.")
    
    success_count = 0
    for i, profile_id in enumerate(profile_ids, 1):
        print(f"\n[{i}/{len(profile_ids)}] ", end="")
        if generate_prompts_for_profile(profile_id):
            success_count += 1
        
        # Add delay to avoid rate limiting
        if i < len(profile_ids):
            time.sleep(1)
    
    print(f"\nCompleted! {success_count}/{len(profile_ids)} prompts generated successfully.")

def main():
    """Main function for prompt generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate prompts for AI Persona Image Generator')
    parser.add_argument('--profile-id', type=int, help='Generate prompts for specific profile ID')
    parser.add_argument('--category', type=str, help='Generate prompts for all profiles in category')
    parser.add_argument('--subcategory', type=str, help='Generate prompts for all profiles in category/subcategory')
    parser.add_argument('--all', action='store_true', help='Generate prompts for all profiles that need them')
    
    args = parser.parse_args()
    
    try:
        setup_openai_api()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set the OPENAI_API_KEY environment variable.")
        return
    
    if args.profile_id:
        generate_prompts_for_profile(args.profile_id)
    elif args.category and args.subcategory:
        generate_prompts_for_category(args.category, args.subcategory)
    elif args.category:
        generate_prompts_for_category(args.category)
    elif args.all:
        generate_prompts_for_all()
    else:
        print("Please specify an action. Use --help for options.")
        print("\nAvailable commands:")
        print("  --profile-id ID      Generate prompts for specific profile ID")
        print("  --category CAT       Generate prompts for all profiles in category")
        print("  --subcategory CAT SUB Generate prompts for all profiles in category/subcategory")
        print("  --all                Generate prompts for all profiles that need them")

if __name__ == "__main__":
    main() 