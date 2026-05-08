# Behaverse Assessment Documentation - Webapp

This webapp implements a three-level hierarchical navigation system for the Behaverse assessment documentation, following the mockup design provided.

## Structure

The webapp implements the following navigation levels:

### Level 1: Engine Navigation (Left Panel)
- Lists all 16 engines (E1-E16)
- Blue background matching the mockup
- Click to select an engine

### Level 2: Category Navigation (Middle Panel)
- Shows categories for the selected engine:
  - about
  - parameters
  - timelines
  - data
- Light steel blue background
- Click to select a category

### Level 3: Sub-Navigation (Third Panel - Conditional)
- Only appears for categories that have sub-items
- Currently implemented for "timelines" category with:
  - timeline 1
  - timeline 2  
  - timeline 3
- Gray background matching the mockup
- Click to select a specific sub-item

### Content Area (Right Panel)
- Displays content based on current navigation selection
- Shows headers and placeholder content
- Updates dynamically when navigation changes

## Features

- **Responsive Design**: Adapts to different screen sizes
- **Smooth Transitions**: Animated layout changes when sub-navigation appears/disappears
- **Active States**: Visual feedback for currently selected items
- **Clean Typography**: Uses Futura font for a minimalistic, elegant look
- **Color Scheme**: Matches the provided mockup with blues and grays

## Technical Implementation

- **HTML**: Semantic structure with proper accessibility
- **CSS**: Grid layout with responsive design and smooth transitions
- **JavaScript**: Dynamic content loading and navigation state management
- **No Dependencies**: Pure HTML/CSS/JS implementation

## Running the Webapp

### Local Development
```bash
cd webapp
python3 -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

### File Structure
```
webapp/
├── index.html          # Main HTML structure
├── js/
│   ├── script.js       # Application logic
│   └── timeline.js     # Timeline rendering
├── css/
│   ├── styles.css      # Main styling
│   └── parameters.css  # Parameter table styling
├── pages/              # Generated HTML pages
├── assets/             # Media files
└── README.md           # This documentation
```


## Navigation Flow

1. **Select Engine**: Click any engine (E1-E16) in the left panel
2. **Select Category**: Click a category (about, parameters, timelines, data) in the middle panel
3. **Select Sub-Item** (if applicable): For "timelines", click a specific timeline in the third panel
4. **View Content**: Content updates automatically in the main area

## Customization

### Adding New Engines
Edit the `generateEngineData()` function in `script.js` to add more engines.

### Adding New Categories
Modify the `categories` object in the engine data structure.

### Adding Sub-Items
Set `hasSubItems: true` and define `subItems` object for any category.

## Browser Compatibility

Tested and compatible with:
- Chrome/Chromium
- Firefox
- Safari
- Edge

Requires modern browser with CSS Grid support.