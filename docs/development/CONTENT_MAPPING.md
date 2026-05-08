# Content Mapping: Excel to Webapp Structure

## Executive Summary

This document maps the content from `Task spec.xlsx` to our three-level webapp navigation structure (Engines > Categories > Sub-items). The Excel file contains specifications for 16 cognitive assessment tasks that need to be transformed into a hierarchical documentation system.

---

## Excel File Analysis

### Source Structure
- **File**: `content/Task spec.xlsx`
- **Sheets**: 5 main sheets with different data types
- **Size**: 4 different data granularities (scenes, parameters, saved_data, justification)

### Current Excel Sheets Overview

| Sheet | Rows | Purpose | Key Data |
|-------|------|---------|----------|
| `scenes` | 16 | Task descriptions | Main task info, descriptions, references |
| `parameters` | 301 | Task parameters | Detailed configuration parameters |
| `saved_data` | 7 | Data events | Event tracking specifications |
| `justification` | 4 | Timeline specs | Research justifications |

---

## Proposed Webapp Mapping Structure

### Level 1: Engines (Top Navigation)
**Current State**: E1-E20 placeholders  
**Proposed**: Map to individual cognitive tasks

```
E1  → BCS (Belval Card Sorting)
E2  → DS (Digit Span) 
E3  → NB (N-back)
E4  → WO (Which-One)
E5  → UFOV (Useful Field of View)
E6  → TH (Target Hit)
E7  → SRM (Stimulus Response Mapping)
E8  → SOS (Self-Ordered Search)
E9  → SMC (Symbol Matrix Comparison)
E10 → RE (Regular Expression)
E11 → OC (Ordered Clicks)
E12 → BSAC (Button/Spatial Attention Cueing)  
E13 → MOT (Multiple Object Tracking)
E14 → SART (Sustained Attention Response Task)
E15 → GNG (Go/No-Go)
E16 → BM (Belval Matrices)

Note that the navigation panel should only show the id of the task (e.g., BCS) and not the full name. The full name should be displayed in the content area when an engine is selected.
```

### Level 2: Categories (Middle Navigation)  
**Current State**: about | parameters | timelines | data  
**Proposed**: Standardized categories for each engine

```
about      → Task overview, description, references
parameters → Configuration parameters and settings  
timelines  → Research timelines and justifications
data       → Data collection and event specifications
```

### Level 3: Sub-items (Right Navigation)
Dynamic content based on category selection:

#### For "about" category:
```
overview    → Task description and purpose
references  → Academic references and links  
glossary    → Technical terminology definitions
notes       → Implementation notes and considerations
```

#### For "parameters" category:
```
constants           → Fixed configuration values
stimulus-params     → Stimulus-related parameters
user-input-params   → User interaction parameters  
feedback-params     → Feedback and scoring parameters
timing-params       → Temporal control parameters
```

#### For "timelines" category:
```
research-timeline   → Academic research context
implementation-plan → Development roadmap
justification       → Scientific rationale
```

#### For "data" category:
```
events       → Data collection events
trial-data   → Per-trial measurements
user-actions → Interaction logging
analytics    → Analysis specifications
```

---

## Data Transformation Requirements

### 1. Engine-Level Data (from `scenes` sheet)
**Source**: Excel rows where each row = 1 task  
**Target**: Engine data structure

```javascript
// Example transformation for E1 (BCS)
engines["E1"] = {
    name: "Belval Card Sorting",
    categories: {
        about: {
            name: "About",
            content: {
                overview: { /* from scenes.description */ },
                references: { /* from scenes.references */ },
                glossary: { /* from scenes.glossary */ },
                notes: { /* from scenes.note */ }
            }
        }
        // ... other categories
    }
}
```

### 2. Parameter Data (from `parameters` sheet)  
**Source**: 301 rows of parameter specifications  
**Target**: Parameters category structure

**Grouping Strategy**:
```sql
GROUP BY config, type
-- Results in task-specific parameter groups
-- E.g., DS + "Stimulus Parameters" = digit-span stimulus config
```

**Parameter Types Mapping**:
- `Constants` → constants sub-item
- `Stimulus Parameters`/`Stimulus parameters` → stimulus-params  
- `User Input parameters`/`User input parameters` → user-input-params
- `Feedback parameters` → feedback-params
- `Timing parameters`/`Temporal parameters` → timing-params

### 3. Timeline Data (from `justification` sheet)
**Source**: 4 rows of research justifications  
**Target**: Timelines category structure

Limited data available - may need supplementation:
```
XCIT_BCS_01 → "WCST-like, 3 features, 4 reference cards, no cue"
XCIT_BCS_02 → "Task switching, 3 features, 4 reference cards, cue" 
XCIT_BCS_03 → "Task switching/learning, 2 features, 2 reference cards, AABBAA, cue"
```

