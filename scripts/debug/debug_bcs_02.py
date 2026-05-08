#!/usr/bin/env python3
"""
Debug BCS_02 Timeline - Check what blocks are being extracted
"""

from pathlib import Path
from clean_timeline_generator import CleanTimelineResolver

def debug_bcs_02_extraction():
    """Debug what content is being extracted from BCS_02."""
    base_path = Path("/home/pedro/Repos/behaverse_assessment_documentation")
    
    # BCS Configuration
    bcs_config_path = str(base_path / "data/content_temp/Configs/BCS.json")
    bcs_locales_path = str(base_path / "data/content_temp")
    bcs_images_path = str(base_path / "data/content_temp/Images/BCS")
    
    # Create resolver
    resolver = CleanTimelineResolver(bcs_config_path, bcs_locales_path, bcs_images_path)
    
    # Extract timeline content
    timeline = resolver.extract_timeline_content("XCIT_BCS_02")
    
    print("=== BCS_02 Timeline Extraction Debug ===")
    print()
    
    if timeline:
        blocks = timeline.get('blocks', [])
        print(f"Total blocks found: {len(blocks)}")
        print()
        
        tutorial_blocks = []
        practice_blocks = []
        test_blocks = []
        
        for i, block in enumerate(blocks):
            print(f"Block {i+1}:")
            if 'timeline' in block:
                timeline_ref = block['timeline']
                print(f"  Type: timeline reference")
                print(f"  Timeline: {timeline_ref}")
                if 'Tutorial' in timeline_ref:
                    tutorial_blocks.append(block)
                    print("  → Grouped as: Tutorial")
                elif 'Practice' in timeline_ref:
                    practice_blocks.append(block)
                    print("  → Grouped as: Practice")
                elif 'Test' in timeline_ref:
                    test_blocks.append(block)
                    print("  → Grouped as: Test")
                else:
                    print("  → Not grouped (no match)")
            elif 'name' in block:
                block_name = block['name']
                print(f"  Type: test block")
                print(f"  Name: {block_name}")
                if 'Tutorial' in block_name:
                    tutorial_blocks.append(block)
                    print("  → Grouped as: Tutorial")
                elif 'Practice' in block_name:
                    practice_blocks.append(block)
                    print("  → Grouped as: Practice")
                elif 'Test' in block_name:
                    test_blocks.append(block)
                    print("  → Grouped as: Test")
                else:
                    print("  → Not grouped (no match)")
                if 'exitRules' in block:
                    print(f"  Exit Rules: {block['exitRules']}")
            else:
                print("  Type: unknown")
            print()
        
        print("=== Summary ===")
        print(f"Tutorial blocks: {len(tutorial_blocks)}")
        print(f"Practice blocks: {len(practice_blocks)}")
        print(f"Test blocks: {len(test_blocks)}")
        
        if not test_blocks:
            print()
            print("❌ NO TEST BLOCKS FOUND!")
            print("This explains why Test sections are missing from the HTML.")
    else:
        print("❌ No timeline data found for XCIT_BCS_02")

if __name__ == "__main__":
    debug_bcs_02_extraction()