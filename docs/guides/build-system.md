# Build System Documentation

This document explains the build pipeline, template system, and how to extend the content generation system.

## Build Pipeline Overview

The build system consists of several components working together:

```
Excel Data + JSON Configs → Template Processing → HTML Generation → Webapp Data
```

## Core Components

### 1. Build Master (`scripts/build/build_master.py`)

The main orchestrator that coordinates the entire build process:

```python
# Key functions:
- Load templates from content/engines/templates/
- Extract data from Excel and JSON sources  
- Process templates with extracted data
- Generate HTML files for all engines
- Create webapp JSON data file
- Output build statistics
```

**Usage:**
```bash
python3 scripts/build/build_master.py
```

### 2. Excel Processor (`scripts/utils/excel_processor.py`)

Extracts structured data from the Excel specification file:

**Input:** `data/content_temp/Task spec.xlsx`

**Extracted data:**
- **Scenes sheet** → Engine metadata (names, descriptions, codes)
- **Parameters sheet** → Parameter definitions and specifications
- **Saved_data sheet** → Data field definitions and types
- **Justification sheet** → Timeline descriptions and metadata

**Output:** Python dictionaries with structured engine data

### 3. Template Processor (`scripts/utils/template_processor.py`)

Processes HTML templates with Mustache-style variable substitution:

**Template variables supported:**
```html
{{ENGINE_NAME}}           # Full engine name
{{ENGINE_CODE}}           # Short code (e.g., BCS)  
{{ENGINE_DESCRIPTION}}    # Engine description
{{PARAMETER_COUNT}}       # Number of parameters
{{GLOSSARY_HTML}}         # Formatted glossary entries
{{PARAMETER_SECTIONS}}    # Parameter cards HTML
{{REFERENCES_HTML}}       # References list HTML
{{NOTES_HTML}}            # Implementation notes HTML
```

**Special processing:**
- Glossary formatting with two-column layout
- Parameter card generation with styling
- Conditional content rendering (e.g., `{{#HAS_GLOSSARY}}`)

### 4. Webapp Generator (`scripts/utils/webapp_generator.py`)

Creates the JSON data file consumed by the webapp:

**Output:** `content/generated/pilot_webapp_data.json`

**Structure:**
```json
{
  "engines": [
    {
      "name": "Engine Name",
      "code": "ENG",
      "pages": {
        "description": "HTML content...",
        "parameters": "HTML content...",
        "timelines": "HTML content...",
        "data": "HTML content..."
      }
    }
  ]
}
```

## Template System

### Template Location
```
content/engines/templates/
├── description.html      # Engine descriptions with references
├── parameters.html       # Parameters, glossary, implementation notes  
├── timelines.html       # Timeline overview pages
├── timeline_detail.html # Individual timeline details
└── data.html           # Data specifications
```

### Template Syntax

**Basic Variables:**
```html
<h1>{{ENGINE_NAME}}</h1>
<p>Engine code: {{ENGINE_CODE}}</p>
```

**Conditional Content:**
```html
{{#HAS_GLOSSARY}}
<section class="parameter-section">
    <h2>Technical Glossary</h2>
    <div class="glossary-table">
        {{GLOSSARY_HTML}}
    </div>
</section>
{{/HAS_GLOSSARY}}
```

**Formatted Content:**
```html
<!-- Pre-formatted HTML content -->
<div class="parameters-cards-container">
    {{PARAMETER_SECTIONS}}
</div>
```

### Adding New Templates

1. **Create template file** in `content/engines/templates/`
2. **Use supported variables** (see template processor for full list)
3. **Add CSS styling** within `<style>` tags
4. **Update template processor** to handle new template type
5. **Rebuild content** to test changes

## Data Flow

### 1. Data Extraction
```bash
Excel File → Python Dictionaries
├── engine_data = {name, code, description, ...}
├── parameters = [{name, type, description, ...}, ...]
├── glossary = [{term, definition}, ...]
└── references = [{title, url, description}, ...]
```

### 2. Template Processing
```bash
Templates + Data → HTML Content
├── Apply variable substitutions
├── Process conditional blocks  
├── Format complex content (glossary, parameters)
└── Generate styled HTML
```

### 3. File Generation
```bash
HTML Content → File System
├── content/generated/pilot/[ENGINE]/description.html
├── content/generated/pilot/[ENGINE]/parameters.html
├── content/generated/pilot/[ENGINE]/timelines.html
└── content/generated/pilot/[ENGINE]/data.html
```

### 4. Webapp Integration
```bash
HTML Files → JSON Data
├── Extract HTML content from generated files
├── Structure as webapp-compatible JSON
├── Save as pilot_webapp_data.json
└── Copy to webapp/engines.json
```

## Extending the System

### Adding a New Engine

1. **Update Excel data:**
   - Add row to 'scenes' sheet with engine metadata
   - Add parameters to 'parameters' sheet
   - Add timeline data to 'justification' sheet (if applicable)

2. **Create JSON config** (optional):
   ```bash
   data/content_temp/Configs/NEW_ENGINE.json
   ```

3. **Rebuild content:**
   ```bash
   python3 scripts/build/build_master.py
   ```

