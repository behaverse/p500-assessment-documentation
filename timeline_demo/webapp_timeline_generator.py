#!/usr/bin/env python3
"""
WebApp Timeline Content Generator

Generates timeline content for the main webapp by using the clean timeline generator
to process configuration files and create rich timeline content for each engine.
"""

import json
import re
import yaml
from pathlib import Path
import os
import sys

# Add the current directory to the Python path to import our modules
sys.path.append('.')

from clean_timeline_generator import CleanTimelineResolver, CleanHTMLGenerator

class WebAppTimelineGenerator:
    def __init__(self):
        self.config_dir = Path("content/timeline_configs")
        self.locales_path = Path("content")
        self.images_path = Path("content/images")
        self.output_dir = Path("webapp/assets/timelines")
        self.engines_json_path = Path("webapp/content/engines.json")
        
        # Engine name mappings
        self.engine_names = {
            'BCS': 'Belval Card Sorting',
            'DS': 'Digit Span',
            'NB': 'N-back',
            'WO': 'Which-One',
            'UFOV': 'Useful Field of View',
            'TH': 'Target Hit',
            'SRM': 'Stimulus Response Mapping',
            'SOS': 'Self-Ordered Search',
            'SMC': 'Symbol Matrix Comparison',
            'RE': 'Regular Expression',
            'BM': 'Belval Matrices',
            'BSAC': 'Spatial Attention Cueing',
            'MOT': 'Multiple Object Tracking',
            'OC': 'Ordered Clicks',
            'OOO': 'Odd One Out',
            'PC': 'Polygon Comparison',
        }
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def find_engine_configs(self):
        """Find all engine configuration files."""
        configs = []
        for config_file in self.config_dir.glob("*.json"):
            if not config_file.name.endswith('.meta'):
                engine_code = config_file.stem
                configs.append(engine_code)
        return sorted(configs)
    
    def find_engine_timelines(self, config_path: Path, engine_code: str):
        """Find all timeline definitions in an engine configuration."""
        try:
            resolver = CleanTimelineResolver(
                str(config_path), 
                str(self.locales_path), 
                str(self.images_path / engine_code)
            )
            
            config = resolver.config
            timelines = config.get('Timelines', {})
            
            # Find timelines that start with the engine code
            engine_timelines = []
            for timeline_name in timelines.keys():
                if timeline_name.startswith(f'XCIT_{engine_code}_'):
                    engine_timelines.append(timeline_name)
            
            return sorted(engine_timelines)
        except Exception as e:
            print(f"Error processing {engine_code}: {e}")
            return []
    
    def generate_timeline_content(self, engine_code: str, timeline_name: str):
        """Generate the clean timeline content for a specific timeline."""
        config_path = self.config_dir / f"{engine_code}.json"
        
        try:
            resolver = CleanTimelineResolver(
                str(config_path),
                str(self.locales_path),
                str(self.images_path / engine_code)
            )
            
            generator = CleanHTMLGenerator(resolver)
            timeline_data = resolver.extract_timeline_content(timeline_name)
            
            if not timeline_data:
                return None
            
            # Generate HTML content
            content_html = generator._build_timeline_content(timeline_name, timeline_data)
            
            # Wrap in the webapp structure
            wrapped_content = f'''<div class="timeline-detail-container">
    <div class="timeline-header">
        <div class="timeline-title-section">
            <h2>{timeline_name}</h2>
            <div class="timeline-meta">
                <span class="timeline-engine">{self.engine_names.get(engine_code, engine_code)}</span>
                <span class="timeline-id">{timeline_name}</span>
            </div>
        </div>
    </div>
    
    <div class="timeline-content">
        <div class="timeline-description">
            <h3>Timeline Content</h3>
        </div>
        
        {content_html}
    </div>
</div>

<style>
{generator._get_clean_css()}

/* Additional styles for webapp integration */
.timeline-detail-container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}}

.timeline-header {{
    border-bottom: 2px solid #dee2e6;
    padding-bottom: 20px;
    margin-bottom: 30px;
}}

.timeline-title-section h2 {{
    font-size: 28px;
    font-weight: 600;
    margin: 0 0 10px 0;
    color: #212529;
}}

.timeline-meta {{
    display: flex;
    gap: 20px;
    font-size: 14px;
    color: #6c757d;
}}

.timeline-engine {{
    font-weight: 500;
}}

.timeline-id {{
    font-family: monospace;
    background: #f8f9fa;
    padding: 4px 8px;
    border-radius: 4px;
    border: 1px solid #dee2e6;
}}

/* Responsive adjustments */
@media (max-width: 768px) {{
    .timeline-detail-container {{
        padding: 10px;
    }}
    
    .timeline-title-section h2 {{
        font-size: 24px;
    }}
    
    .timeline-meta {{
        flex-direction: column;
        gap: 8px;
    }}
}}
</style>

<script>
{generator._get_collapsible_js()}
</script>'''
            
            return wrapped_content
            
        except Exception as e:
            print(f"Error generating content for {engine_code} - {timeline_name}: {e}")
            return None
    
    def load_existing_engines_json(self):
        """Load the existing engines.json file."""
        try:
            with open(self.engines_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self.engines_json_path} not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing {self.engines_json_path}: {e}")
            return {}
    
    def update_engine_timelines(self, engines_data: dict, engine_code: str, timelines: list):
        """Update the timeline content for a specific engine in the engines data."""
        if engine_code not in engines_data:
            print(f"Engine {engine_code} not found in engines.json")
            return
        
        engine_data = engines_data[engine_code]
        
        # Ensure timelines category exists
        if 'categories' not in engine_data:
            engine_data['categories'] = {}
        
        if 'timelines' not in engine_data['categories']:
            engine_data['categories']['timelines'] = {
                'hasSubItems': True,
                'subItems': {}
            }
        
        timelines_category = engine_data['categories']['timelines']
        
        # Clear existing timeline content
        timelines_category['subItems'] = {}
        
        # Clear old content field if it exists
        if 'content' in timelines_category:
            del timelines_category['content']
        
        # Add new timeline content
        for i, timeline_name in enumerate(timelines, 1):
            print(f"  Processing timeline {timeline_name}...")
            
            content = self.generate_timeline_content(engine_code, timeline_name)
            if content:
                # Create a friendly display name using just the number
                timeline_display = f"{i:02d}"
                
                timelines_category['subItems'][timeline_display] = {
                    'title': f"{engine_code} {timeline_display}",
                    'body': content
                }
            else:
                print(f"    Failed to generate content for {timeline_name}")
        
        # Add default/overview content
        timeline_count = len(timelines)
        engine_full_name = self.engine_names.get(engine_code, engine_code)
        
        default_content = f'''<div class="timelines-container">
    <div class="timelines-header">
        <h2>{engine_full_name} Timelines</h2>
        <div class="timeline-stats">
            <span class="timeline-count">{timeline_count} available timelines</span>
        </div>
    </div>
    
    <div class="timelines-overview">
        <p>Select a specific timeline from the sub-navigation to view detailed timeline content including instructions, test blocks, rules, and parameters.</p>
        
        <div class="timeline-summary">
            <h3>Available Timelines</h3>
            <div class="timeline-grid">'''
        
        for i, timeline_name in enumerate(timelines, 1):
            timeline_display = f"{i:02d}"
            default_content += f'''
                <div class="timeline-card" data-timeline="{timeline_name}">
                    <div class="timeline-card-header">
                        <h4>{engine_code} {timeline_display}</h4>
                        <span class="timeline-id">{timeline_name}</span>
                    </div>
                    <div class="timeline-card-body">
                        <p>Detailed timeline configuration with instructions, rules, and test blocks.</p>
                    </div>
                </div>'''
        
        default_content += '''
            </div>
        </div>
    </div>
    
    <div class="timeline-info">
        <h3>About Timelines</h3>
        <p>Each timeline represents a complete task configuration with:</p>
        <ul>
            <li><strong>Instructions</strong>: Step-by-step user guidance</li>
            <li><strong>Test Blocks</strong>: Configured assessment phases</li>
            <li><strong>Rules</strong>: Game mechanics and requirements</li>
            <li><strong>Parameters</strong>: Detailed configuration settings</li>
        </ul>
        <p>This content is generated from the actual configuration files used by the assessment engine.</p>
    </div>
</div>

<style>
.timelines-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

.timelines-header {
    border-bottom: 2px solid #dee2e6;
    padding-bottom: 20px;
    margin-bottom: 30px;
}

.timelines-header h2 {
    font-size: 28px;
    font-weight: 600;
    margin: 0 0 10px 0;
    color: #212529;
}

.timeline-stats {
    color: #6c757d;
    font-size: 14px;
}

.timeline-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.timeline-card {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: box-shadow 0.2s ease;
}

.timeline-card:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.timeline-card-header {
    margin-bottom: 12px;
}

.timeline-card-header h4 {
    font-size: 16px;
    font-weight: 600;
    margin: 0 0 8px 0;
    color: #212529;
}

.timeline-id {
    font-family: monospace;
    background: #f8f9fa;
    padding: 4px 8px;
    border-radius: 4px;
    border: 1px solid #dee2e6;
    font-size: 12px;
    color: #6c757d;
}

.timeline-card-body p {
    color: #495057;
    font-size: 14px;
    line-height: 1.5;
    margin: 0;
}

.timeline-info {
    margin-top: 40px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
}

.timeline-info h3 {
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 15px 0;
    color: #212529;
}

.timeline-info p {
    color: #495057;
    line-height: 1.6;
    margin: 0 0 15px 0;
}

.timeline-info ul {
    color: #495057;
    line-height: 1.6;
    margin: 0 0 15px 0;
}

.timeline-info ul li {
    margin-bottom: 8px;
}

@media (max-width: 768px) {
    .timeline-grid {
        grid-template-columns: 1fr;
    }
    
    .timelines-container {
        padding: 10px;
    }
}
</style>'''
        
        timelines_category['content'] = {
            'title': f"{engine_full_name} Timelines",
            'body': default_content
        }
    
    def generate_all_timeline_content(self):
        """Generate timeline content for all engines."""
        print("WebApp Timeline Generator")
        print("=" * 50)
        
        # Load existing engines.json
        print("Loading engines.json...")
        engines_data = self.load_existing_engines_json()
        
        if not engines_data:
            print("Failed to load engines.json. Cannot proceed.")
            return
        
        # Find all engine configurations
        configs = self.find_engine_configs()
        print(f"Found {len(configs)} engine configurations")
        
        updated_engines = []
        
        # Process each engine
        for engine_code in configs:
            if engine_code not in engines_data:
                print(f"Skipping {engine_code} - not found in engines.json")
                continue
                
            print(f"\nProcessing {engine_code} ({self.engine_names.get(engine_code, engine_code)})...")
            
            # Find timelines for this engine
            config_path = self.config_dir / f"{engine_code}.json"
            timelines = self.find_engine_timelines(config_path, engine_code)
            
            if not timelines:
                print(f"  No timelines found for {engine_code}")
                continue
            
            print(f"  Found {len(timelines)} timelines: {', '.join(timelines)}")
            
            # Update timeline content
            self.update_engine_timelines(engines_data, engine_code, timelines)
            updated_engines.append(engine_code)
        
        # Save updated engines.json
        if updated_engines:
            print(f"\nSaving updated engines.json with timelines for: {', '.join(updated_engines)}")
            
            # Create backup
            backup_path = self.engines_json_path.with_suffix('.json.backup')
            if self.engines_json_path.exists():
                import shutil
                shutil.copy2(self.engines_json_path, backup_path)
                print(f"Backup created: {backup_path}")
            
            # Save updated file
            with open(self.engines_json_path, 'w', encoding='utf-8') as f:
                json.dump(engines_data, f, indent=2, ensure_ascii=False)
            
            print(f"Successfully updated timeline content for {len(updated_engines)} engines!")
        else:
            print("No engines were updated.")
        
        print("\nGeneration complete!")


def main():
    """Main function to run the timeline content generation."""
    generator = WebAppTimelineGenerator()
    generator.generate_all_timeline_content()


if __name__ == "__main__":
    main()