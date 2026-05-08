#!/usr/bin/env python3
"""
Clean Timeline HTML Generator - Matches main app styling

Creates a clean, professional HTML page for timeline display without colors or emojis.
Focuses on XCIT_OC_01 timeline with proper hierarchical indentation.
"""

import json
import re
import yaml
from pathlib import Path
import os

class CleanTimelineResolver:
    def __init__(self, config_path: str, locales_path: str, images_path: str):
        """Initialize with paths to config, locales, and images."""
        self.config_path = Path(config_path)
        self.locales_path = Path(locales_path)
        self.images_path = Path(images_path)
        self.config = self._load_config()
        self.localization = self._load_localization()
        self.resolved_blocks = {}
        
    def _load_config(self) -> dict:
        """Load and parse the JSON config file."""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove C-style comments
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        return json.loads(content)
    
    def _load_localization(self) -> dict:
        """Load the English localization file."""
        en_file = self.locales_path / "Locales" / "en.yaml"
        if en_file.exists():
            with open(en_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def resolve_text_reference(self, text_ref: str) -> str:
        """Resolve a text reference to actual text."""
        if '.' not in text_ref:
            return text_ref
            
        parts = text_ref.split('.')
        current = self.localization
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return f"[Missing: {text_ref}]"
                
        return str(current) if current else f"[Empty: {text_ref}]"
    
    def find_image_path(self, image_ref: str) -> str:
        """Find the actual path to an image reference."""
        image_file = self.images_path / f"{image_ref}.png"
        if image_file.exists():
            return str(image_file)
        return f"[Image not found: {image_ref}]"
    
    def resolve_block_inheritance(self, block_name: str) -> dict:
        """Resolve inheritance for a specific block."""
        if block_name in self.resolved_blocks:
            return self.resolved_blocks[block_name]
            
        blocks = self.config.get('Blocks', {})
        if block_name not in blocks:
            return {}
            
        block = blocks[block_name].copy()
        
        if 'Inherits' in block:
            parent_name = block['Inherits']
            parent_block = self.resolve_block_inheritance(parent_name)
            
            merged_block = parent_block.copy()
            
            if 'Parameters' in merged_block and 'Parameters' in block:
                merged_block['Parameters'].update(block['Parameters'])
            elif 'Parameters' in block:
                merged_block['Parameters'] = block['Parameters']
                
            # Handle Adapt field separately
            if 'Adapt' in merged_block and 'Adapt' in block:
                # If both parent and child have Adapt, use the child's version
                merged_block['Adapt'] = block['Adapt']
            elif 'Adapt' in block:
                merged_block['Adapt'] = block['Adapt']
                
            for key, value in block.items():
                if key != 'Inherits' and key != 'Parameters' and key != 'Adapt':
                    merged_block[key] = value
                    
            block = merged_block
            
        self.resolved_blocks[block_name] = block
        return block
    
    def extract_timeline_content(self, timeline_name: str) -> dict:
        """Extract and resolve content for a specific timeline."""
        timelines = self.config.get('Timelines', {})
        if timeline_name not in timelines:
            return {}
            
        timeline = timelines[timeline_name].copy()
        
        if 'blocks' in timeline:
            processed_blocks = []
            for block in timeline['blocks']:
                processed_block = block.copy()
                
                if 'timeline' in block:
                    referenced_timeline = self.extract_timeline_content(block['timeline'])
                    processed_block['_resolved_timeline'] = referenced_timeline
                
                if 'name' in block:
                    resolved_block = self.resolve_block_inheritance(block['name'])
                    processed_block['_resolved_block'] = resolved_block
                    
                processed_blocks.append(processed_block)
            timeline['blocks'] = processed_blocks
            
        return timeline

class CleanHTMLGenerator:
    def __init__(self, resolver: CleanTimelineResolver):
        self.resolver = resolver
        
    def generate_html_page(self, timeline_name: str, output_path: str):
        """Generate a clean HTML page for the timeline."""
        timeline = self.resolver.extract_timeline_content(timeline_name)
        
        if not timeline:
            print(f"Timeline '{timeline_name}' not found")
            return
        
        html_content = self._build_html_page(timeline_name, timeline)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"Clean HTML generated: {output_path}")
    
    def _get_collapsible_js(self) -> str:
        return '''
        <script>
        function toggleSection(sectionId) {
            var section = document.getElementById(sectionId);
            var content = document.getElementById('content-' + sectionId);
            var icon = document.getElementById('icon-' + sectionId);
            if (section.classList.contains('collapsed')) {
                section.classList.remove('collapsed');
                content.style.display = '';
                icon.innerHTML = '<span class="circle-open">○</span>'; // Empty circle for expanded
            } else {
                section.classList.add('collapsed');
                content.style.display = 'none';
                icon.innerHTML = '<span class="circle-closed">●</span>'; // Filled circle for collapsed
            }
        }
        window.addEventListener('DOMContentLoaded', function() {
            // Start with all sections expanded
            var sections = document.querySelectorAll('.collapsible-section');
            sections.forEach(function(section) {
                var content = section.querySelector('.collapsible-content');
                var icon = section.querySelector('.collapse-icon');
                if (content) content.style.display = '';
                if (icon) icon.innerHTML = '<span class="circle-open">○</span>'; // Empty circle for expanded
            });
        });
        </script>
        '''
    
    def _get_clean_css(self) -> str:
        """Return the clean CSS styling."""
        return '''
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.4; /* Reduced line height */
            color: #333;
            background: #f8f9fa;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 10px; /* Reduced padding */
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            min-height: 100vh;
        }
        
        .page-header {
            border-bottom: 1px solid #e9ecef;
            padding-bottom: 10px; /* Reduced padding */
            margin-bottom: 15px; /* Reduced margin */
        }
        
        .page-header h1 {
            font-size: 22px; /* Slightly smaller font */
            font-weight: 600;
            margin-bottom: 3px; /* Reduced margin */
            color: #212529;
        }
        
        .subtitle {
            color: #6c757d;
            font-size: 14px;
        }
        
        .timeline-section {
            margin-bottom: 20px; /* Reduced margin */
            border: 1px solid #dee2e6;
            border-radius: 4px;
        }
        
        .main-section {
            margin-bottom: 25px; /* Reduced margin */
            border: 1px solid #dee2e6;
            border-radius: 6px;
        }
        
        .main-section-number {
            font-weight: 700;
            color: #495057;
            font-size: 20px;
        }
        
        .main-section-header h2 {
            font-size: 20px;
            font-weight: 600;
            color: #212529;
            margin: 0;
        }
        
        .main-section-content {
            padding: 15px; /* Reduced padding */
        }
        
        .subsection {
            margin-bottom: 15px; /* Reduced margin */
            border: 1px solid #e9ecef;
            border-radius: 4px;
            background: #fdfdfd;
        }
        
        .subsection:last-child {
            margin-bottom: 0;
        }
        
        .subsection-header {
            background: #f1f3f4;
            padding: 10px 15px; /* Reduced padding */
            border-bottom: 1px solid #e9ecef;
            display: flex;
            align-items: center;
            gap: 8px; /* Reduced gap */
        }
        
        .subsection-number {
            font-weight: 600;
            color: #6c757d;
            font-size: 16px;
        }
        
        .subsection-header h3 {
            font-size: 16px;
            font-weight: 500;
            color: #495057;
            margin: 0;
        }
        
        .subsection-content {
            padding: 12px; /* Reduced padding */
        }
        
        .instruction-item {
            margin-bottom: 15px; /* Reduced margin */
            padding-bottom: 10px; /* Reduced padding */
            border-bottom: 1px solid #f1f3f4;
            display: flex;
            align-items: flex-start;
            gap: 10px; /* Reduced gap */
        }
        
        .instruction-item:last-child {
            border-bottom: none;
            margin-bottom: 0;
        }
        
        .instruction-number {
            font-size: 14px;
            font-weight: 600;
            color: #6c757d;
            flex-shrink: 0;
            width: 40px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding-top: 2px;
        }
        
        .number-circle {
            background: #adb5bd;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
        }
        
        .instruction-content {
            flex: 1;
            min-width: 0;
        }
        
        .instruction-image {
            margin: 15px 0;
            text-align: center;
        }
        
        .instruction-image img {
            max-width: 100%;
            height: auto;
            border: 1px solid #dee2e6;
            border-radius: 4px;
        }
        
        .content-heading {
            font-size: 16px;
            font-weight: 600;
            color: #212529;
            margin-bottom: 10px;
        }
        
        .instruction-text {
            color: #495057;
            margin-bottom: 10px;
        }
        
        .test-rules, .test-exit-rules, .test-adapt-rules, .test-parameters {
            margin-bottom: 25px;
        }
        
        .rules-header, .params-header, .exit-header, .adapt-header {
            display: flex;
            align-items: center;
            cursor: pointer;
            user-select: none;
            padding-bottom: 5px;
            margin-bottom: 15px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .rules-header h4, .params-header h4, .exit-header h4, .adapt-header h4 {
            font-size: 16px;
            font-weight: 600;
            color: #212529;
            margin: 0;
            padding: 0;
        }
        
        .rules-content {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            border-left: 3px solid #dee2e6;
        }
        
        .rule-heading {
            font-size: 16px;
            font-weight: 600;
            color: #212529;
            margin-bottom: 15px;
        }
        
        .rule-text {
            color: #495057;
            margin-bottom: 15px;
        }
        
        .rule-text:last-child {
            margin-bottom: 0;
        }
        
        .indent-0 {
            margin-left: 0;
        }
        
        .indent-1 {
            margin-left: 20px;
        }
        
        .indent-2 {
            margin-left: 40px;
        }
        
        .indent-3 {
            margin-left: 60px;
        }
        
        .rule-image {
            margin: 15px 0;
            text-align: center;
        }
        
        .rule-image img {
            max-width: 100%;
            height: auto;
            border: 1px solid #dee2e6;
            border-radius: 4px;
        }
        
        .parameters-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 5px; /* Reduced margin */
        }
        
        .parameters-table tr {
            border-bottom: 1px solid #f1f3f4;
        }
        
        .parameters-table tr:last-child {
            border-bottom: none;
        }
        
        .param-name {
            font-weight: 600;
            color: #495057;
            padding: 8px 10px 8px 0; /* Reduced padding */
            vertical-align: top;
            width: 30%;
            min-width: 150px;
            text-align: right;
        }
        
        .param-value {
            color: #6c757d;
            padding: 8px 0; /* Reduced padding */
            vertical-align: top;
        }
        
        .param-dict {
            margin: 0;
        }
        
        .param-dict-item {
            padding: 2px 0; /* Reduced padding */
            margin-left: 15px;
        }
        
        .param-list {
            margin: 0;
        }
        
        .param-list-item {
            padding: 3px 0;
            margin-left: 0;
            display: flex;
            align-items: flex-start;
            gap: 8px;
        }
        
        .param-list-item .param-val {
            flex: 1;
            margin-left: 10px;
        }
        
        .param-list-item .param-val .param-dict {
            margin-left: 0;
        }
        
        .param-key {
            font-weight: 500;
            color: #495057;
        }
        
        .param-index {
            font-weight: 600;
            color: #495057;
            font-family: monospace;
            flex-shrink: 0;
        }
        
        .param-val {
            color: #6c757d;
        }
        
        .param-simple {
            color: #6c757d;
        }
        
        .page-footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            text-align: center;
        }
        
        .page-footer p {
            color: #6c757d;
            font-size: 12px;
        }
        '''
    
    def _build_html_page(self, timeline_name: str, timeline_data: dict) -> str:
        """Build the complete HTML page content."""
        content_html = self._build_timeline_content(timeline_name, timeline_data)
        return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{timeline_name} - Timeline Content</title>
    <style>
        {self._get_clean_css()}
        .main-section-header {{
            background: #f8f9fa;
            padding: 12px 15px;
            border-bottom: 2px solid #dee2e6;
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            user-select: none;
        }}
        .subsection-header {{
            background: #f1f3f4;
            padding: 8px 12px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            user-select: none;
        }}
        .collapse-icon {{
            margin-right: 8px;
            transition: none;
            min-width: 20px;
            text-align: center;
        }}
        /* Closed circle (filled) */
        .circle-closed {{
            font-size: 16px;
            font-weight: bold;
        }}
        /* Open circle (empty) - much larger and thicker */
        .circle-open {{
            font-size: 26px; /* Twice as large */
            font-weight: 900; /* Extra bold */
            text-stroke: 1px black; /* For webkit browsers */
            -webkit-text-stroke: 1px black; /* For webkit browsers */
            text-shadow: 0 0 2px black; /* Thicker shadow for all browsers */
            line-height: 0.8; /* Adjust line height to better align vertically */
        }}
        .collapsible-section.collapsed .collapsible-content {{
            display: none;
        }}
    </style>
    {self._get_collapsible_js()}
