#!/usr/bin/env python3
"""
Generate BCS_02 Timeline - Creates a clean timeline demo for BCS_02

This script specifically generates the BCS_02 timeline without the Advanced section.
"""

from pathlib import Path
import re
from clean_timeline_generator import CleanTimelineResolver, CleanHTMLGenerator

def generate_bcs_02_timeline():
    """Generate timeline demo for BCS_02."""
    # Get the base path
    base_path = Path("/home/pedro/Repos/behaverse_assessment_documentation")
    
    # BCS Configuration
    bcs_config_path = str(base_path / "data/content_temp/Configs/BCS.json")
    bcs_locales_path = str(base_path / "data/content_temp")
    bcs_images_path = str(base_path / "data/content_temp/Images/BCS")
    
    # Create resolver and generator for BCS
    bcs_resolver = CleanTimelineResolver(bcs_config_path, bcs_locales_path, bcs_images_path)
    bcs_generator = CleanHTMLGenerator(bcs_resolver)
    
    # Generate the BCS_02 timeline demo
    bcs_02_output_path = str(base_path / "webapp/bcs_02_timeline_demo.html")
    print(f"Generating BCS_02 timeline demo to: {bcs_02_output_path}")
    bcs_generator.generate_html_page("XCIT_BCS_02", bcs_02_output_path)
    
    # Make sure the Advanced section is removed
    with open(bcs_02_output_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Check and fix any UFOV references that might have been mistakenly included
    html_content = html_content.replace("XCIT_UFOV_03", "XCIT_BCS_02")
    html_content = html_content.replace("Useful Field of View Test", "Belval Card Sorting")
    
    # Remove any Advanced section references (but keep Test section)
    # Only remove sections that specifically mention "Advanced" in the title
    pattern = r'<section class="main-section collapsible-section"[^>]*>.*?<h2>[^<]*Advanced[^<]*</h2>.*?</section>\s*'
    html_content = re.sub(pattern, '', html_content, flags=re.DOTALL)
    
    # Write the fixed content back to the file
    with open(bcs_02_output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Successfully generated BCS_02 timeline demo - preserving Test section, removing only Advanced if present")

if __name__ == "__main__":
    generate_bcs_02_timeline()