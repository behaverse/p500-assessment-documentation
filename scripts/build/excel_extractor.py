#!/usr/bin/env python3
"""
Excel Data Extractor for Behaverse Assessment Documentation
===========================================================

This script extracts data from Task spec.xlsx and organizes it for webapp content generation.
It processes the 'scenes' and 'parameters' sheets to generate description and parameters pages
for all 16 engines in the spreadsheet.

Features:
- Extracts glossary from scenes sheet for parameters page
- Processes parameters with proper grouping and formatting
- Generates HTML content matching the webapp structure
- Supports all 16 engines defined in the spreadsheet
"""

import pandas as pd
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

class ExcelExtractor:
    """Extract and process data from Task spec.xlsx for webapp content generation."""
    
    def __init__(self, excel_path: str = "content/Task spec.xlsx"):
        """Initialize the extractor with the Excel file path."""
        self.excel_path = Path(excel_path)
        self.engines_data = {}
        self.scenes_data = None
        self.parameters_data = None
        
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.excel_path}")
    
    def load_excel_data(self):
        """Load data from all relevant Excel sheets."""
        print("📊 Loading Excel data...")
        
        try:
            # Load scenes sheet (engine descriptions)
            self.scenes_data = pd.read_excel(self.excel_path, sheet_name='scenes')
            print(f"   Loaded scenes: {len(self.scenes_data)} engines")
            
            # Load parameters sheet
            self.parameters_data = pd.read_excel(self.excel_path, sheet_name='parameters')
            print(f"   Loaded parameters: {len(self.parameters_data)} parameters")
            
        except Exception as e:
            raise Exception(f"Error loading Excel data: {e}")
    
    def extract_engine_list(self) -> List[str]:
        """Extract list of all engine configs from the scenes sheet."""
        if self.scenes_data is None:
            raise ValueError("Excel data not loaded. Call load_excel_data() first.")
        
        # Get unique engine configs from scenes sheet
        engines = self.scenes_data['config'].dropna().unique().tolist()
        print(f"🎯 Found {len(engines)} engines: {engines}")
        return engines
    
    def extract_description_data(self, engine_config: str) -> Dict[str, Any]:
        """Extract description page data for a specific engine from scenes sheet."""
        engine_row = self.scenes_data[self.scenes_data['config'] == engine_config]
        
        if engine_row.empty:
            print(f"⚠️  Warning: No data found for engine {engine_config}")
            return None
        
        row = engine_row.iloc[0]
        
        # Extract all relevant fields
        description_data = {
            'config': engine_config,
            'name': row.get('name', ''),
            'description': row.get('description', ''),
            'references': row.get('references', ''),
            'glossary': row.get('glossary', ''),  # This will be moved to parameters page
            'note': row.get('note', ''),
            'category': row.get('category', 'Task')
        }
        
        # Clean up NaN values
        for key, value in description_data.items():
            if pd.isna(value):
                description_data[key] = ''
        
        return description_data
    
    def extract_parameters_data(self, engine_config: str) -> Dict[str, Any]:
        """Extract parameters page data for a specific engine from parameters sheet."""
        engine_params = self.parameters_data[self.parameters_data['config'] == engine_config]
        
        if engine_params.empty:
            print(f"⚠️  Warning: No parameters found for engine {engine_config}")
            return None
        
        # Group parameters by type/category
        parameters_by_type = {}
        total_params = 0
        
        for _, param_row in engine_params.iterrows():
            param_type = param_row.get('type', 'General')
            if pd.isna(param_type):
                param_type = 'General'
            
            if param_type not in parameters_by_type:
                parameters_by_type[param_type] = []
            
            # Extract parameter details
            param_info = {
                'name': param_row.get('parameter', ''),
                'description': param_row.get('description', ''),
                'value_type': param_row.get('value_type', ''),
                'default': param_row.get('default', ''),
                'possible_values': param_row.get('possible_values', ''),
                'value_min': param_row.get('value_min', ''),
                'value_max': param_row.get('value_max', ''), 
                'note': param_row.get('note', ''),
                'sampling_rate': param_row.get('sampling_rate', '')
            }
            
            # Clean up NaN values
            for key, value in param_info.items():
                if pd.isna(value):
                    param_info[key] = ''
            
            parameters_by_type[param_type].append(param_info)
            total_params += 1
        
        return {
            'config': engine_config,
            'parameters_by_type': parameters_by_type,
            'total_params': total_params,
            'total_categories': len(parameters_by_type)
        }
    
    def format_glossary_html(self, glossary_text: str) -> str:
        """Format glossary text into HTML definition list."""
        if not glossary_text or pd.isna(glossary_text):
            return ""
        
        html = []
        html.append('<div class="glossary-section">')
        html.append('<h2>Glossary</h2>')
        html.append('<table class="glossary-table">')
        
        # Split glossary by lines and process each term/definition pair
        lines = glossary_text.strip().split('\n')
        current_term = None
        current_definition = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line contains definition (term: definition pattern)
            if ':' in line and not line.startswith(' '):
                # Save previous term if exists
                if current_term:
                    definition = ' '.join(current_definition).strip()
                    html.append(f'  <tr>')
                    html.append(f'    <td class="glossary-term">{current_term}</td>')
                    html.append(f'    <td class="glossary-definition">{definition}</td>')
                    html.append(f'  </tr>')
                
                # Start new term
                parts = line.split(':', 1)
                current_term = parts[0].strip()
                current_definition = [parts[1].strip()] if len(parts) > 1 else []
            else:
                # Continue definition from previous line
                if current_term:
                    current_definition.append(line)
        
        # Save last term
        if current_term:
            definition = ' '.join(current_definition).strip()
            html.append(f'  <tr>')
            html.append(f'    <td class="glossary-term">{current_term}</td>')
            html.append(f'    <td class="glossary-definition">{definition}</td>')
            html.append(f'  </tr>')
        
        html.append('</table>')
        html.append('</div>')
        
        return '\n'.join(html)
    
    def format_parameter_value_options(self, possible_values: str) -> str:
        """Format possible values into HTML list."""
        if not possible_values or pd.isna(possible_values):
            return ""
        
        html = []
        html.append('<div class="parameter-detail"><strong>Options:</strong></div>')
        html.append('<ul class="parameter-options">')
        
        try:
            # Try to parse as JSON first
            if possible_values.strip().startswith('{'):
                values_dict = json.loads(possible_values)
                for key, description in values_dict.items():
                    html.append(f'            <li><code>{key}</code>: {description}</li>')
            else:
                # Handle simple comma-separated values
                values = [v.strip() for v in possible_values.split(',')]
                for value in values:
                    html.append(f'            <li><code>{value}</code></li>')
        except (json.JSONDecodeError, Exception):
            # Fallback: treat as plain text
            html.append(f'            <li>{possible_values}</li>')
        
        html.append('        </ul>')
        return '\n'.join(html)
    
    def generate_description_html(self, engine_config: str) -> str:
        """Generate HTML content for description page."""
        desc_data = self.extract_description_data(engine_config)
        if not desc_data:
            return f"<p>No description data found for {engine_config}</p>"
        
        html = []
        html.append('<div class="description-sections">')
        
        # Main description
        if desc_data['description']:
            html.append('        <div class="overview-text">')
            html.append(f'            {desc_data["description"]}')
            html.append('        </div>')
        
        # References section
        if desc_data['references']:
            html.append('        <section class="description-section">')
            html.append('            <h2>References & Resources</h2>')
            html.append(f'            {desc_data["references"]}')
            html.append('        </section>')
        
        # Note: Glossary is moved to parameters page as per requirements
        # if desc_data['glossary']:
        #     html.append('        <section class="description-section">')
        #     html.append('            <h2>Technical Glossary</h2>')
        #     html.append(self.format_glossary_html(desc_data['glossary']))
        #     html.append('        </section>')
        
        html.append('</div>')
        
        return '\n'.join(html)
    
    def generate_parameters_html(self, engine_config: str) -> str:
        """Generate HTML content for parameters page (with glossary at top)."""
        params_data = self.extract_parameters_data(engine_config)
        desc_data = self.extract_description_data(engine_config)
        
        if not params_data:
            return f"<p>No parameters data found for {engine_config}</p>"
        
        html = []
        html.append('<div class="parameters-container">')
        
        # Glossary section at the top (moved from description page)
        if desc_data and desc_data['glossary']:
            html.append(self.format_glossary_html(desc_data['glossary']))
            html.append('')  # Add spacing
        
        # Main Parameters heading
        html.append('    <h2>Parameters</h2>')
        
        # Parameters by category/type
        for param_type, parameters in params_data['parameters_by_type'].items():
            html.append(f'    <h3>{param_type} ({len(parameters)} parameters)</h3>')
            
            for param in parameters:
                html.append('    <div class="parameter-item">')
                html.append(f'        <h4 class="parameter-name">{param["name"]}</h4>')
                
                if param['description']:
                    html.append(f'        <p class="parameter-description">{param["description"]}</p>')
                
                # Create inline details
                details = []
                if param['value_type']:
                    details.append(f'<strong>Type:</strong> {param["value_type"]}')
                if param['default']:
                    details.append(f'<strong>Default:</strong> {param["default"]}')
                if param['value_min'] or param['value_max']:
                    range_text = f"{param['value_min'] or '0'} - {param['value_max'] or 'inf'}"
                    details.append(f'<strong>Range:</strong> {range_text}')
                
                if details:
                    html.append(f'        <div class="parameter-details">')
                    for detail in details:
                        html.append(f'            <span>{detail}</span>')
                    html.append(f'        </div>')
                
                # Additional notes
                if param['note']:
                    html.append(f'        <div class="parameter-note"><strong>Note:</strong> {param["note"]}</div>')
                
                html.append('    </div>')
        
        html.append('</div>')
        
        return '\n'.join(html)
    
    def generate_all_engines_content(self) -> Dict[str, Dict[str, str]]:
        """Generate content for all engines in the spreadsheet."""
        self.load_excel_data()
        engines = self.extract_engine_list()
        
        all_content = {}
        
        print(f"\n🔄 Processing {len(engines)} engines...")
        
        for engine_config in engines:
            print(f"   Processing {engine_config}...")
            
            # Generate description page content
            description_html = self.generate_description_html(engine_config)
            
            # Generate parameters page content  
            parameters_html = self.generate_parameters_html(engine_config)
            
            # Get engine name for title
            desc_data = self.extract_description_data(engine_config)
            engine_name = desc_data['name'] if desc_data else engine_config
            
            all_content[engine_config] = {
                'name': engine_name,
                'config': engine_config,
                'description': {
                    'title': f'{engine_name} Description',
                    'body': description_html
                },
                'parameters': {
                    'title': f'{engine_name} Parameters',
                    'body': parameters_html
                }
            }
        
        print(f"✅ Successfully processed {len(all_content)} engines")
        return all_content
    
    def update_webapp_engines_json(self, content_data: Dict[str, Dict[str, str]], 
                                 output_path: str = "webapp/engines.json"):
        """Update the webapp engines.json with the generated content."""
        output_file = Path(output_path)
        
        # Start with fresh data using actual engine names as keys
        new_data = {}
        
        print(f"\n📝 Creating webapp engines.json with engine names as keys...")
        
        updated_count = 0
        
        for engine_config, engine_content in content_data.items():
            # Use engine config directly as the key (BCS, DS, UFOV, etc.)
            webapp_id = engine_config
            
            # Create new engine data with proper structure
            new_data[webapp_id] = {
                'name': engine_content['name'],
                'config': engine_config,
                'categories': {
                    'description': {
                        'name': 'Description',
                        'hasSubItems': False,
                        'content': engine_content['description']
                    },
                    'parameters': {
                        'name': 'Parameters',
                        'hasSubItems': False,
                        'content': engine_content['parameters']
                    }
                }
            }
            
            updated_count += 1
            print(f"   ✅ Updated {webapp_id} ({engine_config})")
        
        # Save new engines.json with proper engine names as keys
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎯 Successfully updated {updated_count} engines in {output_file}")
        
        # Also generate individual parameter HTML files
        self.generate_parameter_html_files(content_data)
        
        return output_file
    
    def generate_parameter_html_files(self, content_data):
        """Generate individual HTML files for each engine's parameters."""
        pages_dir = Path("webapp/pages/parameters")
        pages_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📄 Generating parameter HTML files...")
        
        for engine_config, engine_content in content_data.items():
            # Create HTML file for this engine's parameters
            html_filename = f"{engine_config}_parameters.html"
            html_path = pages_dir / html_filename
            
            # Get the parameters content
            if 'parameters' in engine_content and 'body' in engine_content['parameters']:
                parameters_content = engine_content['parameters']['body']
            else:
                parameters_content = '<p>No parameters available</p>'
            
            # Create complete HTML document
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{engine_content['name']} Parameters - Behaverse Assessment</title>
    <link rel="stylesheet" href="../../css/parameters.css">
</head>
<body>
{parameters_content}
</body>
</html>"""
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"   ✅ Generated {html_filename}")
        
        print(f"📁 Parameter HTML files saved to: {pages_dir}")


def main():
    """Main function to run the Excel extraction and webapp update."""
    print("=" * 70)
    print("BEHAVERSE EXCEL EXTRACTOR")
    print("=" * 70)
    print("Extracting content from Task spec.xlsx for webapp generation")
    print()
    
    try:
        # Initialize extractor
        extractor = ExcelExtractor()
        
        # Generate content for all engines
        content_data = extractor.generate_all_engines_content()
        
        # Update webapp engines.json
        output_file = extractor.update_webapp_engines_json(content_data)
        
        print(f"\n🚀 Content extraction completed successfully!")
        print(f"📁 Updated file: {output_file}")
        print(f"🔢 Processed engines: {len(content_data)}")
        print(f"\n📖 Next steps:")
        print(f"   1. Start the webapp: cd webapp && python3 -m http.server 8000")
        print(f"   2. Test the updated content at http://localhost:8000")
        print(f"   3. Verify glossary appears at top of parameters pages")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)