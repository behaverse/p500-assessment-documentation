#!/usr/bin/env python3
import json
from clean_timeline_generator import CleanTimelineResolver

def debug_section_creation():
    # Initialize resolver with proper paths (same as generate_bcs_02_timeline.py)
    config_path = "data/content_temp/Configs/BCS.json"
    locales_path = "data/content_temp"
    images_path = "data/content_temp/Images/BCS"
    
    resolver = CleanTimelineResolver(config_path, locales_path, images_path)
    
    timeline_name = "XCIT_BCS_02"
    
    print(f"Loading config from: {config_path}")
    timeline_data = resolver.extract_timeline_content(timeline_name)
    
    if not timeline_data:
        print("Failed to load timeline data")
        return
        
    print(f"\nTimeline data loaded successfully")
    print(f"Number of blocks: {len(timeline_data.get('blocks', []))}")
    
    blocks = timeline_data.get('blocks', [])
    
    # Debug section grouping
    sections = {
        'Tutorial': [],
        'Practice': [], 
        'Test': []
    }
    
    print("\n--- Block Analysis ---")
    for i, block in enumerate(blocks):
        print(f"\nBlock {i+1}:")
        if 'timeline' in block:
            timeline_ref = block['timeline']
            print(f"  Type: Timeline reference")
            print(f"  Timeline: {timeline_ref}")
            
            if 'Tutorial' in timeline_ref:
                sections['Tutorial'].append(block)
                print(f"  -> Added to Tutorial section")
            elif 'Practice' in timeline_ref:
                sections['Practice'].append(block)
                print(f"  -> Added to Practice section")
            elif 'Test' in timeline_ref:
                sections['Test'].append(block)
                print(f"  -> Added to Test section")
            else:
                print(f"  -> No section match found!")
                
        elif 'name' in block:
            block_name = block['name']
            print(f"  Type: Block with name")
            print(f"  Name: {block_name}")
            
            if 'Tutorial' in block_name:
                sections['Tutorial'].append(block)
                print(f"  -> Added to Tutorial section")
            elif 'Practice' in block_name:
                sections['Practice'].append(block)
                print(f"  -> Added to Practice section")
            elif 'Test' in block_name:
                sections['Test'].append(block)
                print(f"  -> Added to Test section")
            else:
                print(f"  -> No section match found!")
        else:
            print(f"  Type: Unknown (no timeline or name)")
    
    print("\n--- Section Summary ---")
    for section_name in ['Tutorial', 'Practice', 'Test']:
        count = len(sections[section_name])
        print(f"{section_name}: {count} blocks")
        
    print("\n--- Section Creation Loop ---")
    section_counter = 1
    for section_name in ['Tutorial', 'Practice', 'Test']:
        has_blocks = bool(sections[section_name])
        print(f"{section_name}: has_blocks={has_blocks}, would create main-section-{section_counter if has_blocks else 'N/A'}")
        if has_blocks:
            section_counter += 1

if __name__ == "__main__":
    debug_section_creation()