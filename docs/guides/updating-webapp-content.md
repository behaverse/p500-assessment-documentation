# Updating Webapp Content

This guide explains how to update the content displayed in the webapp, including modifying templates, updating data sources, and rebuilding the application.

## Overview

The webapp content comes from two main sources:
1. **Static templates** in `content/engines/templates/`
2. **Generated content** in `content/generated/pilot/`
3. **Webapp data** in `webapp/engines.json`

## Step-by-Step Update Process

### 1. Modify Source Data (Optional)

If you need to update the underlying data:

```bash
# Edit the Excel file containing engine specifications
data/content_temp/Task spec.xlsx

# Or modify JSON configuration files
data/content_temp/Configs/[ENGINE_NAME].json
```

**Key Excel sheets:**
- `scenes` - Engine descriptions and metadata
- `parameters` - Parameter definitions and specifications  
- `saved_data` - Data field definitions
- `justification` - Timeline descriptions

### 2. Update HTML Templates

Templates control how content is displayed. They use Mustache-style variables:

```bash
# Main templates directory
content/engines/templates/
├── description.html      # Engine descriptions with references
├── parameters.html       # Parameters, glossary, implementation notes
├── timelines.html       # Timeline overview pages
├── timeline_detail.html # Individual timeline details
└── data.html           # Data specifications
```

**Common template variables:**
- `{{ENGINE_NAME}}` - Full engine name
- `{{ENGINE_CODE}}` - Short engine code (e.g., BCS)
- `{{GLOSSARY_HTML}}` - Formatted glossary entries
- `{{PARAMETER_SECTIONS}}` - Parameter cards HTML
- `{{REFERENCES_HTML}}` - References list

**Example template modification:**
```html
<!-- In parameters.html, modify glossary styling -->
<div class="glossary-table">
    {{GLOSSARY_HTML}}
</div>

<style>
.glossary-term {
    text-align: right;  <!-- Right-align terms -->
    border: none;       <!-- Remove borders -->
}
</style>
```

### 3. Rebuild Content

After modifying templates or source data:

```bash
# Navigate to repository root
cd /home/pedro/Repos/behaverse_assessment_documentation

# Run the main build script
python3 scripts/build/build_master.py
```

**Build process generates:**
- 120 HTML files across all engines
- Updated webapp data file (`pilot_webapp_data.json`)
- Content statistics and validation

### 4. Update Webapp

Copy the generated webapp data to the webapp directory:

```bash
# Update the webapp with new content
cp content/generated/pilot_webapp_data.json webapp/engines.json
```

**CRITICAL:** This step is required every time you rebuild content. The webapp reads from `engines.json` to display engine data.

### 5. Test Changes

Start the development server to test your changes:

```bash
# Navigate to webapp directory  
cd webapp

# Start HTTP server
python3 -m http.server 8000

# Access at http://localhost:8000
```

## File Update Reference

### Files You Should Modify

**Templates (modify these):**
- `content/engines/templates/*.html` - HTML templates for pages
- `data/content_temp/Task spec.xlsx` - Source data
- `data/content_temp/Configs/*.json` - Engine configurations

**Webapp frontend (rarely modify):**
- `webapp/index.html` - Main application HTML
- `webapp/script.js` - JavaScript application logic
- `webapp/styles.css` - CSS styling

### Files You Should NOT Modify Directly

**Generated content (auto-generated):**
- `content/generated/pilot/` - All HTML files (rebuilt automatically)
- `content/generated/pilot_webapp_data.json` - Webapp data source
- `content/generated/pilot_webapp_snippet.js` - Generated JavaScript

**These files are overwritten on every build.**

### Critical File: `webapp/engines.json`

This is the **single most important file** for webapp updates:

```bash
# Always update this after rebuilding content
cp content/generated/pilot_webapp_data.json webapp/engines.json
```

**What this file contains:**
- Engine metadata (names, descriptions, codes)
- Template content for all page types
- Parameter definitions and specifications
- Navigation structure data

## Common Update Scenarios

### Scenario 1: Update Glossary Formatting

1. **Edit template**: `content/engines/templates/parameters.html`
2. **Modify CSS**: Add/modify styles in the `<style>` section
3. **Rebuild**: `python3 scripts/build/build_master.py`
4. **Update webapp**: `cp content/generated/pilot_webapp_data.json webapp/engines.json`
5. **Test**: `cd webapp && python3 -m http.server 8000`

### Scenario 2: Add New Parameters

1. **Update Excel**: Add parameters to `data/content_temp/Task spec.xlsx`
2. **Rebuild**: `python3 scripts/build/build_master.py`
3. **Update webapp**: `cp content/generated/pilot_webapp_data.json webapp/engines.json`
4. **Test**: View new parameters in webapp

### Scenario 3: Modify Page Layout

1. **Edit template**: Modify relevant template in `content/engines/templates/`
2. **Update styles**: Add CSS in template or `webapp/styles.css`
3. **Rebuild**: `python3 scripts/build/build_master.py`
4. **Update webapp**: `cp content/generated/pilot_webapp_data.json webapp/engines.json`
5. **Test**: Check layout changes in browser

### Scenario 4: Add New Engine

1. **Add Excel data**: Add engine data to all relevant Excel sheets
2. **Add config**: Create `data/content_temp/Configs/[NEW_ENGINE].json`
3. **Rebuild**: `python3 scripts/build/build_master.py`
4. **Update webapp**: `cp content/generated/pilot_webapp_data.json webapp/engines.json`
5. **Test**: New engine should appear in webapp navigation

## Build Script Options

The build script provides detailed output:

```bash
python3 scripts/build/build_master.py

# Sample output:
# 🚀 Starting build process...
# Loaded 5 templates: ['timelines', 'description', 'timeline_detail', 'parameters', 'data']
# Extracting engine data from 'scenes' sheet...
# Extracted data for 16 engines
# ...
# ✅ Build completed successfully!
```

## Troubleshooting

### Build Fails
```bash
# Check if you're in the right directory
pwd  # Should show: .../behaverse_assessment_documentation

# Check if Excel file exists
ls data/content_temp/Task\ spec.xlsx
```

### Webapp Shows Old Content
```bash
# Make sure you updated engines.json
ls -la webapp/engines.json
cp content/generated/pilot_webapp_data.json webapp/engines.json
```

### Changes Not Visible
```bash
# Clear browser cache or open in private/incognito mode
# Restart HTTP server
pkill -f "python.*http.server"
cd webapp && python3 -m http.server 8000
```

### Template Variables Not Working
- Check variable names match exactly (case-sensitive)
- Ensure variables are wrapped in double curly braces: `{{VARIABLE_NAME}}`
- Verify the data exists in the source files

## Quick Reference Commands

```bash
# Complete update workflow
cd /home/pedro/Repos/behaverse_assessment_documentation
python3 scripts/build/build_master.py
cp content/generated/pilot_webapp_data.json webapp/engines.json
cd webapp && python3 -m http.server 8000

# Check generated content
ls content/generated/pilot/
head content/generated/pilot_webapp_data.json

# Validate JavaScript
node -c webapp/script.js

# Stop server
pkill -f "python.*http.server"
```

## Summary

**The essential steps for any content update:**

1. 🔄 **Modify**: Templates or source data
2. 🏗️ **Build**: `python3 scripts/build/build_master.py`
3. 📋 **Update**: `cp content/generated/pilot_webapp_data.json webapp/engines.json`
4. 🧪 **Test**: `cd webapp && python3 -m http.server 8000`

**Remember:** The webapp always reads from `webapp/engines.json`, so this file must be updated after every content rebuild!