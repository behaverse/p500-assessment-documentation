#!/usr/bin/env python3
"""
Webapp Updater Script
=====================

Updates webapp/script.js with migrated engine data from Task spec.xlsx
Preserves existing navigation logic while replacing placeholder content with real data.
"""

import json
import re
from pathlib import Path

def transform_engine_data_for_webapp(engines_data):
    """Transform the migrated engine data to match webapp's expected structure"""
    
    # First, add the HOME page
    webapp_data = {
        "HOME": {
            "name": "HOME",
            "isHomePage": True,
            "content": {
                "title": "Behaverse Assessment Documentation",
                "body": """
                    <h2>Welcome to Behaverse Assessment Documentation</h2>
                    <p>This platform provides comprehensive documentation for cognitive assessment engines.</p>
                    <h3>Available Assessment Tasks</h3>
                    <p>Explore 16 cognitive assessment engines, each designed for specific research needs:</p>
                    <ul>
                        <li><strong>BCS</strong> - Belval Card Sorting (set-shifting)</li>
                        <li><strong>DS</strong> - Digit Span (working memory)</li>
                        <li><strong>NB</strong> - N-back (working memory)</li>
                        <li><strong>WO</strong> - Which-One (attention & flanker tasks)</li>
                        <li><strong>UFOV</strong> - Useful Field of View (visual attention)</li>
                        <li><strong>TH</strong> - Target Hit (reaction time)</li>
                        <li><strong>SRM</strong> - Stimulus Response Mapping (reaction time)</li>
                        <li><strong>SOS</strong> - Self-Ordered Search (spatial working memory)</li>
                        <li><strong>SMC</strong> - Symbol Matrix Comparison (pattern matching)</li>
                        <li><strong>RE</strong> - Regular Expression (sustained attention)</li>
                        <li><strong>BM</strong> - Belval Matrices (fluid intelligence)</li>
                        <li><strong>BSAC</strong> - Spatial Attention Cueing (spatial attention)</li>
                        <li><strong>MOT</strong> - Multiple Object Tracking (visual attention)</li>
                        <li><strong>OC</strong> - Ordered Clicks (spatial working memory)</li>
                        <li><strong>OOO</strong> - Odd One Out (reasoning)</li>
                        <li><strong>PC</strong> - Polygon Comparison (visual perception)</li>
                    </ul>
                    <h3>Features</h3>
                    <p>• Complete task descriptions and scientific background</p>
                    <p>• Detailed parameter specifications</p>
                    <p>• Academic references and glossaries</p>
                    <p>• Implementation notes and considerations</p>
                """
            }
        }
    }
    
    # Transform each engine to webapp format
    for engine_id, engine_data in engines_data.items():
        webapp_engine = {
            "name": engine_data["config"],  # Show config code (BCS, DS, etc.) in navigation
            "fullName": engine_data["name"], # Store full name for content display
            "config": engine_data["config"],
            "categories": {}
        }
        
        # Transform each category
        for category_id, category_data in engine_data["categories"].items():
            webapp_category = {
                "hasSubItems": True,  # All categories have sub-items based on our structure
                "subItems": {}
            }
            
            # Transform content items to sub-items
            if "content" in category_data:
                for content_id, content_item in category_data["content"].items():
                    webapp_category["subItems"][content_id] = {
                        "title": content_item["title"],
                        "body": content_item["body"]
                    }
            
            webapp_engine["categories"][category_id] = webapp_category
        
        webapp_data[engine_id] = webapp_engine
    
    return webapp_data

def update_webapp_script():
    """Update webapp/script.js with migrated engine data"""
    
    # Read the migrated engine data
    engines_path = Path("migrated_content/engines.json")
    if not engines_path.exists():
        print("❌ Error: engines.json not found. Run migrate_scenes.py first.")
        return False
    
    with open(engines_path, 'r', encoding='utf-8') as f:
        engines_data = json.load(f)
    
    print("📖 Loaded migrated engine data")
    
    # Transform for webapp
    webapp_data = transform_engine_data_for_webapp(engines_data)
    
    # Read current webapp script
    script_path = Path("webapp/script.js")
    if not script_path.exists():
        print("❌ Error: webapp/script.js not found")
        return False
    
    with open(script_path, 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    print("📖 Read current webapp script")
    
    # Find the engineData definition and replace it
    # Look for the pattern: const engineData = { ... };
    engine_data_pattern = r'const engineData = \{.*?\n\};'
    
    # Create new engineData JavaScript
    new_engine_data = "const engineData = " + json.dumps(webapp_data, indent=4, ensure_ascii=False) + ";"
    
    # Replace the engineData in the script
    if re.search(engine_data_pattern, script_content, re.DOTALL):
        updated_script = re.sub(engine_data_pattern, new_engine_data, script_content, flags=re.DOTALL)
        print("✅ Found and replaced engineData in script")
    else:
        print("❌ Could not find engineData pattern in script")
        return False
    
    # Backup original script
    backup_path = script_path.with_suffix('.js.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    print(f"💾 Backed up original script to {backup_path}")
    
    # Write updated script
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(updated_script)
    
    print("✅ Updated webapp/script.js with migrated content")
    
    # Create summary
    print(f"\n📊 UPDATE SUMMARY")
    print(f"   - Engines updated: {len(engines_data)}")
    print(f"   - Categories per engine: about, parameters, timelines, data")
    print(f"   - Content items: overview, references, glossary, notes (where available)")
    print(f"   - Navigation shows: {[data['name'] for data in webapp_data.values() if 'name' in data and data['name'] != 'HOME']}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("WEBAPP UPDATE WITH MIGRATED CONTENT")
    print("=" * 60)
    
    success = update_webapp_script()
    
    if success:
        print(f"\n🎯 Next step: Test the webapp to ensure all content displays correctly")
        print(f"   Open http://localhost:8080 and verify:")
        print(f"   - Navigation shows config codes (BCS, DS, etc.)")
        print(f"   - Content displays full task names and descriptions")
        print(f"   - All categories and sub-items work properly")
    else:
        print(f"\n❌ Update failed. Check error messages above.")