</head>
<body>
    <div class=\"container\">
        <header class=\"page-header\">
            <h1>{timeline_name}</h1>
            <div class=\"subtitle\">Useful Field of View Test - Timeline Content</div>
        </header>
        {content_html}
    </div>
</body>
</html>"""
    
    def _build_timeline_content(self, timeline_name: str, timeline_data: dict) -> str:
        """Build the main timeline content grouped by main sections."""
        blocks = timeline_data.get('blocks', [])
        content_html = '<div class="timeline-content">'
        
        # Group blocks by main sections (Tutorial, Practice, Test)
        sections = {
            'Tutorial': [],
            'Practice': [], 
            'Test': []
        }
        
        for block in blocks:
            if 'timeline' in block:
                timeline_ref = block['timeline']
                if 'Tutorial' in timeline_ref:
                    sections['Tutorial'].append(block)
                elif 'Practice' in timeline_ref:
                    sections['Practice'].append(block)
                elif 'Test' in timeline_ref:
                    sections['Test'].append(block)
            elif 'name' in block:
                block_name = block['name']
                if 'Tutorial' in block_name:
                    sections['Tutorial'].append(block)
                elif 'Practice' in block_name:
                    sections['Practice'].append(block)
                elif 'Test' in block_name:
                    sections['Test'].append(block)
        
        # Build content for each main section (collapsible)
        section_counter = 1
        for section_name in ['Tutorial', 'Practice', 'Test']:
            if sections[section_name]:
                section_id = f"main-section-{section_counter}"
                
                # Get the proper section title from the timeline name and section
                section_title = f"{timeline_name}_{section_name}"
                # Check if this section exists in localization, if not, try to find a representative block's title
                if section_name == 'Test':
                    # For Test section, look for the first Test block's title pattern
                    test_blocks = [b for b in sections[section_name] if 'timeline' in b]
                    if test_blocks:
                        first_timeline = test_blocks[0]['timeline']
                        # Extract the base test name (e.g., XCIT_BCS_02_Test_01 becomes XCIT_BCS_02_Test)
                        section_title = first_timeline.rsplit('_', 1)[0] if '_' in first_timeline else section_title
                
                content_html += f'''
        <section class="main-section collapsible-section" id="{section_id}">
            <div class="main-section-header collapsible-header" onclick="toggleSection('{section_id}')">
                <span class="collapse-icon" id="icon-{section_id}">−</span>
                <span class="main-section-number">{section_counter}.</span>
                <h2>{section_title}</h2>
            </div>
            <div class="main-section-content collapsible-content" id="content-{section_id}">
        '''
                subsection_counter = 1
                for block in sections[section_name]:
                    if 'timeline' in block:
                        content_html += self._build_subsection(subsection_counter, block, 'Instructions', section_counter)
                    elif 'name' in block:
                        content_html += self._build_subsection(subsection_counter, block, 'Test Block', section_counter)
                    subsection_counter += 1
                content_html += '</div></section>'
                section_counter += 1
        content_html += '</div>'
        return content_html
    
    def _build_subsection(self, subsection_num: int, block: dict, section_type: str, parent_section: int) -> str:
        """Build a subsection within a main section."""
        if 'timeline' in block:
            timeline_ref = block['timeline']
            # Use the full timeline reference name from the config
            subsection_name = timeline_ref
        elif 'name' in block:
            # Use the full name from the config
            subsection_name = block['name']
        else:
            subsection_name = section_type
        
        subsection_id = f"subsection-{parent_section}-{subsection_num}"
        subsection_html = f'''
        <div class="subsection collapsible-section" id="{subsection_id}">
            <div class="subsection-header collapsible-header" onclick="toggleSection('{subsection_id}')">
                <span class="collapse-icon" id="icon-{subsection_id}">−</span>
                <span class="subsection-number">{subsection_num}.</span>
                <h3>{subsection_name}</h3>
            </div>
            <div class="subsection-content collapsible-content" id="content-{subsection_id}">
        '''
        
        if 'timeline' in block:
            subsection_html += self._build_instruction_content_for_subsection(block)
        elif 'name' in block:
            subsection_html += self._build_test_content_for_subsection(block)
            
        subsection_html += '</div></div>'
        return subsection_html
    
    def _build_instruction_content_for_subsection(self, block: dict) -> str:
        """Build instruction content for a subsection."""
        content_html = ''
        resolved = block.get('_resolved_timeline', {})
        
        if 'blocks' in resolved:
            for resolved_block in resolved['blocks']:
                if 'Instructions' in resolved_block:
                    instructions = resolved_block['Instructions']
                    
                    for j, instruction in enumerate(instructions, 1):
                        content_html += f'<div class="instruction-item">'
                        content_html += f'<div class="instruction-number"><span class="number-circle">{j}</span></div>'
                        content_html += f'<div class="instruction-content">'
                        
                        content = instruction.get('Content', [])
                        for content_item in content:
                            if 'Text' in content_item:
                                text_ref = content_item['Text']
                                resolved_text = self.resolver.resolve_text_reference(text_ref)
                                heading = content_item.get('heading')
                                
                                if heading == 2:
                                    content_html += f'<h4 class="content-heading">{resolved_text}</h4>'
                                else:
                                    clean_text = resolved_text.replace('\\n', '<br>').replace('\n<br>', '<br>')
                                    content_html += f'<div class="instruction-text">{clean_text}</div>'
                            
                            if 'Image' in content_item:
                                img_ref = content_item['Image']
                                # Use only the image reference - path will be fixed in post-processing
                                # Make sure to include the .png extension
                                content_html += f'<div class="instruction-image"><img src="Images/{img_ref}.png" alt="{img_ref}" /></div>'
                        
                        content_html += '</div></div>'  # Close instruction-content and instruction-item
        
        return content_html
    
    def _build_test_content_for_subsection(self, block: dict) -> str:
        """Build test content for a subsection."""
        content_html = ''
        resolved_block = block.get('_resolved_block', {})
        
        # Add rules if available
        rules_name = block.get('rulesName')
        if rules_name:
            # Create a unique ID for this rules section
            rules_id = f"rules-{block.get('name', 'section').replace('.', '-')}"
            content_html += f'''
            <div class="test-rules collapsible-section" id="{rules_id}">
                <div class="rules-header collapsible-header" onclick="toggleSection('{rules_id}')">
                    <span class="collapse-icon" id="icon-{rules_id}">−</span>
                    <h4>Game Rules</h4>
                </div>
                <div class="rules-content-wrapper collapsible-content" id="content-{rules_id}">'''
                
            # Get the actual rules content from the config
            rules_section = self.resolver.config.get('Rules', {})
            if rules_name in rules_section:
                rules_content = rules_section[rules_name]
                content_html += self._build_rules_content(rules_content)
            else:
                content_html += f'<p>Rules "{rules_name}" not found in configuration.</p>'
            content_html += '</div></div>'
        
        # Add exit rules if available
        exit_rules = block.get('exitRules')
        if exit_rules:
            # Create a unique ID for this exit rules section
            exit_id = f"exit-{block.get('name', 'section').replace('.', '-')}"
            content_html += f'''
            <div class="test-exit-rules collapsible-section" id="{exit_id}">
                <div class="exit-header collapsible-header" onclick="toggleSection('{exit_id}')">
                    <span class="collapse-icon" id="icon-{exit_id}">−</span>
                    <h4>exitRules</h4>
                </div>
                <div class="exit-content-wrapper collapsible-content" id="content-{exit_id}">
                <table class="parameters-table">'''
                
            for i, rule in enumerate(exit_rules):
                content_html += f'<tr><td class="param-name">[{i}]</td><td class="param-value">{self._format_parameter_value(rule)}</td></tr>'
            content_html += '</table></div></div>'
        
        # Get the block name
        block_name = block.get('name', '')
        
        # Initialize adapt_rules
        adapt_rules = None
        
        # Try to get the Adapt field from the resolved block
        if resolved_block and 'Adapt' in resolved_block:
            adapt_rules = resolved_block.get('Adapt')
        
        # If not found in resolved_block, try looking directly in the Blocks section of the config
        if not adapt_rules and block_name:
            blocks_section = self.resolver.config.get('Blocks', {})
            if block_name in blocks_section and 'Adapt' in blocks_section[block_name]:
                adapt_rules = blocks_section[block_name].get('Adapt')
                
        # If adapt rules are available and it's a non-empty list, add them to the HTML
        if adapt_rules is not None and isinstance(adapt_rules, list) and len(adapt_rules) > 0:
            # Create a unique ID for this adapt rules section
            adapt_id = f"adapt-{block.get('name', 'section').replace('.', '-')}"
            content_html += f'''
            <div class="test-adapt-rules collapsible-section" id="{adapt_id}">
                <div class="adapt-header collapsible-header" onclick="toggleSection('{adapt_id}')">
                    <span class="collapse-icon" id="icon-{adapt_id}">−</span>
                    <h4>Adapt</h4>
                </div>
                <div class="adapt-content-wrapper collapsible-content" id="content-{adapt_id}">
                <table class="parameters-table">'''
                
            for i, rule in enumerate(adapt_rules):
                content_html += f'<tr><td class="param-name">[{i}]</td><td class="param-value">{self._format_parameter_value(rule)}</td></tr>'
            content_html += '</table></div></div>'
        
        # Removed duplicate code for adapt rules
        
        # Add parameters
        if 'Parameters' in resolved_block:
            # Create a unique ID for this parameters section
            params_id = f"params-{block.get('name', 'section').replace('.', '-')}"
            content_html += f'''
            <div class="test-parameters collapsible-section" id="{params_id}">
                <div class="params-header collapsible-header" onclick="toggleSection('{params_id}')">
                    <span class="collapse-icon" id="icon-{params_id}">−</span>
                    <h4>Parameters</h4>
                </div>
                <div class="params-content-wrapper collapsible-content" id="content-{params_id}">
                <table class="parameters-table">'''
                
            parameters = resolved_block['Parameters']
            for param_key, param_value in parameters.items():
                content_html += f'<tr>'
                content_html += f'<td class="param-name">{param_key}</td>'
                content_html += f'<td class="param-value">{self._format_parameter_value(param_value)}</td>'
                content_html += f'</tr>'
            content_html += '</table></div></div>'
        
        return content_html
    
    def _format_parameter_value(self, value) -> str:
        """Format parameter values with proper structure for complex data types."""
        # Handle string representations of dictionaries/lists
        if isinstance(value, str):
            # Try to parse dict-like strings
            if value.strip().startswith('{') and value.strip().endswith('}'):
                try:
                    import ast
                    parsed_value = ast.literal_eval(value)
                    return self._format_parameter_value(parsed_value)  # Recursive call
                except (ValueError, SyntaxError):
                    pass
            # Try to parse list-like strings
            elif value.strip().startswith('[') and value.strip().endswith(']'):
                try:
                    import ast
                    parsed_value = ast.literal_eval(value)
                    return self._format_parameter_value(parsed_value)  # Recursive call
                except (ValueError, SyntaxError):
                    pass
        
        if isinstance(value, dict):
            formatted = '<div class="param-dict">'
            for key, val in value.items():
                formatted += f'<div class="param-dict-item">'
                formatted += f'<span class="param-key">{key}:</span> '
                formatted += f'<span class="param-val">{self._format_parameter_value(val)}</span>'  # Recursive
                formatted += f'</div>'
            formatted += '</div>'
            return formatted
        elif isinstance(value, list):
            formatted = '<div class="param-list">'
            for i, item in enumerate(value):
                formatted += f'<div class="param-list-item">'
                formatted += f'<span class="param-index">[{i}]:</span> '
                formatted += f'<div class="param-val">{self._format_parameter_value(item)}</div>'  # Recursive with div for proper indentation
                formatted += f'</div>'
            formatted += '</div>'
            return formatted
        else:
            return f'<span class="param-simple">{self._format_simple_value(value)}</span>'
    
    def _format_simple_value(self, value) -> str:
        """Format simple values (strings, numbers, booleans)."""
        if isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, str):
            # Remove outer quotes if they exist and return clean string
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                return value[1:-1]
            return value
        elif value is None:
            return 'null'
        else:
            return str(value)
    
    def _build_instruction_content_simple(self, block: dict) -> str:
        """Build simplified instruction content for phase grouping."""
        content_html = '<div class="phase-instructions">'
        
        resolved = block.get('_resolved_timeline', {})
        if 'blocks' in resolved:
            for resolved_block in resolved['blocks']:
                if 'Instructions' in resolved_block:
                    instructions = resolved_block['Instructions']
                    
                    for instruction in instructions:
                        content = instruction.get('Content', [])
                        for content_item in content:
                            if 'Text' in content_item:
                                text_ref = content_item['Text']
                                resolved_text = self.resolver.resolve_text_reference(text_ref)
                                heading = content_item.get('heading')
                                
                                if heading == 2:
                                    content_html += f'<h4 class="phase-heading">{resolved_text}</h4>'
                                else:
                                    clean_text = resolved_text.replace('\\n', '<br>').replace('\n<br>', '<br>')
                                    content_html += f'<div class="phase-text">{clean_text}</div>'
                                    
                            if 'Image' in content_item:
                                img_ref = content_item['Image']
                                img_path = f"data/content_temp/Images/{img_ref}.png"
                                content_html += f'<div class="phase-image"><img src="{img_path}" alt="{img_ref}" /></div>'
        
        content_html += '</div>'
        return content_html
    
    def _build_test_content_simple(self, block: dict) -> str:
        """Build simplified test block content for phase grouping."""
        content_html = '<div class="phase-test">'
        
        resolved_block = block.get('_resolved_block', {})
        
        # Add rules if available
        rules_name = block.get('rulesName')
        if rules_name:
            content_html += f'<div class="test-rules"><h4>Game Rules</h4>'
            content_html += self._build_rules_content(rules_name)
            content_html += '</div>'
        
        # Add parameters
        if 'Parameters' in resolved_block:
            content_html += '<div class="test-parameters"><h4>Parameters</h4>'
            parameters = resolved_block['Parameters']
            for param_key, param_value in parameters.items():
                content_html += f'<div class="param-item">{param_key}: {param_value}</div>'
            content_html += '</div>'
        
        content_html += '</div>'
        return content_html
    
    def _build_instruction_section(self, section_num: int, block: dict) -> str:
        """Build HTML for an instruction section."""
        timeline_ref = block['timeline']
        section_html = f'''
        <section class="timeline-section">
            <div class="section-header">
                <span class="section-number">{section_num}.</span>
                <h2>Instructions</h2>
                <span class="section-ref">{timeline_ref}</span>
            </div>
            <div class="section-content">
        '''
        
        resolved = block.get('_resolved_timeline', {})
        if 'blocks' in resolved:
            for resolved_block in resolved['blocks']:
                if 'Instructions' in resolved_block:
                    instructions = resolved_block['Instructions']
                    
                    for j, instruction in enumerate(instructions, 1):
                        section_html += f'<div class="instruction-item">'
                        section_html += f'<div class="instruction-number"><span class="number-circle">{j}</span></div>'
                        section_html += f'<div class="instruction-content">'
                        
                        content = instruction.get('Content', [])
                        for content_item in content:
                            if 'Text' in content_item:
                                text_ref = content_item['Text']
                                resolved_text = self.resolver.resolve_text_reference(text_ref)
                                heading = content_item.get('heading')
                                
                                if heading == 2:
                                    section_html += f'<h3 class="content-heading">{resolved_text}</h3>'
                                else:
                                    # Clean HTML formatting
                                    clean_text = resolved_text.replace('\\n', '<br>').replace('\n<br>', '<br>')
                                    section_html += f'<div class="instruction-text">{clean_text}</div>'
                            
                            if 'Image' in content_item:
                                img_ref = content_item['Image']
                                img_path = f"data/content_temp/Images/{img_ref}.png"
                                section_html += f'<div class="instruction-image"><img src="{img_path}" alt="{img_ref}" /></div>'
                        
                        section_html += '</div>'  # Close instruction-content
                        section_html += '</div>'  # Close instruction-item
        
        section_html += '</div></section>'  # Close section-content and section
        return section_html
    
    def _build_test_section(self, section_num: int, block: dict) -> str:
        """Build HTML for a test section."""
        block_name = block['name']
        section_html = f'''
        <section class="timeline-section">
            <div class="section-header">
                <span class="section-number">{section_num}.</span>
                <h2>Test Block</h2>
                <span class="section-ref">{block_name}</span>
            </div>
            <div class="section-content">
        '''
        
        # Show rules content if available
        if 'rulesName' in block:
            rules_name = block['rulesName']
            section_html += f'<div class="test-rules">'
            section_html += f'<h4>Game Rules ({rules_name})</h4>'
            
            if rules_name in self.resolver.config.get('Rules', {}):
                rules = self.resolver.config['Rules'][rules_name]
                section_html += self._build_rules_content(rules)
                
            section_html += '</div>'
        
        # Add parameters
        if 'Parameters' in block:
            section_html += '<div class="test-parameters"><h4>Parameters</h4>'
            parameters = block['Parameters']
            for param_key, param_value in parameters.items():
                section_html += f'<div class="param-item">{param_key}: {param_value}</div>'
            section_html += '</div>'
        
        section_html += '</div></section>'  # Close section-content and section
        return section_html
    
    def _build_rules_content(self, rules_content) -> str:
        """Build HTML content for game rules."""
        content_html = '<div class="rules-content">'
        
        if isinstance(rules_content, str):
            # If rules_content is a string, treat it as plain text
            content_html += f'<p>{rules_content}</p>'
        elif isinstance(rules_content, list):
            # Keep track of heading level for proper hierarchy
            current_heading = None
            current_indent = 0
            
            # If rules_content is a list, iterate and build content
            for rule in rules_content:
                if isinstance(rule, str):
                    content_html += f'<p>{rule}</p>'
                elif isinstance(rule, dict):
                    # For dictionary items, check for special keys
                    if 'text' in rule:
                        text_value = rule['text']
                        resolved_text = self.resolver.resolve_text_reference(text_value)
                        heading_level = rule.get('heading')
                        
                        if heading_level == 2:
                            content_html += f'<h3 class="rule-heading">{resolved_text}</h3>'
                            current_heading = resolved_text
                            current_indent = 0
                        else:
                            indent_class = f'indent-{current_indent}'
                            clean_text = resolved_text.replace('\\n', '<br>').replace('\n<br>', '<br>')
                            content_html += f'<div class="rule-text {indent_class}">{clean_text}</div>'
                    
                    elif 'Image' in rule:
                        img_ref = rule['Image']
                        # Use only the image reference - path will be fixed in post-processing
                        indent_class = f'indent-{current_indent + 1}'
                        # Make sure to include the .png extension
                        content_html += f'<div class="rule-image {indent_class}"><img src="Images/{img_ref}.png" alt="{img_ref}" /></div>'
                    
                    else:
                        # For any other dictionary items, show key-value pairs
                        for key, value in rule.items():
                            content_html += f'<div class="rule-item">'
                            content_html += f'<span class="rule-key">{key}:</span> '
                            if key == 'text' or key == 'title':
                                resolved_value = self.resolver.resolve_text_reference(str(value))
                                content_html += f'<span class="rule-value">{resolved_value}</span>'
                            else:
                                content_html += f'<span class="rule-value">{value}</span>'
                            content_html += f'</div>'
        
        content_html += '</div>'
        return content_html


def main():
    """Generate the clean timeline HTML demo."""
    # Paths for the UFOV configuration
    config_path = "data/content_temp/Configs/BCS.json"
    locales_path = "data/content_temp"
    images_path = "data/content_temp/Images"
    
    # Create resolver and generator
    resolver = CleanTimelineResolver(config_path, locales_path, images_path)
    generator = CleanHTMLGenerator(resolver)
    
    # Generate the HTML page
    output_path = "clean_timeline_demo.html"
    generator.generate_html_page("XCIT_BCS_02", output_path)

if __name__ == "__main__":
    main()
