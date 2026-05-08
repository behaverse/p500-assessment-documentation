#!/usr/bin/env python3
"""
Generate OC_01 Timeline - Creates a clean timeline demo for OC_01

This script specifically generates the OC_01 timeline demo.
"""

from pathlib import Path
import re
from clean_timeline_generator import CleanTimelineResolver, CleanHTMLGenerator

def generate_oc_01_timeline():
    """Generate timeline demo for OC_01."""
    # Get the base path
    base_path = Path("/home/pedro/Repos/behaverse_assessment_documentation")
    
    # OC Configuration
    oc_config_path = str(base_path / "data/content_temp/Configs/OC.json")
    oc_locales_path = str(base_path / "data/content_temp")
    oc_images_path = str(base_path / "data/content_temp/Images/OC")
    
    # Create resolver and generator for OC
    oc_resolver = CleanTimelineResolver(oc_config_path, oc_locales_path, oc_images_path)
    oc_generator = CleanHTMLGenerator(oc_resolver)
    
    # Generate the OC_01 timeline demo
    oc_01_output_path = str(base_path / "webapp/oc_01_timeline_demo.html")
    print(f"Generating OC_01 timeline demo to: {oc_01_output_path}")
    oc_generator.generate_html_page("XCIT_OC_01", oc_01_output_path)
    
    print(f"Successfully generated OC_01 timeline demo")

if __name__ == "__main__":
    generate_oc_01_timeline()