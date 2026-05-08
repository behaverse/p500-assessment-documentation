#!/usr/bin/env python3

import json
import os
import yaml
import pandas as pd
from pathlib import Path

class EnhancedTimelineResolver:
    """Enhanced resolver that captures ALL timeline information including images and inheritance"""
    
    def __init__(self, config_dir, localization_file):
        self.config_dir = Path(config_dir)
        self.localization = self._load_localization(localization_file)
        self.configs = {}
        self.load_all_configs()
    
    def _load_localization(self, localization_file):
        """Load localization strings"""
        try:
            with open(localization_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load localization file {localization_file}: {e}")
            return {}
    
    def load_timeline_descriptions(self):
        """Load timeline descriptions from the Excel file"""
        descriptions = {}
        excel_path = Path("content/timeline_names.xlsx")
        
        try:
            if excel_path.exists():
                df = pd.read_excel(excel_path, sheet_name="names")
                
                # Create a mapping from timeline name to description
                for _, row in df.iterrows():
                    timeline = row.get('timeline', '').strip()
                    description = row.get('description', '').strip()
                    
                    # Clean up description (remove extra whitespace and newlines)
                    if description and description != 'nan':
                        description = ' '.join(description.split())
                        descriptions[timeline] = description
                
                print(f"✓ Loaded {len(descriptions)} timeline descriptions from Excel file")
            else:
                print(f"Warning: Timeline descriptions file not found at {excel_path}")
                
        except Exception as e:
            print(f"Warning: Could not load timeline descriptions: {e}")
            
        return descriptions
    
    def _clean_json_comments(self, content):
        """Remove C-style comments from JSON content using proven regex approach"""
        import re
        
        # Remove C-style comments using the working approach from timeline demo
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        return content
    
    def load_all_configs(self):
        """Load all timeline configuration files"""
        for config_file in self.config_dir.glob("*.json"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = self._clean_json_comments(f.read())
                    config = json.loads(content)
                    self.configs[config_file.stem] = config
            except Exception as e:
                print(f"Warning: Could not load config {config_file}: {e}")
    
    def get_localized_text(self, key):
        """Get localized text for a key"""
        if not key or not self.localization:
            return key or ""
        
        parts = key.split('.')
        current = self.localization
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return key  # Return original key if not found
        
        return str(current) if current is not None else key
    
    def resolve_block_inheritance(self, config, block_name):
        """Resolve complete block inheritance chain with all parameters and inheritance tracking"""
        if block_name not in config.get('Blocks', {}):
            return {}
        
        resolved = {}
        inheritance_chain = []
        inheritance_details = {}
        
        def resolve_recursive(name, visited=None):
            if visited is None:
                visited = set()
            
            if name in visited:
                print(f"Warning: Circular inheritance detected for block {name}")
                return {}
            
            visited.add(name)
            blocks = config.get('Blocks', {})
            
            if name not in blocks:
                return {}
            
            block = blocks[name]
            inheritance_chain.append(name)
            
            # Start with inherited properties
            if 'Inherits' in block:
                parent_name = block['Inherits']
                parent_props = resolve_recursive(parent_name, visited.copy())
                
                # Track what parameters come from the parent
                parent_params = parent_props.get('Parameters', {})
                if parent_params:
                    inheritance_details[parent_name] = {}
                    for key, value in parent_params.items():
                        inheritance_details[parent_name][key] = {
                            'value': value,
                            'overridden': False  # Will be updated if overridden
                        }
                
                for key, value in parent_props.items():
                    resolved[key] = value
            
            # Override with current block properties
            current_params = block.get('Parameters', {})
            for key, value in block.items():
                if key != 'Inherits':
                    # Special handling for Parameters to merge properly
                    if key == 'Parameters' and 'Parameters' in resolved:
                        # Merge parameters and mark overridden ones
                        merged_params = resolved['Parameters'].copy()
                        for param_name, param_value in value.items():
                            # Check if this parameter exists in any parent level
                            for level_name, level_params in inheritance_details.items():
                                if param_name in level_params:
                                    level_params[param_name]['overridden'] = True
                            # Add/override the parameter
                            merged_params[param_name] = param_value
                        resolved[key] = merged_params
                    else:
                        resolved[key] = value
            
            return resolved
        
        result = resolve_recursive(block_name)
        
        # Add inheritance tracking information to the resolved block
        result['_inheritance_chain'] = inheritance_chain
        result['_inheritance_details'] = inheritance_details
        
        return result
    
    def resolve_timeline(self, engine_id, timeline_id):
        """Resolve complete timeline with all blocks, parameters, and inheritance"""
        if engine_id not in self.configs:
            return None
        
        config = self.configs[engine_id]
        timelines = config.get('Timelines', {})
        
        if timeline_id not in timelines:
            return None
        
        timeline = timelines[timeline_id]
        resolved_blocks = []
        
        for block in timeline.get('blocks', []):
            if 'timeline' in block:
                # This is an instruction timeline reference
                instruction_timeline_name = block['timeline']
                if instruction_timeline_name in timelines:
                    instruction_timeline = timelines[instruction_timeline_name]
                    resolved_block = {
                        '_original_name': instruction_timeline_name,
                        '_type': 'instruction_timeline',
                        '_instruction_data': instruction_timeline
                    }
                    resolved_blocks.append(resolved_block)
                else:
                    # Timeline not found
                    resolved_block = {
                        '_original_name': instruction_timeline_name,
                        '_type': 'unknown',
                        '_instruction_data': None
                    }
                    resolved_blocks.append(resolved_block)
            else:
                # This is a test block with parameters
                block_name = block.get('name')
                if block_name:
                    resolved_block = self.resolve_block_inheritance(config, block_name)
                    resolved_block['_original_name'] = block_name
                    resolved_block['_type'] = 'test_block'
                    resolved_block['_rules_name'] = block.get('rulesName')
                    
                    # Add all timeline-level parameters to the resolved block
                    for key, value in block.items():
                        if key not in ['name']:  # Don't override the resolved block name
                            resolved_block[key] = value
                    
                    resolved_blocks.append(resolved_block)
                else:
                    resolved_blocks.append(block)
        
        return {
            'id': timeline_id,
            'engine': engine_id,
            'blocks': resolved_blocks,
            'config': config
        }

class EnhancedTimelineHTMLGenerator:
    """Enhanced HTML generator that includes images and all parameters"""
    
    def __init__(self, resolver):
        self.resolver = resolver
    
    def format_parameter_value(self, value, indent=0):
        """Format parameter values with proper handling of complex types"""
        if isinstance(value, dict):
            items = []
            for k, v in value.items():
                formatted_value = self.format_parameter_value(v, indent + 1)
                items.append(f'<div class="param-dict-item indent-{indent}"><span class="param-key">{k}:</span> {formatted_value}</div>')
            return '<div class="param-dict">' + ''.join(items) + '</div>'
        
        elif isinstance(value, list):
            items = []
            for i, item in enumerate(value):
                formatted_item = self.format_parameter_value(item, indent + 1)
                items.append(f'<div class="param-list-item"><span class="param-index">[{i}]</span><span class="param-val">{formatted_item}</span></div>')
            return '<div class="param-list">' + ''.join(items) + '</div>'
        
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        
        elif isinstance(value, (int, float)):
            return str(value)
        
        else:
            return str(value) if value is not None else 'null'
    
    def render_parameters_with_inheritance(self, block, section_counter, block_counter):
        """Render inheritance information with toggle button"""
        inheritance_chain = block.get('_inheritance_chain', [])
        inheritance_details = block.get('_inheritance_details', {})
        
        # Collect timeline-level parameters (parameters set directly on the timeline block)
        timeline_level_params = {}
        for key, value in block.items():
            if key.startswith('_'):
                continue  # Skip internal metadata
            if key in ['Parameters', 'Inherits']:
                continue  # Skip these as they're handled elsewhere
            # These are timeline-level parameters
            timeline_level_params[key] = value
        
        # Show inheritance info if we have inheritance chain OR timeline-level params
        if (not inheritance_chain or len(inheritance_chain) <= 1) and not timeline_level_params:
            return ""  # No inheritance or timeline params to show
        
        # Create inheritance chain display
        if inheritance_chain and len(inheritance_chain) > 1:
            chain_display = " → ".join(inheritance_chain)
        else:
            chain_display = "Timeline Parameters"
        
        inheritance_id = f"inheritance-details-{section_counter}-{block_counter}"
        
        html = [f'''
                <div class="inheritance-toggle-card">
                    <div class="inheritance-toggle-header">
                        <strong>Inheritance Chain:</strong> {chain_display}
                        <button class="inheritance-toggle-btn" onclick="toggleInheritanceDetails('{inheritance_id}', this)">show</button>
                    </div>
                    <div class="inheritance-details" id="{inheritance_id}" style="display: none;">''']
        
        # Generate inheritance details for each level FIRST (in inheritance order)
        for level_name, level_params in inheritance_details.items():
            if level_params:  # Only show levels that have parameters
                html.append(f'''
                        <div class="inheritance-section">
                            <h5 class="inheritance-level-header">Inherited from {level_name}</h5>
                            <table class="parameters-table inheritance-table">''')
                
                for param_name, param_info in level_params.items():
                    param_value = param_info.get('value', 'N/A')
                    is_overridden = param_info.get('overridden', False)
                    css_class = 'param-overridden' if is_overridden else ''
                    display_name = f"{param_name} (overridden)" if is_overridden else param_name
                    
                    html.append(f'''
                            <tr class="{css_class}">
                                <td class="param-name">{display_name}</td>
                                <td class="param-value">{self.format_parameter_value(param_value)}</td>
                            </tr>''')
                
                html.append('''
                            </table>
                        </div>''')
        
        # Add timeline-level parameters section LAST (final override level)
        if timeline_level_params:
            html.append(f'''
                        <div class="inheritance-section">
                            <h5 class="inheritance-level-header">Timeline Parameters</h5>
                            <table class="parameters-table inheritance-table">''')
            
            for param_name, param_value in timeline_level_params.items():
                html.append(f'''
                            <tr class="">
                                <td class="param-name">{param_name}</td>
                                <td class="param-value">{self.format_parameter_value(param_value)}</td>
                            </tr>''')
            
            html.append('''
                            </table>
                        </div>''')
        
        html.append('''
                    </div>
                </div>''')
        
        return ''.join(html)
    
    def render_instruction_content(self, content_item):
        """Render instruction content including images"""
        html = []
        
        if 'Text' in content_item:
            text = self.resolver.get_localized_text(content_item['Text'])
            if content_item.get('heading'):
                html.append(f'<h4 class="content-heading">{text}</h4>')
            else:
                html.append(f'<div class="instruction-text">{text}</div>')
        
        if 'Image' in content_item:
            image_path = content_item['Image']
            # Add .png extension if not present
            if not image_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                image_path_with_ext = image_path + '.png'
            else:
                image_path_with_ext = image_path
            html.append(f'''
            <div class="instruction-image">
                <img src="../content/images/{image_path_with_ext}" alt="Instruction image" onerror="this.style.display='none'; this.parentNode.innerHTML='<em>Image: {image_path} (not found)</em>';">
            </div>''')
        
        return ''.join(html)
    
    def render_instructions_block(self, instructions_data):
        """Render instruction blocks with proper numbering and images"""
        html = []
        instruction_counter = 1
        
        for block in instructions_data.get('blocks', []):
            for instruction in block.get('Instructions', []):
                content_items = instruction.get('Content', [])
                
                html.append(f'''
            <div class="instruction-item">
                <div class="instruction-number">
                    <span class="number-circle">{instruction_counter}</span>
                </div>
                <div class="instruction-content">''')
                
                for content_item in content_items:
                    html.append(self.render_instruction_content(content_item))
                
                html.append('''
                </div>
            </div>''')
                instruction_counter += 1
        
        return ''.join(html)
    
    def render_rules_content(self, config, rules_name):
        """Render rules with images and proper formatting"""
        rules = config.get('Rules', {}).get(rules_name, [])
        html = []
        
        for rule in rules:
            if 'text' in rule:
                text = self.resolver.get_localized_text(rule['text'])
                if rule.get('heading'):
                    html.append(f'<div class="rule-heading">{text}</div>')
                else:
                    html.append(f'<div class="rule-text">{text}</div>')
            
            if 'Image' in rule:
                image_path = rule['Image']
                # Add .png extension if not present
                if not image_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    image_path_with_ext = image_path + '.png'
                else:
                    image_path_with_ext = image_path
                html.append(f'''
                <div class="rule-image">
                    <img src="../content/images/{image_path_with_ext}" alt="Rule image" onerror="this.style.display='none'; this.parentNode.innerHTML='<em>Image: {image_path} (not found)</em>';">
                </div>''')
        
        return ''.join(html)
    
    def render_exit_rules(self, block):
        """Render exit rules if present"""
        exit_rules = block.get('ExitRules', [])
        if not exit_rules:
            return ""
        
        html = ['''
        <div class="test-exit-rules">
            <div class="exit-header">
                <h4>Exit Rules</h4>
            </div>
            <div class="exit-rules-content">''']
        
        for i, rule in enumerate(exit_rules, 1):
            html.append(f'<div class="exit-rule"><strong>Rule {i}:</strong>')
            for key, value in rule.items():
                html.append(f' {key}: {value}')
            html.append('</div>')
        
        html.append('</div></div>')
        return ''.join(html)
    
    def render_trials_info(self, block):
        """Render trials information if present"""
        trials = block.get('Trials', [])
        trial_order = block.get('TrialOrder')
        
        if not trials and not trial_order:
            return ""
        
        html = ['''
        <div class="test-trials">
            <div class="trials-header">
                <h4>Trials Configuration</h4>
            </div>''']
        
        if trial_order:
            html.append(f'<div class="trial-order"><strong>Trial Order:</strong> {self.format_parameter_value(trial_order)}</div>')
        
            if trials:
                html.append(f'<div class="trials-list"><strong>Trials ({len(trials)} total):</strong>')
                for i, trial in enumerate(trials):  # Show ALL trials, not just first 5
                    html.append(f'<div class="trial-item"><strong>Trial {i+1}:</strong> {self.format_parameter_value(trial)}</div>')
                html.append('</div>')
        
        html.append('</div>')  # Close the test-trials div
        return ''.join(html)
    
    def group_blocks_hierarchically(self, blocks, timeline_id):
        """Group blocks into hierarchical sections based on naming patterns"""
        # Extract the base timeline name (e.g., XCIT_OC_01 from XCIT_OC_01_Tutorial_Intro)
        base_name = timeline_id  # e.g., XCIT_OC_01
        
        # Group blocks by their section (Tutorial, Practice, Test, etc.)
        sections = {}
        section_order = []
        
        for block in blocks:
            block_name = block.get('_original_name', 'Unknown Block')
            
            # Extract section name from block name
            if block_name.startswith(base_name + '_'):
                # Remove base name and underscore
                remaining = block_name[len(base_name) + 1:]
                
                # Find the section name (first part before next underscore or end)
                if '_' in remaining:
                    section_name = remaining.split('_')[0]
                else:
                    section_name = remaining
                
                if section_name not in sections:
                    sections[section_name] = []
                    section_order.append(section_name)
                
                sections[section_name].append(block)
            else:
                # Handle blocks that don't follow the naming pattern
                if 'Other' not in sections:
                    sections['Other'] = []
                    if 'Other' not in section_order:
                        section_order.append('Other')
                sections['Other'].append(block)
        
        return sections, section_order
    
    def get_timeline_duration(self, timeline_id, description=""):
        """Get the duration for a timeline from the Excel file or estimate from description"""
        # Try to get duration from the loaded timeline descriptions Excel file
        excel_path = Path("content/timeline_names.xlsx")
        
        try:
            if excel_path.exists():
                df = pd.read_excel(excel_path, sheet_name="names")
                
                # Find the row for this timeline
                timeline_row = df[df['timeline'] == timeline_id]
                if not timeline_row.empty:
                    duration = timeline_row.iloc[0].get('duration', None)
                    if duration and str(duration) != 'nan' and duration != 0:
                        return str(int(duration))
                
        except Exception as e:
            print(f"Warning: Could not read duration from Excel file: {e}")
        
        # Default duration if not found in Excel
        return "5-10"

    def generate_timeline_page(self, engine_id, timeline_id, description=""):
        """Generate a complete HTML page for a specific timeline with enhanced content"""
        config = self.resolver.configs.get(engine_id)
        if not config:
            return None
        
        # Resolve the main timeline
        timeline_data = self.resolver.resolve_timeline(engine_id, timeline_id)
        if not timeline_data:
            return None

        # Start building the HTML
        html = ['''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{}</title>
    <link rel="stylesheet" href="../../../css/styles.css">
    <link rel="stylesheet" href="../../../css/parameters.css">
    <script src="../../../js/timeline.js"></script>
</head>
<body>
    <div class="container">'''.format(timeline_id)]

        # Generate the main content with hierarchical blocks
        html.append('''
    <div class="timeline-content">
        <div class="timeline-header">
            <h2>{}</h2>
            {}
        </div>
        
        
        <!-- Video/Media Section -->
        <div class="timeline-media">
            <div class="video-container">
                <video controls poster="../../../assets/engines/{}/thumbnail.jpg" preload="metadata">
                    <source src="../../../assets/engines/{}/video.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                <div class="timeline-actions">
                    <button class="test-timeline-btn" onclick="testTimeline('{}')">Test this timeline</button>
                    <span class="timeline-duration">Duration: {} minutes</span>
                </div>
            </div>
        </div>
        
        <!-- About Section -->
        <h3 class="section-title">About</h3>
        <div class="timeline-about">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>
            <p>Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.</p>
        </div>
        
        <!-- Config Section -->
        <h3 class="section-title">Config</h3>
        <div class="timeline-config"></div>'''.format(
            timeline_id,
            f'<p class="timeline-description">{description}</p>' if description else '',
            engine_id,  # for video thumbnail path
            engine_id,  # for video source path
            timeline_id,  # for test button
            self.get_timeline_duration(timeline_id, description)  # get duration
        ))
        
        # Group blocks hierarchically
        sections, section_order = self.group_blocks_hierarchically(timeline_data['blocks'], timeline_id)
        
        section_counter = 1
        
        for section_name in section_order:
            section_blocks = sections[section_name]
            
            html.append(f'''
        <section class="main-section collapsible-section" id="section-{section_counter}">
            <div class="main-section-header collapsible-header" onclick="timelineToggleSection('section-{section_counter}')">
                <span class="collapse-icon" id="icon-section-{section_counter}"></span>
                <span class="main-section-number">{section_counter}.</span>
                <h2>{section_name}</h2>
            </div>
            <div class="main-section-content collapsible-content" id="content-section-{section_counter}">''')
            
            block_counter = 1
            for block in section_blocks:
                block_name = block.get('_original_name', 'Unknown Block')
                block_type = block.get('_type', 'unknown')
                
                html.append(f'''
        <div class="block-section collapsible-section" id="block-{section_counter}-{block_counter}">
            <div class="block-header collapsible-header" onclick="timelineToggleSection('block-{section_counter}-{block_counter}')">
                <span class="collapse-icon" id="icon-block-{section_counter}-{block_counter}"></span>
                <span class="block-number">{section_counter}.{block_counter}</span>
                <h3>{block_name}</h3>
            </div>
            <div class="block-content collapsible-content" id="content-block-{section_counter}-{block_counter}">''')
                
                if block_type == 'instruction_timeline':
                    # This is an instruction timeline
                    instructions_data = block.get('_instruction_data')
                    if instructions_data:
                        # Render instruction blocks
                        instruction_counter = 1
                        for sub_block in instructions_data.get('blocks', []):
                            html.append(f'''
        <div class="instruction-section collapsible-section" id="instruction-{section_counter}-{block_counter}-{instruction_counter}">
            <div class="instruction-header collapsible-header" onclick="timelineToggleSection('instruction-{section_counter}-{block_counter}-{instruction_counter}')">
                <span class="collapse-icon" id="icon-instruction-{section_counter}-{block_counter}-{instruction_counter}"></span>
                <span class="instruction-number">{section_counter}.{block_counter}.{instruction_counter}</span>
                <h4>Instructions</h4>
            </div>
            <div class="instruction-content collapsible-content" id="content-instruction-{section_counter}-{block_counter}-{instruction_counter}">''')
                            
                            html.append(self.render_instructions_block({'blocks': [sub_block]}))
                            
                            html.append('''
            </div>
        </div>''')
                            instruction_counter += 1
                    else:
                        html.append('<div class="no-content">No instruction data found</div>')
                        
                elif block_type == 'test_block':
                    # Regular test block with parameters
                    rules_name = block.get('_rules_name')
                    
                    # Render all parameters (including inherited ones)
                    parameters = block.get('Parameters', {})
                    if parameters:
                        inheritance_html = self.render_parameters_with_inheritance(block, section_counter, block_counter)
                        html.append(f'''
        <div class="test-parameters collapsible-section" id="params-{section_counter}-{block_counter}">
            <div class="params-header collapsible-header" onclick="timelineToggleSection('params-{section_counter}-{block_counter}')">
                <span class="collapse-icon" id="icon-params-{section_counter}-{block_counter}"></span>
                <h4>Parameters</h4>
            </div>
            <div class="params-content collapsible-content" id="content-params-{section_counter}-{block_counter}">
{inheritance_html}
                <table class="parameters-table">''')
                        
                        for param_name, param_value in parameters.items():
                            html.append(f'''
                <tr>
                    <td class="param-name">{param_name}</td>
                    <td class="param-value">{self.format_parameter_value(param_value)}</td>
                </tr>''')
                        
                        html.append('''
                </table>
            </div>
        </div>''')
                    
                    # Render exit rules
                    exit_rules_html = self.render_exit_rules(block)
                    if exit_rules_html.strip():
                        html.append(f'''
        <div class="exit-rules collapsible-section" id="exit-rules-{section_counter}-{block_counter}">
            <div class="exit-rules-header collapsible-header" onclick="timelineToggleSection('exit-rules-{section_counter}-{block_counter}')">
                <span class="collapse-icon" id="icon-exit-rules-{section_counter}-{block_counter}"></span>
                <h4>Exit Rules</h4>
            </div>
            <div class="exit-rules-content collapsible-content" id="content-exit-rules-{section_counter}-{block_counter}">
{exit_rules_html}
            </div>
        </div>''')
                    
                    # Render trials information
                    trials_html = self.render_trials_info(block)
                    if trials_html.strip():
                        html.append(f'''
        <div class="trials-info collapsible-section" id="trials-{section_counter}-{block_counter}">
            <div class="trials-header collapsible-header" onclick="timelineToggleSection('trials-{section_counter}-{block_counter}')">
                <span class="collapse-icon" id="icon-trials-{section_counter}-{block_counter}"></span>
                <h4>Trials Information</h4>
            </div>
            <div class="trials-content collapsible-content" id="content-trials-{section_counter}-{block_counter}">
{trials_html}
            </div>
        </div>''')
                    
                    # Render rules if specified
                    if rules_name:
                        html.append(f'''
        <div class="test-rules collapsible-section" id="rules-{section_counter}-{block_counter}">
            <div class="rules-header collapsible-header" onclick="timelineToggleSection('rules-{section_counter}-{block_counter}')">
                <span class="collapse-icon" id="icon-rules-{section_counter}-{block_counter}"></span>
                <h4>Rules</h4>
            </div>
            <div class="rules-content collapsible-content" id="content-rules-{section_counter}-{block_counter}">
{self.render_rules_content(config, rules_name)}
            </div>
        </div>''')
                
                else:
                    # Unknown block type
                    html.append('<div class="no-content">Block type not recognized or no data available</div>')
                
                html.append('''
            </div>
        </div>''')
                block_counter += 1
            
            html.append('''
            </div>
        </section>''')
            section_counter += 1

        # Close Config section
        html.append('''
        </div>
        
        <!-- Sample Data Section -->
        <h3 class="section-title">Sample Data</h3>
        <div class="timeline-sample-data">
            <p>You can download a sample dataset <a href="#" class="sample-data-link">here</a></p>
        </div>''')

        # Close the HTML with JavaScript
        html.append('''
    </div>
    </div>
    <script>
        function timelineToggleSection(sectionId) {
            console.log('Toggling section:', sectionId);
            
            const section = document.getElementById(sectionId);
            const content = document.getElementById('content-' + sectionId);
            const icon = document.getElementById('icon-' + sectionId);
            
            if (!section || !content || !icon) {
                console.log('timelineToggleSection: Missing elements for', sectionId);
                console.log('Section:', section, 'Content:', content, 'Icon:', icon);
                return;
            }
            
            if (section.classList.contains('expanded')) {
                console.log('Collapsing section:', sectionId);
                section.classList.remove('expanded');
                content.style.display = 'none';
            } else {
                console.log('Expanding section:', sectionId);
                section.classList.add('expanded');
                content.style.display = 'block';
            }
        }

        // Note: toggleInheritanceDetails function is now defined in timeline.js

        // Initialize sections with proper default states
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Initializing timeline sections...');
            
            const sections = document.querySelectorAll('.collapsible-section');
            console.log('Found', sections.length, 'collapsible sections');
            
            sections.forEach(function(section, index) {
                // Only expand main sections by default, keep others collapsed
                if (section.classList.contains('main-section')) {
                    section.classList.add('expanded');
                    console.log('Initialized main section', section.id, 'as expanded');
                } else {
                    // Nested sections (block-section, instruction-section, etc.) start collapsed
                    section.classList.remove('expanded');
                    
                    // Explicitly hide nested content
                    const content = section.querySelector('.collapsible-content, .block-content, .instruction-content, .params-content');
                    if (content) {
                        content.style.display = 'none';
                    }
                    console.log('Initialized nested section', section.id, 'as collapsed');
                }
            });
        });
    </script>
</body>
</html>''')
        
        return ''.join(html)

def main():
    """Generate enhanced timeline pages with all content"""
    config_dir = Path("content/timeline_configs")
    localization_file = Path("content/en.yaml")
    output_dir = Path("webapp/pages/timelines")
    
    if not config_dir.exists():
        print(f"Error: Config directory {config_dir} not found")
        return
    
    if not localization_file.exists():
        print(f"Warning: Localization file {localization_file} not found")
    
    # Initialize resolver and generator
    resolver = EnhancedTimelineResolver(config_dir, localization_file)
    generator = EnhancedTimelineHTMLGenerator(resolver)
    
    # Load timeline descriptions from Excel file
    timeline_descriptions = resolver.load_timeline_descriptions()
    
    # Generate pages for all engines and their timelines
    total_pages = 0
    for engine_id, config in resolver.configs.items():
        timelines = config.get('Timelines', {})
        
        # Find main timelines (those that start with engine prefix)
        main_timelines = []
        for timeline_id in timelines.keys():
            if timeline_id.startswith('XCIT_' + engine_id.upper() + '_') and not any(
                timeline_id.endswith(suffix) for suffix in ['_Intro', '_Outro', '_Rules']
            ):
                main_timelines.append(timeline_id)
        
        if not main_timelines:
            print(f"No main timelines found for engine {engine_id}")
            continue
        
        # Create output directory for this engine
        engine_output_dir = output_dir / engine_id.lower()
        engine_output_dir.mkdir(parents=True, exist_ok=True)
        
        for timeline_id in main_timelines:
            try:
                # Get the description for this timeline
                description = timeline_descriptions.get(timeline_id, "")
                html_content = generator.generate_timeline_page(engine_id, timeline_id, description)
                if html_content:
                    output_file = engine_output_dir / f"{timeline_id.lower()}.html"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print(f"✓ Generated: {output_file}")
                    total_pages += 1
                else:
                    print(f"✗ Failed to generate content for {engine_id}:{timeline_id}")
            except Exception as e:
                import traceback
                print(f"✗ Error generating {engine_id}:{timeline_id}: {e}")
                traceback.print_exc()
    
    print(f"\n🚀 Generated {total_pages} enhanced timeline pages with complete content including images and inheritance!")

if __name__ == "__main__":
    main()