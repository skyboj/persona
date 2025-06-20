#!/usr/bin/env python3
"""
Database utility functions for AI Persona Image Generator
"""

import sqlite3
import argparse
import json
import os
from typing import List, Tuple, Dict, Any

DATABASE_FILE = "profiles.db"

def create_database() -> None:
    """Create the database and tables."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Drop existing table if it exists
    cursor.execute("DROP TABLE IF EXISTS admin_profiles")
    
    cursor.execute("""
        CREATE TABLE admin_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            company_name TEXT NOT NULL,
            admin_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            city TEXT,
            category TEXT NOT NULL,
            subcategory TEXT NOT NULL,
            prompt_generated BOOLEAN DEFAULT 0,
            image_generated BOOLEAN DEFAULT 0,
            positive_prompt TEXT,
            negative_prompt TEXT,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database created successfully.")

def recreate_database() -> None:
    """Recreate the database (drop and create tables)."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Drop existing table
    cursor.execute("DROP TABLE IF EXISTS admin_profiles")
    
    # Create new table
    cursor.execute("""
        CREATE TABLE admin_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            company_name TEXT NOT NULL,
            admin_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            city TEXT,
            category TEXT NOT NULL,
            subcategory TEXT NOT NULL,
            prompt_generated BOOLEAN DEFAULT 0,
            image_generated BOOLEAN DEFAULT 0,
            positive_prompt TEXT,
            negative_prompt TEXT,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database recreated successfully.")

