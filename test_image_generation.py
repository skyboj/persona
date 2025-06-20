#!/usr/bin/env python3
"""
Test image generation for AI Persona Image Generator
Creates test images without using Stable Diffusion API
"""

import os
import sqlite3
from PIL import Image, ImageDraw, ImageFont
import random

# Database configuration
DATABASE_FILE = "profiles.db"
OUTPUT_DIR = "generated_images"

def create_test_image(output_path: str, profile_name: str) -> bool:
    """Create a simple test image with profile name."""
    try:
        # Create a simple image
        width, height = 512, 512
        image = Image.new('RGB', (width, height), color=(random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)))
        
        # Add some text
        draw = ImageDraw.Draw(image)
        
        # Try to use a default font, fallback to basic if not available
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Add profile name
        text = f"Test Image\n{profile_name}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill=(0, 0, 0), font=font)
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save image
        image.save(output_path)
        print(f"✓ Test image created: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error creating test image: {e}")
        return False

def generate_test_images_for_profiles() -> None:
    """Generate test images for profiles that have prompts but no images."""
    print("Generating test images for profiles...")
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Get all profiles with prompts but no images
    cursor.execute("""
        SELECT id, admin_id, first_name, last_name, category, subcategory
        FROM admin_profiles 
        WHERE prompt_generated = 1 AND image_generated = 0
        LIMIT 3
    """)
    
    profiles = cursor.fetchall()
    print(f"Found {len(profiles)} profiles for test image generation")
    
    for profile in profiles:
        profile_id, admin_id, first_name, last_name, category, subcategory = profile
        
        print(f"Generating test image for {first_name} {last_name}...")
        
        # Create unique filename
        safe_first_name = "".join(c for c in first_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_last_name = "".join(c for c in last_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        output_filename = f"test_admin_{admin_id}_{safe_first_name}_{safe_last_name}.png"
        
        # Create folder structure: generated_images/{category}/{subcategory}/
        subcat_folder = subcategory if subcategory else "no_subcategory"
        output_dir = os.path.join(OUTPUT_DIR, category, subcat_folder)
        output_path = os.path.join(output_dir, output_filename)
        
        success = create_test_image(output_path, f"{first_name} {last_name}")
        
        if success:
            cursor.execute("""
                UPDATE admin_profiles 
                SET image_path = ?, image_generated = 1
                WHERE id = ?
            """, (output_path, profile_id))
            
            print(f"✓ Test image generated and path saved for {first_name} {last_name}")
        else:
            print(f"✗ Failed to generate test image for {first_name} {last_name}")
    
    conn.commit()
    conn.close()
    print("Test image generation complete.")

def main():
    """Main function for test image generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate test images for AI Persona Image Generator')
    parser.add_argument('--generate', action='store_true', help='Generate test images for profiles with prompts but no images')
    
    args = parser.parse_args()
    
    if args.generate:
        generate_test_images_for_profiles()
    else:
        print("Please specify an action. Use --help for options.")
        print("\nAvailable commands:")
        print("  --generate           Generate test images for profiles")

if __name__ == "__main__":
    main() 