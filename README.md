# Behaverse Assessment Documentation

A comprehensive documentation platform for cognitive assessment engines, featuring an interactive webapp with generated content from Excel specifications.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the webapp
cd webapp && python3 -m http.server 8000
# Visit: http://localhost:8000
```

## 📁 Repository Structure

```
behaverse_assessment_documentation/
├── 📂 content/                    # Source data and generated content
│   ├── Task spec.xlsx             # Master spreadsheet with engine data
│   ├── timeline_names.xlsx        # Timeline naming reference
│   ├── engines.json               # Generated engine configuration
│   ├── en.yaml                    # English language strings
│   ├── timeline_configs/          # JSON timeline configuration files
│   └── images/                    # Engine images and assets
├── 📂 docs/                       # Project documentation
│   ├── development/               # Development guides and fix summaries
│   ├── guides/                    # User guides
│   ├── specs/                     # Technical specifications
│   └── archive/                   # Archived documentation
├── 📂 scripts/                    # Python automation scripts
│   ├── build/                     # Build scripts (excel_extractor.py)
│   ├── generation/                # Content generation scripts
│   │   └── generate_enhanced_timeline_pages.py
│   ├── debug/                     # Debugging utilities
│   ├── utils/                     # Utility modules
│   └── legacy/                    # Archive of old scripts
├── 📂 webapp/                     # Interactive web application
│   ├── index.html                 # Main webapp interface
│   ├── js/                        # JavaScript files
│   │   ├── script.js              # Application logic
│   │   └── timeline.js            # Timeline visualization
│   ├── css/                       # Stylesheets
│   │   ├── styles.css             # Main styling
│   │   └── parameters.css         # Parameter table styling
│   ├── pages/                     # Generated HTML pages (92 files)
│   └── assets/                    # Media files and resources
├── 📂 timeline_demo/              # Timeline demonstration files
├── 📂 visual_references/          # UI mockups and visual guides
└── 📂 likely_obselete/            # Archived/deprecated files (pending cleanup)
```

## 🛠️ Development Workflow

### 1. Content Generation
```bash
# Generate timeline pages from configuration
cd scripts/generation
python3 generate_enhanced_timeline_pages.py

# Or use the wrapper script
python3 generate_timelines.py
```

### 2. Webapp Development
```bash
cd webapp
python3 -m http.server 8000

# Validate JavaScript (optional)
node -c js/script.js
```

### 3. Adding New Engines

1. **Add engine data** to `content/Task spec.xlsx`
2. **Add JSON config** in `content/timeline_configs/`
3. **Run content generation** from `scripts/generation/`
4. **Update webapp** with new engine entries

## 📊 Generated Content

The system generates comprehensive documentation including:

- **📋 Parameter Tables**: Interactive parameter specifications with search/filter
- **⏱️ Timeline Configurations**: Visual timeline structures and metadata  
- **📖 Descriptions**: Rich content with glossaries and references
- **📄 Data Dictionaries**: Complete data field specifications

## 🧰 Key Components

### Excel Data Extractor (`scripts/build/excel_extractor.py`)
- Parses `Task spec.xlsx` to extract engine parameters, descriptions, and metadata
- Handles multiple sheets and complex data structures
- Generates structured JSON data for template processing

### Timeline Generator (`scripts/generation/generate_enhanced_timeline_pages.py`)
- Processes JSON configuration files for timeline data
- Extracts trial structures, block configurations, and metadata
- Generates HTML pages for each timeline configuration

### Webapp (`webapp/`)
- **3-tier navigation**: Engines → Categories → Sub-items
- **Dynamic content loading**: Fetches from `engines.json`
- **Interactive features**: Parameter search, filtering, collapsible sections
- **Responsive design**: Clean, professional interface

## 🚦 Status

### ✅ Working Features
- **16 engines** documented: BCS, DS, NB, WO, UFOV, TH, SRM, SOS, SMC, RE, BM, BSAC, MOT, OC, OOO, PC
- **Interactive webapp** with navigation and content display
- **Parameter tables** with search and filtering
- **Timeline pages** (92 generated pages)

### 🔄 In Development
- Enhanced parameter enum display
- Timeline justification and instructions
- Demo videos integration

## 📈 Usage Statistics

Current generated content:
- **16 engines** documented
- **92 HTML pages** in webapp
- **22 timeline configurations**
- **Interactive search** across all documentation

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-engine`  
3. **Add your content** to the data sources
4. **Run content generation** scripts
5. **Test the webapp** locally
6. **Submit pull request**

## 📚 Documentation

- **Development Docs**: `docs/development/` - Implementation guides, content mapping, fix summaries
- **Technical Specs**: `docs/specs/`
- **User Guides**: `docs/guides/`
- **Visual References**: `docs/visual_references/`


## 🔧 Troubleshooting

### Common Issues

**Build fails with missing files:**
```bash
# Ensure all data files exist
ls content/Task\ spec.xlsx
ls content/timeline_configs/
```

**Webapp shows "Loading...":**
```bash
# Check JavaScript syntax
node -c webapp/js/script.js

# Verify engines.json is accessible
curl http://localhost:8000/../content/engines.json
```

**Import errors in scripts:**
```bash
# Run from repository root
cd /path/to/behaverse_assessment_documentation
python3 scripts/generation/generate_enhanced_timeline_pages.py
```

---

**🎯 Ready to explore cognitive assessment documentation at scale!**