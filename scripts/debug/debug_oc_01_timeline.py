#!/usr/bin/env python3
"""
Debug OC_01 Timeline Generation - For examining the OC_01 timeline extraction and HTML generation
"""

from pathlib import Path
import re
import json
from clean_timeline_generator import CleanTimelineResolver, CleanHTMLGenerator

def debug_oc_01_generation():
    """Debug the generation of OC_01 timeline."""
    # Get the base path
    base_path = Path("/home/pedro/Repos/behaverse_assessment_documentation")
    
    # OC Configuration
    oc_config_path = str(base_path / "data/content_temp/Configs/OC.json")
    oc_locales_path = str(base_path / "data/content_temp")
    oc_images_path = str(base_path / "data/content_temp/Images/OC")
    
    # Create resolver for OC
    oc_resolver = CleanTimelineResolver(oc_config_path, oc_locales_path, oc_images_path)
    
    # Extract the OC_01 timeline content
    timeline_name = "XCIT_OC_01"
    timeline_data = oc_resolver.extract_timeline_content(timeline_name)
    
    # Print timeline data overview
    print(f"Timeline: {timeline_name}")
    print(f"Total blocks: {len(timeline_data.get('blocks', []))}")
    
    # Group blocks by section type
    sections = {'Tutorial': [], 'Practice': [], 'Test': []}
    
    for block in timeline_data.get('blocks', []):
        if 'timeline' in block:
            timeline_ref = block['timeline']
            for section_name in sections:
                if section_name in timeline_ref:
                    sections[section_name].append(block)
                    break
        elif 'name' in block:
            block_name = block['name']
            for section_name in sections:
                if section_name in block_name:
                    sections[section_name].append(block)
                    break
    
    # Print sections overview
    print("\nSections overview:")
    for section_name, blocks in sections.items():
        print(f"- {section_name}: {len(blocks)} blocks")
        for i, block in enumerate(blocks, 1):
            if 'timeline' in block:
                print(f"  {i}. Timeline: {block['timeline']}")
            elif 'name' in block:
                print(f"  {i}. Name: {block['name']}")
    
    # Create generator and check HTML generation
    oc_generator = CleanHTMLGenerator(oc_resolver)
    
    # Generate HTML for testing
    print("\nGenerating OC_01 timeline demo...")
    oc_01_output_path = str(base_path / "webapp/oc_01_timeline_demo.html")
    oc_generator.generate_html_page(timeline_name, oc_01_output_path)
    print(f"HTML generated at: {oc_01_output_path}")
    
    # Verify the title in the generated HTML
    with open(oc_01_output_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Fix the title if needed
    if "Useful Field of View Test" in html_content:
        html_content = html_content.replace("Useful Field of View Test", "Ordered Clicks")
        with open(oc_01_output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("Fixed title in HTML")
    
    # Verify the image paths
    image_paths = re.findall(r'src="(data/content_temp/Images/.*?)"', html_content)
    if image_paths:
        print(f"\nFound {len(image_paths)} image references in HTML:")
        for path in image_paths[:5]:  # Show first 5 images only
            print(f"- {path}")
        
        # Fix image paths if needed
        html_content = html_content.replace('src="data/content_temp/Images/', 'src="../data/content_temp/Images/')
        with open(oc_01_output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("Fixed image paths in HTML")

if __name__ == "__main__":
    debug_oc_01_generation()