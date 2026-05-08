#!/usr/bin/env python3
"""
Generate Clean Timeline Demo - Creates a clean timeline demo for any specified timeline

Usage:
  python generate_clean_timeline.py <engine> <timeline_name>

Example:
  python generate_clean_timeline.py BCS XCIT_BCS_02
  python generate_clean_timeline.py OC XCIT_OC_01
"""

import sys
from pathlib import Path
import re
from clean_timeline_generator import CleanTimelineResolver, CleanHTMLGenerator

# Dictionary mapping engines to their display names
ENGINE_NAMES = {
    "BCS": "Belval Card Sorting",
    "OC": "Ordered Clicks",
    "DS": "Digital Span", 
    "NB": "N-Back",
    "UFOV": "Useful Field of View Test",
    "TMT": "Trail Making Test",
    "NLT": "Number Letter Task",
    "SST": "Stop Signal Task",
    "ANT": "Attention Network Test",
    "CRT": "Choice Reaction Time",
    "FT": "Flanker Task",
    "SART": "Sustained Attention to Response Task",
    "PAL": "Paired Associate Learning",
    "WM": "Working Memory",
    # Add more engines as needed
}

def generate_clean_timeline(engine: str, timeline_name: str):
    """Generate clean timeline demo for the specified timeline."""
    # Get the base path
    base_path = Path("/home/pedro/Repos/behaverse_assessment_documentation")
    
    # Configuration paths
    config_path = str(base_path / f"data/content_temp/Configs/{engine}.json")
    locales_path = str(base_path / "data/content_temp")
    images_path = str(base_path / f"data/content_temp/Images/{engine}")
    
    # Verify paths exist
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"Error: Config file not found: {config_path}")
        return False
    
    if not Path(locales_path).exists():
        print(f"Error: Locales path not found: {locales_path}")
        return False
    
    # Create resolver and generator
    resolver = CleanTimelineResolver(config_path, locales_path, images_path)
    generator = CleanHTMLGenerator(resolver)
    
    # Generate timeline output filename - use lowercase engine and timeline
    timeline_short = timeline_name.lower().split('_')[-2:]  # Get the last two parts (e.g., bcs_02)
    output_filename = '_'.join(timeline_short) + "_timeline_demo.html"
    output_path = str(base_path / "webapp" / output_filename)
    
    # Generate the timeline demo
    print(f"Generating {timeline_name} timeline demo to: {output_path}")
    generator.generate_html_page(timeline_name, output_path)
    print(f"Clean HTML generated: {output_path}")
    
    # Post-processing to fix common issues
    with open(output_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 1. Fix the title if needed
    if engine in ENGINE_NAMES:
        display_name = ENGINE_NAMES[engine]
        for old_name in ENGINE_NAMES.values():
            if old_name != display_name and old_name in html_content:
                html_content = html_content.replace(old_name, display_name)
                print(f"Fixed title: {old_name} -> {display_name}")
    
    # 2. Fix image paths to ensure they're correct from the webapp directory
    
    # Replace simple "Images/reference" format with proper path (without duplicating engine)
    if 'src="Images/' in html_content:
        html_content = html_content.replace('src="Images/', f'src="../data/content_temp/Images/')
        print("Fixed simple image paths")
    
    # Check if there are still any other image formats to fix
    pattern = r'src="([^"]+)"'
    matches = re.findall(pattern, html_content)
    
    # Replace all remaining image paths with the correct path
    if matches:
        for img_path in matches:
            # Skip if path already starts with ../data
            if img_path.startswith('../data'):
                continue
                
            # Extract the engine and image name from the path
            if 'Images' in img_path:
                # Find the position of 'Images' in the path
                images_pos = img_path.find('Images')
                if images_pos != -1:
                    # Extract everything after 'Images/'
                    img_part = img_path[images_pos + 7:]  # 7 is the length of 'Images/'
                    # Create new path with correct relative path from webapp directory
                    # Don't add the engine name again if it's already in the path
                    if engine + '/' in img_part or engine + '.' in img_part:
                        new_path = f'../data/content_temp/Images/{img_part}'
                    else:
                        new_path = f'../data/content_temp/Images/{engine}/{img_part}'
                    # Replace the old path with the new path
                    html_content = html_content.replace(f'src="{img_path}"', f'src="{new_path}"')
                    print(f"Fixed complex image path: {img_path} -> {new_path}")
            else:
                # For other formats, add the full path structure
                # Avoid duplicating the engine name if it's already in the path
                if engine + '/' in img_path or engine + '.' in img_path:
                    new_path = f'../data/content_temp/Images/{img_path}'
                else:
                    new_path = f'../data/content_temp/Images/{engine}/{img_path}'
                html_content = html_content.replace(f'src="{img_path}"', f'src="{new_path}"')
                print(f"Fixed other image path: {img_path} -> {new_path}")
    
    # Write the fixed content back to the file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Successfully generated {timeline_name} timeline demo")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_clean_timeline.py <engine> <timeline_name>")
        print("Example: python generate_clean_timeline.py BCS XCIT_BCS_02")
        sys.exit(1)
    
    engine = sys.argv[1]
    timeline_name = sys.argv[2]
    
    generate_clean_timeline(engine, timeline_name)