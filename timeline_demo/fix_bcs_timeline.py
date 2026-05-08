#!/usr/bin/env python3
"""
Fix BCS Timeline Generator - Removes XCIT_BCS_02_Advanced section

This script fixes the timeline for BCS_02 by removing the Advanced section
which is not present in the actual BCS.json configuration.
"""

from pathlib import Path
import re

def remove_advanced_section(html_content):
    """Remove the XCIT_BCS_02_Advanced section from the HTML content."""
    # Define a pattern to match the entire section from start to end
    pattern = r'<section class="main-section collapsible-section" id="main-section-3">.*?</section>\s*'
    # Use re.DOTALL to make . match newlines as well
    fixed_content = re.sub(pattern, '', html_content, flags=re.DOTALL)
    return fixed_content

def main():
    """Fix the BCS_02 timeline HTML demo by removing the Advanced section."""
    # Get the base path
    base_path = Path("/home/pedro/Repos/behaverse_assessment_documentation")
    
    # Path to the BCS_02 timeline demo HTML file
    bcs_02_html_path = base_path / "webapp/bcs_02_timeline_demo.html"
    
    # Read the content of the HTML file
    with open(bcs_02_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Remove the Advanced section
    fixed_content = remove_advanced_section(html_content)
    
    # Write the fixed content back to the file
    with open(bcs_02_html_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"Fixed BCS_02 timeline demo at: {bcs_02_html_path}")
    print("Removed XCIT_BCS_02_Advanced section that was not in the BCS.json configuration")

if __name__ == "__main__":
    main()