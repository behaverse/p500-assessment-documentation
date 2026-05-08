# Timeline Implementation Guide

## Overview

The timeline functionality has been successfully implemented in the Behaverse Assessment Documentation webapp. This feature allows users to explore detailed timeline configurations for each assessment engine, including instructions, test blocks, rules, and parameters.

## What's Been Implemented

### 1. Timeline Manager (`js/timeline.js`)
- **TimelineManager class**: Core functionality for loading and processing timeline configurations
- **Configuration Loading**: Automatically loads timeline configs from `/content/timeline_configs/`
- **JSON Cleaning**: Handles C-style comments in JSON configuration files
- **Localization Support**: Basic YAML parsing for instruction text resolution
- **HTML Generation**: Creates rich, collapsible timeline content with proper styling

### 2. Main App Integration (`js/script.js`)
- **Timeline Navigation**: Special handling for the "timelines" category
- **Dynamic Sub-navigation**: Automatically populates timeline entries for each engine
- **Content Loading**: Seamless integration with existing content loading system

### 3. Content Generation (`generate_timeline_content.py`)
- **Automated Setup**: Scans timeline configurations and updates `engines.json`
- **Timeline Discovery**: Finds main timeline entries (e.g., `XCIT_BCS_01`, `XCIT_BCS_02`)
- **Category Creation**: Adds timeline categories to all supported engines
- **Overview Pages**: Generates informative overview content for each engine's timelines

### 4. Timeline Structure
Each timeline page includes:
- **Collapsible Sections**: Expandable/collapsible main sections and subsections
- **Instructions**: Step-by-step user guidance with numbered steps
- **Test Blocks**: Configured assessment phases
- **Rules**: Game mechanics and requirements  
- **Parameters**: Detailed configuration settings
- **Images**: Referenced instruction images (when available)

## Supported Engines

The following engines have timeline configurations available:

| Engine | Name | Timelines Available |
|--------|------|-------------------|
| BCS | Belval Card Sorting | 5 timelines |
| BM | Belval Matrices | 4 timelines |
| BSAC | Spatial Attention Cueing | 9 timelines |
| DS | Digit Span | 4 timelines |
| MOT | Multiple Object Tracking | 5 timelines |
| NB | N-back | 6 timelines |
| OC | Ordered Clicks | 1 timeline |
| OOO | Odd One Out | 1 timeline |
| PC | Polygon Comparison | 2 timelines |
| RE | Regular Expression | 3 timelines |
| SMC | Symbol Matrix Comparison | 7 timelines |
| SOS | Self-Ordered Search | 2 timelines |
| SRM | Stimulus Response Mapping | 5 timelines |
| TH | Target Hit | 4 timelines |
| UFOV | Useful Field of View | 5 timelines |
| WO | Which-One | 3 timelines |

## How to Use

### For End Users
1. **Navigate to an Engine**: Click on any engine (e.g., BCS, DS, NB) in the main navigation
2. **Select Timelines**: Click on "timelines" in the category navigation
3. **Browse Timeline Overview**: See all available timelines for that engine
4. **View Specific Timeline**: Click on any timeline in the sub-navigation panel
5. **Explore Content**: Use the collapsible sections to navigate through:
   - Instructions and tutorials
   - Practice and test blocks
   - Rules and parameters
   - Visual references

### For Developers
1. **Update Content**: Modify files in `/content/timeline_configs/` to update timeline data
2. **Regenerate**: Run `python3 generate_timeline_content.py` from the webapp directory
3. **Deploy**: Refresh the web server and client browsers

## Technical Details

### File Structure
```
webapp/
├── js/
│   ├── timeline.js       # Timeline management and HTML generation
│   └── script.js         # Main app logic (updated with timeline support)
├── engines.json          # Updated with timeline categories
├── generate_timeline_content.py  # Content generation script
└── index.html           # Updated to include timeline.js

content/
├── timeline_configs/    # Engine-specific timeline configurations
├── en.yaml             # Localization strings
└── images/             # Timeline instruction images
```

### Key Features
- **Dynamic Loading**: Timeline configurations are loaded on-demand
- **Error Handling**: Graceful fallbacks for missing content or configuration errors
- **Responsive Design**: Timeline content adapts to different screen sizes
- **Collapsible Sections**: Users can expand/collapse sections for better navigation
- **Clean JSON Processing**: Handles configuration files with C-style comments
- **Image Support**: Automatically references instruction images when available

### Configuration Format
Timeline configurations follow the established Behaverse format:
- **Timelines**: Main timeline entries (e.g., `XCIT_BCS_01`)
- **Blocks**: Timeline structure with instructions, rules, and parameters
- **References**: Cross-references to other timeline sections
- **Localization**: Text references resolved from `en.yaml`

## Future Enhancements

Potential improvements for future versions:
1. **Advanced Search**: Search within timeline content
2. **Export Options**: PDF or print-friendly timeline views
3. **Interactive Elements**: Links between related timeline sections
4. **Visual Timeline**: Graphical representation of timeline flow
5. **Comparison View**: Side-by-side timeline comparison
6. **Performance Optimization**: Lazy loading for large timeline configurations

## Troubleshooting

### Common Issues
1. **Timeline Not Loading**: Check that `/content/timeline_configs/[ENGINE].json` exists
2. **Missing Images**: Verify image files exist in `/content/images/[ENGINE]/`
3. **Configuration Errors**: Ensure JSON is valid (C-style comments are handled automatically)
4. **Localization Issues**: Check `en.yaml` for referenced text strings

### Debug Steps
1. Check browser console for JavaScript errors
2. Verify HTTP server can access content files
3. Run content generation script to update `engines.json`
4. Clear browser cache if changes don't appear

## Summary

The timeline implementation successfully integrates with the existing webapp architecture while providing rich, interactive timeline content. Users can now explore detailed assessment configurations in an intuitive, well-structured format that maintains consistency with the rest of the documentation platform.