4. **Update webapp:**
   ```bash
   cp content/generated/pilot_webapp_data.json webapp/engines.json
   ```

### Adding a New Template Type

1. **Create template file:**
   ```bash
   content/engines/templates/new_page_type.html
   ```

2. **Update template processor:**
   ```python
   # In scripts/utils/template_processor.py
   def process_new_page_type(self, engine_data):
       # Define template variables
       variables = {
           'ENGINE_NAME': engine_data['name'],
           'ENGINE_CODE': engine_data['code'],
           'CUSTOM_CONTENT': self._format_custom_content(engine_data)
       }
       return self._apply_template('new_page_type.html', variables)
   ```

3. **Update build master:**
   ```python
   # In scripts/build/build_master.py
   # Add to content generation loop
   content['new_page_type'] = processor.process_new_page_type(engine_data)
   ```

### Adding New Variables

1. **Define variable in template processor:**
   ```python
   def _get_template_variables(self, engine_data):
       return {
           'NEW_VARIABLE': self._format_new_content(engine_data),
           # ... existing variables
       }
   ```

2. **Use in templates:**
   ```html
   <div class="new-content">
       {{NEW_VARIABLE}}
   </div>
   ```

## Build Configuration

### Template Loading
Templates are automatically discovered from `content/engines/templates/`:
```python
# Templates loaded by filename (without .html extension)
loaded_templates = ['description', 'parameters', 'timelines', 'data', 'timeline_detail']
```

### Engine Selection
Currently supports all engines found in Excel data:
```python
# Engines are auto-discovered from Excel 'scenes' sheet
engines = ['BCS', 'DS', 'NB', 'WO', 'UFOV', 'TH', 'SRM', 'SOS', 'SMC', 'RE', 'BM', 'BSAC', 'MOT', 'OC', 'OOO', 'PC']
```

### Output Configuration
```python
OUTPUT_PATHS = {
    'generated_content': 'content/generated/pilot/',
    'webapp_data': 'content/generated/pilot_webapp_data.json',
    'summary': 'content/generated/pilot/generation_summary.json'
}
```

## Performance and Statistics

### Build Metrics
```
Total Engines: 16
Total Files Generated: 120 (4 main pages + variable timeline pages per engine)
Total Content Length: ~1.14M characters
Build Time: ~10-15 seconds
Template Processing: ~1-2 seconds per engine
```

### Generated File Structure
```
content/generated/pilot/
├── BCS/
│   ├── description.html (references, overview)
│   ├── parameters.html (glossary, parameters, notes)
│   ├── timelines.html (timeline overview)
│   ├── data.html (data specifications)
│   └── timelines/
│       ├── XCIT_BCS_01.html
│       ├── XCIT_BCS_02.html
│       └── ... (5 timeline files)
└── [... other engines follow same structure]
```

## Debugging and Troubleshooting

### Common Build Issues

**Template not found:**
```bash
# Check template exists
ls content/engines/templates/parameters.html

# Verify template name in build script
grep "parameters" scripts/build/build_master.py
```

**Variable substitution fails:**
```python
# Add debug output to template processor
print(f"Variables: {variables}")
print(f"Template content preview: {template_content[:100]}")
```

**Excel data extraction errors:**
```python
# Check sheet names and columns
import pandas as pd
excel_file = pd.ExcelFile('data/content_temp/Task spec.xlsx')
print(excel_file.sheet_names)
```

### Build Validation

**Check generated files:**
```bash
# Count generated files
find content/generated/pilot -name "*.html" | wc -l

# Check content length
du -sh content/generated/pilot/
```

**Validate webapp data:**
```bash
# Check JSON syntax
python3 -m json.tool content/generated/pilot_webapp_data.json > /dev/null && echo "Valid JSON"

# Check structure
jq '.engines | length' content/generated/pilot_webapp_data.json
```

## Customization Examples

### Custom Glossary Formatting

```python
# In template_processor.py
def _format_glossary(self, glossary_items):
    html_parts = []
    for item in glossary_items:
        html_parts.append(f'''
        <div class="glossary-row">
            <div class="glossary-term">{item['term']}</div>
            <div class="glossary-definition">{item['definition']}</div>
        </div>
        ''')
    return ''.join(html_parts)
```

### Custom Parameter Cards

```python
def _format_parameter_cards(self, parameters):
    cards_html = []
    for param in parameters:
        card_html = f'''
        <div class="parameter-card">
            <h3>{param['name']}</h3>
            <p><strong>Type:</strong> {param['type']}</p>
            <p><strong>Description:</strong> {param['description']}</p>
        </div>
        '''
        cards_html.append(card_html)
    return ''.join(cards_html)
```

## Future Enhancements

### Planned Features
- **Enhanced templating** with loops and more complex conditionals
- **Theme system** for consistent styling across templates
- **Validation system** for data integrity checking
- **Incremental builds** for faster development cycles
- **Plugin system** for custom content processors

### Extension Points
- **Custom data sources** beyond Excel (JSON, CSV, databases)
- **Multiple output formats** (PDF, DOCX, etc.)
- **Internationalization** support for multiple languages
- **Interactive elements** in generated content