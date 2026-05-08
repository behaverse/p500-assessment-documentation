#!/usr/bin/env python3
"""
Validate BCS Timeline - Checks if BCS_02 timeline correctly represents the BCS.json configuration

This script ensures that the BCS_02 timeline HTML only includes sections that actually
exist in the BCS.json configuration file.
"""

import json
from pathlib import Path
import re

def validate_bcs_timeline():
    """Validate that the BCS_02 timeline HTML matches the BCS.json configuration."""
    # Get the base path
    base_path = Path("/home/pedro/Repos/behaverse_assessment_documentation")
    
    # Path to the BCS.json configuration file
    bcs_config_path = base_path / "data/content_temp/Configs/BCS.json"
    
    # Path to the BCS_02 timeline demo HTML file
    bcs_02_html_path = base_path / "webapp/bcs_02_timeline_demo.html"
    
    # Read the BCS.json configuration file
    with open(bcs_config_path, 'r', encoding='utf-8') as f:
        bcs_config = json.load(f)
    
    # Check if XCIT_BCS_02_Advanced exists in the configuration
    advanced_in_config = False
    if "Timelines" in bcs_config:
        for timeline in bcs_config["Timelines"]:
            if timeline.get("Id") == "XCIT_BCS_02_Advanced":
                advanced_in_config = True
                break
    
    # Read the BCS_02 timeline demo HTML file
    with open(bcs_02_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Check if XCIT_BCS_02_Advanced section exists in the HTML
    advanced_in_html = "XCIT_BCS_02_Advanced" in html_content
    
    # Print validation results
    print("\nBCS Timeline Validation Results:")
    print("-" * 30)
    print(f"XCIT_BCS_02_Advanced in config: {advanced_in_config}")
    print(f"XCIT_BCS_02_Advanced in HTML: {advanced_in_html}")
    
    if not advanced_in_config and advanced_in_html:
        print("\n⚠️ ISSUE: XCIT_BCS_02_Advanced section exists in the HTML but not in the configuration.")
        print("The timeline needs to be fixed to match the configuration.")
    elif not advanced_in_config and not advanced_in_html:
        print("\n✅ SUCCESS: The BCS_02 timeline HTML correctly reflects the configuration.")
        print("The XCIT_BCS_02_Advanced section is not in the config and not in the HTML.")
    elif advanced_in_config and not advanced_in_html:
        print("\n⚠️ ISSUE: XCIT_BCS_02_Advanced section exists in the configuration but not in the HTML.")
        print("The timeline needs to be regenerated to include this section.")
    else:
        print("\n✅ SUCCESS: The BCS_02 timeline HTML correctly includes the Advanced section from the configuration.")

if __name__ == "__main__":
    validate_bcs_timeline()