def scan_and_import_json_files(data_dir: str = "data") -> None:
    """Scan JSON files in data directory and import them to database."""
    if not os.path.exists(data_dir):
        print(f"Data directory '{data_dir}' not found!")
        return
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Ensure table exists
    create_database()
    
    total_imported = 0
    total_skipped = 0
    
    # Scan categories (folders)
    for category in os.listdir(data_dir):
        category_path = os.path.join(data_dir, category)
        
        if not os.path.isdir(category_path):
            continue
            
        print(f"\nScanning category: {category}")
        
        # Scan JSON files in category
        for filename in os.listdir(category_path):
            if not filename.endswith('.json'):
                continue
                
            subcategory = filename.replace('.json', '')
            file_path = os.path.join(category_path, filename)
            
            print(f"  Processing: {subcategory}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Process each organization in the JSON file
                for org_data in data:
                    if 'prv' in org_data and 'org' in org_data['prv']:
                        org = org_data['prv']['org']
                        
                        # Extract data
                        company_name = org.get('name', 'Unknown')
                        admin = org.get('admin', {})
                        admin_id = admin.get('id', 0)
                        first_name = admin.get('fname', 'Unknown')
                        last_name = admin.get('sname', 'Unknown')
                        
                        # Extract city from contacts.address.town
                        city = 'Unknown'
                        if 'contacts' in org and 'address' in org['contacts']:
                            city = org['contacts']['address'].get('town', 'Unknown')
                        
                        # Generate company_id (you might want to extract this from somewhere else)
                        company_id = admin_id  # Using admin_id as company_id for now
                        
                        # Check if this admin already exists
                        cursor.execute("""
                            SELECT id FROM admin_profiles 
                            WHERE admin_id = ? AND category = ? AND subcategory = ?
                        """, (admin_id, category, subcategory))
                        
                        if cursor.fetchone():
                            print(f"    Skipped: {first_name} {last_name} (already exists)")
                            total_skipped += 1
                            continue
                        
                        # Insert new profile
                        cursor.execute("""
                            INSERT INTO admin_profiles 
                            (company_id, company_name, admin_id, first_name, last_name, city, category, subcategory)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (company_id, company_name, admin_id, first_name, last_name, city, category, subcategory))
                        
                        print(f"    Imported: {first_name} {last_name} from {company_name}")
                        total_imported += 1
                
            except Exception as e:
                print(f"    Error processing {filename}: {e}")
                continue
    
    conn.commit()
    conn.close()
    
    print(f"\nImport completed!")
    print(f"Total imported: {total_imported}")
    print(f"Total skipped: {total_skipped}")

def view_all_profiles() -> None:
    """Display all profiles in the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, company_id, admin_id, first_name, last_name, city, category, subcategory, company_name, 
               prompt_generated, image_generated
        FROM admin_profiles
        ORDER BY category, subcategory, id
    """)
    
    profiles = cursor.fetchall()
    
    if not profiles:
        print("No profiles found in database.")
        return
    
    print(f"\n{'ID':<4} {'Comp ID':<8} {'Admin ID':<8} {'Name':<20} {'City':<15} {'Category':<15} {'Subcategory':<15} {'Company':<25} {'Prompt':<7} {'Image':<6}")
    print("-" * 130)
    
    for profile in profiles:
        id_val, company_id, admin_id, first_name, last_name, city, category, subcategory, company_name, prompt_gen, image_gen = profile
        name = f"{first_name} {last_name}"
        prompt_status = "✓" if prompt_gen else "✗"
        image_status = "✓" if image_gen else "✗"
        subcat_display = subcategory if subcategory else "N/A"
        city_display = city if city else "N/A"
        
        print(f"{id_val:<4} {company_id:<8} {admin_id:<8} {name:<20} {city_display:<15} {category:<15} {subcat_display:<15} {company_name:<25} {prompt_status:<7} {image_status:<6}")
    
    conn.close()

def view_profiles_by_category(category: str = None, subcategory: str = None) -> None:
    """Display profiles filtered by category and/or subcategory."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    if category and subcategory:
        cursor.execute("""
            SELECT id, admin_id, first_name, last_name, organization_name, 
                   prompt_generated, image_generated
            FROM admin_profiles 
            WHERE category = ? AND subcategory = ?
            ORDER BY id
        """, (category, subcategory))
        filter_desc = f"Category: {category}, Subcategory: {subcategory}"
    elif category:
        cursor.execute("""
            SELECT id, admin_id, first_name, last_name, subcategory, organization_name, 
                   prompt_generated, image_generated
            FROM admin_profiles 
            WHERE category = ?
            ORDER BY subcategory, id
        """, (category,))
        filter_desc = f"Category: {category}"
    else:
        cursor.execute("""
            SELECT id, admin_id, first_name, last_name, category, subcategory, organization_name, 
                   prompt_generated, image_generated
            FROM admin_profiles
            ORDER BY category, subcategory, id
        """)
        filter_desc = "All profiles"
    
    profiles = cursor.fetchall()
    
    if not profiles:
        print(f"No profiles found for: {filter_desc}")
        return
    
    print(f"\nProfiles for: {filter_desc}")
    print(f"Total: {len(profiles)} profiles")
    print("-" * 80)
    
    for profile in profiles:
        if category and subcategory:
            id_val, admin_id, first_name, last_name, org_name, prompt_gen, image_gen = profile
            name = f"{first_name} {last_name}"
            prompt_status = "✓" if prompt_gen else "✗"
            image_status = "✓" if image_gen else "✗"
            print(f"{id_val:<4} {admin_id:<8} {name:<25} {org_name:<30} {prompt_status:<7} {image_status:<6}")
        elif category:
            id_val, admin_id, first_name, last_name, subcategory, org_name, prompt_gen, image_gen = profile
            name = f"{first_name} {last_name}"
            prompt_status = "✓" if prompt_gen else "✗"
            image_status = "✓" if image_gen else "✗"
            subcat_display = subcategory if subcategory else "N/A"
            print(f"{id_val:<4} {admin_id:<8} {name:<20} {subcat_display:<15} {org_name:<25} {prompt_status:<7} {image_status:<6}")
        else:
            id_val, admin_id, first_name, last_name, category, subcategory, org_name, prompt_gen, image_gen = profile
            name = f"{first_name} {last_name}"
            prompt_status = "✓" if prompt_gen else "✗"
            image_status = "✓" if image_gen else "✗"
            subcat_display = subcategory if subcategory else "N/A"
            print(f"{id_val:<4} {admin_id:<8} {name:<20} {category:<15} {subcat_display:<15} {org_name:<20} {prompt_status:<7} {image_status:<6}")
    
    conn.close()

def view_categories() -> None:
    """Display all categories and subcategories with profile counts."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT category, subcategory, COUNT(*) as count,
               SUM(prompt_generated) as prompts_generated,
               SUM(image_generated) as images_generated
        FROM admin_profiles
        GROUP BY category, subcategory
        ORDER BY category, subcategory
    """)
    
    results = cursor.fetchall()
    
    if not results:
        print("No categories found in database.")
        return
    
    print(f"\n{'Category':<20} {'Subcategory':<20} {'Total':<8} {'Prompts':<8} {'Images':<8}")
    print("-" * 70)
    
    for category, subcategory, count, prompts, images in results:
        subcat_display = subcategory if subcategory else "N/A"
        print(f"{category:<20} {subcat_display:<20} {count:<8} {prompts:<8} {images:<8}")
    
    conn.close()

def view_generation_status() -> None:
    """Display generation status summary with category breakdown."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Overall statistics
    cursor.execute("SELECT COUNT(*) FROM admin_profiles")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM admin_profiles WHERE prompt_generated = 1")
    with_prompts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM admin_profiles WHERE image_generated = 1")
    with_images = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM admin_profiles WHERE prompt_generated = 0")
    need_prompts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM admin_profiles WHERE prompt_generated = 1 AND image_generated = 0")
    need_images = cursor.fetchone()[0]
    
    print(f"\nOverall Generation Status:")
    print(f"{'='*30}")
    print(f"Total Profiles: {total}")
    print(f"With Prompts: {with_prompts}")
    print(f"With Images: {with_images}")
    print(f"Need Prompts: {need_prompts}")
    print(f"Need Images: {need_images}")
    
    if total > 0:
        prompt_percentage = (with_prompts / total) * 100
        image_percentage = (with_images / total) * 100
        print(f"\nOverall Progress:")
        print(f"Prompts: {prompt_percentage:.1f}%")
        print(f"Images: {image_percentage:.1f}%")
    
    # Category breakdown
    print(f"\nCategory Breakdown:")
    print(f"{'='*30}")
    cursor.execute("""
        SELECT category, COUNT(*) as total,
               SUM(prompt_generated) as prompts,
               SUM(image_generated) as images
        FROM admin_profiles
        GROUP BY category
        ORDER BY category
    """)
    
    categories = cursor.fetchall()
    for category, cat_total, cat_prompts, cat_images in categories:
        prompt_pct = (cat_prompts / cat_total * 100) if cat_total > 0 else 0
        image_pct = (cat_images / cat_total * 100) if cat_total > 0 else 0
        print(f"{category}: {cat_total} profiles, {prompt_pct:.1f}% prompts, {image_pct:.1f}% images")
    
    conn.close()

def view_image_paths() -> None:
    """Display all image paths in the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, first_name, last_name, category, subcategory, image_path, image_generated
        FROM admin_profiles
        WHERE image_generated = 1
        ORDER BY category, subcategory, id
    """)
    
    profiles = cursor.fetchall()
    
    if not profiles:
        print("No images found in database.")
        return
    
    print(f"\n{'ID':<4} {'Name':<25} {'Category':<15} {'Subcategory':<15} {'Image Path':<50}")
    print("-" * 120)
    
    for profile in profiles:
        id_val, first_name, last_name, category, subcategory, image_path, image_generated = profile
        name = f"{first_name} {last_name}"
        subcat_display = subcategory if subcategory else "N/A"
        path_display = image_path if image_path else "No path"
        
        # Truncate long paths for display
        if len(path_display) > 47:
            path_display = "..." + path_display[-44:]
        
        print(f"{id_val:<4} {name:<25} {category:<15} {subcat_display:<15} {path_display:<50}")
    
    conn.close()

def view_profile_details(profile_id: int) -> None:
    """Display detailed information for a specific profile."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM admin_profiles WHERE id = ?
    """, (profile_id,))
    
    profile = cursor.fetchone()
    
    if not profile:
        print(f"Profile with ID {profile_id} not found.")
        return
    
    # Get column names
    cursor.execute("PRAGMA table_info(admin_profiles)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"\nProfile Details (ID: {profile_id}):")
    print(f"{'='*50}")
    
    for i, (col_name, value) in enumerate(zip(columns, profile)):
        if col_name in ['positive_prompt', 'negative_prompt'] and value:
            print(f"\n{col_name}:")
            print(f"{value}")
        else:
            print(f"{col_name}: {value}")
    
    conn.close()

def reset_generation_status() -> None:
    """Reset all generation status flags (for testing)."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE admin_profiles 
        SET prompt_generated = 0, image_generated = 0, 
            positive_prompt = NULL, negative_prompt = NULL, image_path = NULL
    """)
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"Reset generation status for {affected} profiles.")

def view_prompts() -> None:
    """Display all generated prompts."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, first_name, last_name, category, subcategory, positive_prompt, negative_prompt
        FROM admin_profiles
        WHERE prompt_generated = 1
        ORDER BY category, subcategory, id
    """)
    
    profiles = cursor.fetchall()
    
    if not profiles:
        print("No prompts found in database.")
        return
    
    for profile in profiles:
        id_val, first_name, last_name, category, subcategory, pos_prompt, neg_prompt = profile
        subcat_display = subcategory if subcategory else "N/A"
        print(f"\n{'='*80}")
        print(f"Profile ID: {id_val}")
        print(f"Name: {first_name} {last_name}")
        print(f"Category: {category}, Subcategory: {subcat_display}")
        print(f"\nPositive Prompt:")
        print(f"{pos_prompt}")
        print(f"\nNegative Prompt:")
        print(f"{neg_prompt}")
        print(f"{'='*80}")
    
    conn.close()

def main():
    """Main function for database utilities."""
    parser = argparse.ArgumentParser(description='Database utilities for AI Persona Image Generator')
    parser.add_argument('--create-db', action='store_true', help='Create database and tables')
    parser.add_argument('--recreate-db', action='store_true', help='Recreate database (drop and create tables)')
    parser.add_argument('--import-json', action='store_true', help='Scan and import JSON files from data directory')
    parser.add_argument('--view-all', action='store_true', help='View all profiles')
    parser.add_argument('--view-prompts', action='store_true', help='View all generated prompts')
    parser.add_argument('--view-status', action='store_true', help='View generation status summary')
    parser.add_argument('--view-profile', type=int, help='View details for specific profile ID')
    parser.add_argument('--view-categories', action='store_true', help='View all categories and subcategories')
    parser.add_argument('--view-category', type=str, help='View profiles by category')
    parser.add_argument('--view-subcategory', type=str, nargs=2, metavar=('CATEGORY', 'SUBCATEGORY'), 
                       help='View profiles by category and subcategory')
    parser.add_argument('--reset', action='store_true', help='Reset all generation status (for testing)')
    parser.add_argument('--view-image-paths', action='store_true', help='View all image paths in the database')
    
    args = parser.parse_args()
    
    if args.create_db:
        create_database()
    elif args.recreate_db:
        confirm = input("Are you sure you want to recreate the database? This will delete all existing data! (y/N): ")
        if confirm.lower() == 'y':
            recreate_database()
        else:
            print("Database recreation cancelled.")
    elif args.import_json:
        scan_and_import_json_files()
    elif args.view_all:
        view_all_profiles()
    elif args.view_prompts:
        view_prompts()
    elif args.view_status:
        view_generation_status()
    elif args.view_profile:
        view_profile_details(args.view_profile)
    elif args.view_categories:
        view_categories()
    elif args.view_category:
        view_profiles_by_category(category=args.view_category)
    elif args.view_subcategory:
        category, subcategory = args.view_subcategory
        view_profiles_by_category(category=category, subcategory=subcategory)
    elif args.reset:
        confirm = input("Are you sure you want to reset all generation status? (y/N): ")
        if confirm.lower() == 'y':
            reset_generation_status()
        else:
            print("Reset cancelled.")
    elif args.view_image_paths:
        view_image_paths()
    else:
        print("Please specify an action. Use --help for options.")
        print("\nAvailable commands:")
        print("  --create-db          Create database and tables")
        print("  --recreate-db        Recreate database (drop and create tables)")
        print("  --import-json        Scan and import JSON files from data directory")
        print("  --view-all           View all profiles")
        print("  --view-status        View generation status summary")
        print("  --view-categories    View all categories and subcategories")
        print("  --view-image-paths   View all image paths in the database")
        print("  --help               Show all options")

if __name__ == "__main__":
    main() 