### 4. Data Collection (from `saved_data` sheet)
**Source**: 7 rows of event specifications  
**Target**: Data category structure

Only example for Digit Span available - will need to extrapolate:
```
Events: TrialStart, TrialEnd, StimulusDisplay, ButtonClick, etc.
```

---

## Data Quality Assessment

### Strengths ✅
- **Rich task descriptions**: Comprehensive task overviews in `scenes` sheet
- **Detailed parameters**: 301 parameter specifications with types and defaults
- **Technical glossaries**: Domain-specific terminology definitions
- **Academic references**: Links to research papers and resources

### Gaps ❌ 
- **Incomplete justification data**: Only 4 timeline entries vs 16 tasks
- **Limited saved_data examples**: Only Digit Span events specified
- **Missing timeline details**: Most justification columns empty
- **Inconsistent parameter coverage**: Not all tasks have equal parameter detail

### Data Completeness by Task

| Task | Scenes Data | Parameters | Justification | Events |
|------|-------------|------------|---------------|---------|
| BCS  | ✅ Complete | ✅ (28 params) | ✅ 3 timelines | ❌ Missing |
| DS   | ✅ Complete | ✅ (20 params) | ❌ Missing | ✅ Complete |  
| NB   | ✅ Complete | ✅ (19 params) | ❌ Missing | ❌ Missing |
| Others | ✅ Complete | ✅ Variable | ❌ Missing | ❌ Missing |

---

## Implementation Strategy

### Phase 1: Core Content Migration 🎯
1. **Engine Names**: Map 16 task configs to E1-E16
2. **About Pages**: Transform `scenes` data to about category
3. **Parameter Pages**: Group and transform `parameters` data  
4. **Basic Structure**: Implement full 3-level navigation

### Phase 2: Content Enhancement 📈
1. **Timeline Content**: Create placeholder content for missing timeline data
2. **Data Specifications**: Extrapolate event structures for all tasks
3. **Cross-References**: Link related tasks and concepts
4. **Search Integration**: Ensure all content is searchable

### Phase 3: Validation & Polish ✨
1. **Content Review**: Verify technical accuracy
2. **User Experience**: Test navigation and search
3. **Performance**: Optimize for large content volumes
4. **Documentation**: Update technical documentation

---

## Data Transformation Scripts Needed

### 1. `excel_to_json.py`
```python
# Transform Excel sheets into webapp JSON structure
# Handle data type conversions and cleaning
# Generate consistent content hierarchy
```

### 2. `content_generator.py`
```python  
# Generate missing content using templates
# Create placeholder timeline content
# Extrapolate data event structures
```

### 3. `webapp_updater.py`
```python
# Update webapp/script.js with real engine data
# Replace placeholder content with Excel-derived content
# Maintain existing navigation functionality
```

### 4. `content_validator.py`
```python
# Verify data completeness and consistency
# Check for broken references
# Validate JSON structure integrity
```

---

## Next Steps

1. **Create transformation scripts** based on this mapping
2. **Test data migration** with subset of tasks (e.g., BCS, DS, NB)
3. **Validate webapp functionality** with real content
4. **Iterate on content structure** based on usability testing
5. **Document final data model** for future content updates

---

## Technical Notes

### Key Excel-to-JSON Transformations

```python
# Config codes to engine mapping
CONFIG_TO_ENGINE = {
    'BCS': 'E1', 'DS': 'E2', 'NB': 'E3', 'WO': 'E4',
    'UFOV': 'E5', 'TH': 'E6', 'SRM': 'E7', 'SOS': 'E8',
    # ... continue mapping
}

# Parameter type standardization
PARAM_TYPE_MAPPING = {
    'Stimulus Parameters': 'stimulus-params',
    'Stimulus parameters': 'stimulus-params', 
    'User Input parameters': 'user-input-params',
    'User input parameters': 'user-input-params',
    'Feedback parameters': 'feedback-params',
    # ... handle inconsistencies
}
```

### Content Template Structure
```javascript
// Standard template for each engine
const ENGINE_TEMPLATE = {
    name: "", // from scenes.name
    categories: {
        about: {
            name: "About",
            content: {
                overview: { title: "", body: "" },
                references: { title: "", body: "" },
                glossary: { title: "", body: "" },
                notes: { title: "", body: "" }
            }
        },
        parameters: { /* dynamic from parameters sheet */ },
        timelines: { /* from justification sheet or generated */ },
        data: { /* from saved_data sheet or generated */ }
    }
}
```

---

*This mapping document will be updated as data transformation scripts are developed and tested.*