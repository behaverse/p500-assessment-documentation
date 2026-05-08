#!/usr/bin/env python3
"""
Generate BCS Timelines - Creates clean timeline demos for BCS_01 and BCS_02

This script uses the clean_timeline_generator to create timeline demos for
both BCS_01 and BCS_02 configurations.
"""

from pathlib import Path
from clean_timeline_generator import CleanTimelineResolver, CleanHTMLGenerator

def main():
    """Generate timeline demos for BCS_01 and BCS_02."""
    # Get the base path
    base_path = Path("/home/pedro/Repos/behaverse_assessment_documentation")
    
    # BCS Configuration
    bcs_config_path = str(base_path / "data/content_temp/Configs/BCS.json")
    bcs_locales_path = str(base_path / "data/content_temp")
    bcs_images_path = str(base_path / "data/content_temp/Images/BCS")
    
    # Create resolver and generator for BCS
    bcs_resolver = CleanTimelineResolver(bcs_config_path, bcs_locales_path, bcs_images_path)
    bcs_generator = CleanHTMLGenerator(bcs_resolver)
    
    # Generate the BCS HTML pages for both timelines
    bcs_01_output_path = str(base_path / "webapp/bcs_01_timeline_demo.html")
    print(f"Generating BCS_01 timeline demo to: {bcs_01_output_path}")
    bcs_generator.generate_html_page("XCIT_BCS_01", bcs_01_output_path)
    
    bcs_02_output_path = str(base_path / "webapp/bcs_02_timeline_demo.html")
    print(f"Generating BCS_02 timeline demo to: {bcs_02_output_path}")
    bcs_generator.generate_html_page("XCIT_BCS_02", bcs_02_output_path)
    
    print("Generated timeline demos for BCS_01 and BCS_02")

if __name__ == "__main__":
    main()