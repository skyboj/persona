#!/usr/bin/env python3
"""
Test prompt generator for AI Persona Image Generator
Uses template-based prompts without GPT API for testing
"""

import os
import sqlite3
import random
from typing import List, Tuple, Dict, Any, Optional
import json
import time

# Database configuration
DATABASE_FILE = "profiles.db"

# Prompt templates
POSITIVE_PROMPT_TEMPLATE = """(RAW photo, photorealistic, masterpiece, high-detail, sharp focus, 8k uhd:1.2), (photographed by a professional photographer), (natural skin texture),
{professional photo|shot on iphone|selfie|{old|vintage|faded} selfie}, a portrait of a {18-25|24-35|30-40|40-50|50-60} year old woman, ({smile|slight smile|serious expression|tired expression}:1.1),
(natural lighting), (subtle background)"""

NEGATIVE_PROMPT_TEMPLATE = """(worst quality, low quality, normal quality:1.4), (monochrome, grayscale), (deformed, distorted, disfigured:1.3), ugly, blurry, bad anatomy, mutation, extra limbs, out of frame, plastic, 3d, cgi, render, octane render, cartoon, anime, painting, illustration, drawing, sketch, (unrealistic, fake, artificial), (retouched, perfect skin, flawless, smooth skin), (glamour, fashion, makeup, jewelry), text, signature, watermark, username, artist name"""

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

def generate_prompt_from_template(profile_data: Dict[str, Any]) -> Tuple[str, str]:
    """Generate personalized prompts using template with smart choices."""
    
    # Smart choices based on profile context
    photo_style_choices = ["professional photo", "shot on iphone", "selfie", "old selfie", "vintage selfie", "faded selfie"]
    age_choices = ["18-25", "24-35", "30-40", "40-50", "50-60"]
    expression_choices = ["smile", "slight smile", "serious expression", "tired expression"]
    
    # Choose based on professional context
    photo_style = "professional photo"  # Most appropriate for business profiles
    age = random.choice(["24-35", "30-40"])  # Professional age range
    expression = random.choice(["slight smile", "serious expression"])  # Professional expressions
    
    # Generate positive prompt
    positive_prompt = POSITIVE_PROMPT_TEMPLATE.replace(
        "{professional photo|shot on iphone|selfie|{old|vintage|faded} selfie}", 
        photo_style
    ).replace(
        "{18-25|24-35|30-40|40-50|50-60}", 
        age
    ).replace(
        "{smile|slight smile|serious expression|tired expression}", 
        expression
    )
    
    # Negative prompt stays the same
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
    positive_prompt, negative_prompt = generate_prompt_from_template(profile_data)
    
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
        
        # Add small delay
        if i < len(profile_ids):
            time.sleep(0.1)
    
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
        
        # Add small delay
        if i < len(profile_ids):
            time.sleep(0.1)
    
    print(f"\nCompleted! {success_count}/{len(profile_ids)} prompts generated successfully.")

def main():
    """Main function for prompt generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate prompts for AI Persona Image Generator (Test Version)')
    parser.add_argument('--profile-id', type=int, help='Generate prompts for specific profile ID')
    parser.add_argument('--category', type=str, help='Generate prompts for all profiles in category')
    parser.add_argument('--subcategory', type=str, help='Generate prompts for all profiles in category/subcategory')
    parser.add_argument('--all', action='store_true', help='Generate prompts for all profiles that need them')
    parser.add_argument('--test', action='store_true', help='Test with first 5 profiles')
    
    args = parser.parse_args()
    
    if args.profile_id:
        generate_prompts_for_profile(args.profile_id)
    elif args.category and args.subcategory:
        generate_prompts_for_category(args.category, args.subcategory)
    elif args.category:
        generate_prompts_for_category(args.category)
    elif args.all:
        generate_prompts_for_all()
    elif args.test:
        print("Testing with first 5 profiles...")
        for i in range(1, 6):
            generate_prompts_for_profile(i)
    else:
        print("Please specify an action. Use --help for options.")
        print("\nAvailable commands:")
        print("  --profile-id ID      Generate prompts for specific profile ID")
        print("  --category CAT       Generate prompts for all profiles in category")
        print("  --subcategory CAT SUB Generate prompts for all profiles in category/subcategory")
        print("  --all                Generate prompts for all profiles that need them")
        print("  --test               Test with first 5 profiles")

if __name__ == "__main__":
    main() 