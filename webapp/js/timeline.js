/**
 * Timeline Integration Module for Behaverse Assessment Documentation
 * 
 * This module handles timeline content loading and display functionality
 * for the webapp, integrating with the existing navigation system.
 */

class TimelineManager {
    constructor() {
        this.timelineData = {};
        this.currentTimeline = null;
        this.resolverCache = {};
    }

    /**
     * Initialize timeline functionality
     */
    async init() {
        await this.loadTimelineConfigs();
        this.setupCollapsibleSections();
    }

    /**
     * Load timeline configuration files
     */
    async loadTimelineConfigs() {
        const engines = ['BCS', 'DS', 'NB', 'WO', 'UFOV', 'TH', 'SRM', 'SOS', 'SMC', 'RE', 'BM', 'BSAC', 'MOT', 'OC', 'OOO', 'PC'];
        
        for (const engine of engines) {
            try {
                const response = await fetch(`content/timeline_configs/${engine}.json`);
                if (response.ok) {
                    const text = await response.text();
                    // Clean JSON content (remove C-style comments)
                    const cleanedText = this.cleanJSONContent(text);
                    const config = JSON.parse(cleanedText);
                    this.timelineData[engine] = config;
                }
            } catch (error) {
                console.error(`TimelineManager: Error loading ${engine} config:`, error);
            }
        }
    }

    /**
     * Get available timelines for an engine
     */
    getEngineTimelines(engineCode) {
        const config = this.timelineData[engineCode];
        if (!config || !config.Timelines) {
            return [];
        }

        // Find main timeline entries (not intro/outro)
        const timelines = [];
        const timelineNames = Object.keys(config.Timelines);
        
        for (const name of timelineNames) {
            // Look for main timeline entries like XCIT_BCS_01, XCIT_BCS_02, etc.
            const regex = new RegExp(`^XCIT_${engineCode}_\\d+$`);
            if (regex.test(name)) {
                timelines.push(name);
            }
        }
        
        return timelines.sort();
    }

    /**
     * Clean JSON content by removing C-style comments
     */
    cleanJSONContent(content) {
        // Remove single-line comments
        content = content.replace(/\/\/.*?$/gm, '');
        // Remove multi-line comments
        content = content.replace(/\/\*.*?\*\//gs, '');
        // Remove trailing commas
        content = content.replace(/,(\s*[}\]])/g, '$1');
        return content;
    }

    /**
     * Load localization data
     */
    async loadLocalization() {
        try {
            const response = await fetch('content/en.yaml');
            if (response.ok) {
                const yamlText = await response.text();
                // Simple YAML parsing for our needs (you might want to use a proper YAML parser)
                return this.parseSimpleYAML(yamlText);
            }
        } catch (error) {
            console.error('TimelineManager: Error loading localization:', error);
        }
        return {};
    }

    /**
     * Simple YAML parser for basic key-value pairs
     */
    parseSimpleYAML(yamlText) {
        const result = {};
        const lines = yamlText.split('\n');
        let currentSection = result;
        let sectionPath = [];

        for (let line of lines) {
            line = line.trim();
            if (!line || line.startsWith('#')) continue;

            const indent = line.length - line.trimStart().length;
            const colonIndex = line.indexOf(':');
            
            if (colonIndex > -1) {
                const key = line.substring(0, colonIndex).trim();
                const value = line.substring(colonIndex + 1).trim();
                
                if (value) {
                    // Simple key-value pair
                    currentSection[key] = value;
                } else {
                    // Section header
                    const newSection = {};
                    currentSection[key] = newSection;
                    
                    // Update navigation for nested sections
                    if (indent === 0) {
                        currentSection = result;
                        sectionPath = [key];
                    } else {
                        sectionPath = sectionPath.slice(0, indent / 2);
                        sectionPath.push(key);
                    }
                    
                    // Navigate to the right section
                    currentSection = result;
                    for (const pathKey of sectionPath) {
                        if (!currentSection[pathKey]) {
                            currentSection[pathKey] = {};
                        }
                        currentSection = currentSection[pathKey];
                    }
                }
            }
        }
        
        return result;
    }

    /**
     * Resolve text reference to actual text
     */
    resolveTextReference(textRef, localization) {
        if (!textRef || textRef.indexOf('.') === -1) {
            return textRef;
        }

        const parts = textRef.split('.');
        let current = localization;
        
        for (const part of parts) {
            if (current && typeof current === 'object' && part in current) {
                current = current[part];
            } else {
                return `[Missing: ${textRef}]`;
            }
        }
        
        return typeof current === 'string' ? current : `[Invalid: ${textRef}]`;
    }

    /**
     * Generate HTML content for a timeline
     */
    async generateTimelineHTML(engineCode, timelineName) {
        const config = this.timelineData[engineCode];
        if (!config || !config.Timelines || !config.Timelines[timelineName]) {
            return '<p>Timeline not found.</p>';
        }

        const localization = await this.loadLocalization();
        const timeline = config.Timelines[timelineName];
        
        let html = `
            <div class="timeline-content">
                <div class="timeline-header">
                    <h2>${timelineName}</h2>
                    <div class="timeline-meta">
                        <span class="timeline-engine">${this.getEngineName(engineCode)}</span>
                    </div>
                </div>
        `;

        if (timeline.blocks && Array.isArray(timeline.blocks)) {
            html += '<div class="timeline-blocks">';
            
            for (let i = 0; i < timeline.blocks.length; i++) {
                const block = timeline.blocks[i];
                html += this.generateBlockHTML(block, i + 1, config, localization, engineCode);
            }
            
            html += '</div>';
        }

        html += '</div>';
        
        // Add the CSS and JavaScript for collapsible sections
        html += this.getTimelineCSS();
        html += this.getTimelineJS();
        
        return html;
    }

    /**
     * Generate HTML for a timeline block
     */
    generateBlockHTML(block, blockIndex, config, localization, engineCode) {
        let html = `
            <section class="main-section collapsible-section" id="main-section-${blockIndex}">
                <div class="main-section-header collapsible-header" onclick="timelineToggleSection('main-section-${blockIndex}')">
                    <span class="collapse-icon" id="icon-main-section-${blockIndex}">+</span>
                    <span class="main-section-number">${blockIndex}.</span>
                    <h3>${block.name || block.timeline || `Block ${blockIndex}`}</h3>
                </div>
                <div class="main-section-content collapsible-content" id="content-main-section-${blockIndex}">
        `;

        // Handle timeline references
        if (block.timeline) {
            const referencedTimeline = config.Timelines[block.timeline];
            if (referencedTimeline && referencedTimeline.blocks) {
                for (let j = 0; j < referencedTimeline.blocks.length; j++) {
                    const subBlock = referencedTimeline.blocks[j];
                    html += this.generateSubBlockHTML(subBlock, blockIndex, j + 1, config, localization, engineCode);
                }
            }
        }

        // Handle direct block content
        if (block.Instructions) {
            html += this.generateInstructionsHTML(block.Instructions, blockIndex, 1, localization, engineCode);
        }

        // Handle rules
        if (block.rulesName && config.Rules && config.Rules[block.rulesName]) {
            html += this.generateRulesHTML(config.Rules[block.rulesName], localization);
        }

        // Handle parameters
        if (block.Parameters) {
            html += this.generateParametersHTML(block.Parameters);
        }

        html += '</div></section>';
        return html;
    }

    /**
     * Generate HTML for a sub-block (from referenced timeline)
     */
    generateSubBlockHTML(subBlock, mainIndex, subIndex, config, localization, engineCode) {
        const subBlockId = `subsection-${mainIndex}-${subIndex}`;
        
        let html = `
            <div class="subsection collapsible-section" id="${subBlockId}">
                <div class="subsection-header collapsible-header" onclick="timelineToggleSection('${subBlockId}')">
                    <span class="collapse-icon" id="icon-${subBlockId}">+</span>
                    <span class="subsection-number">${subIndex}.</span>
                    <h4>${subBlock.name || `Sub-block ${subIndex}`}</h4>
                </div>
                <div class="subsection-content collapsible-content" id="content-${subBlockId}">
        `;

        if (subBlock.Instructions) {
            html += this.generateInstructionsHTML(subBlock.Instructions, mainIndex, subIndex, localization, engineCode);
        }

        html += '</div></div>';
        return html;
    }

    /**
     * Generate HTML for instructions
     */
    generateInstructionsHTML(instructions, mainIndex, subIndex, localization, engineCode) {
        if (!instructions || !Array.isArray(instructions)) {
            return '';
        }

        let html = '';
        
        for (let i = 0; i < instructions.length; i++) {
            const instruction = instructions[i];
            html += `
                <div class="instruction-item">
                    <div class="instruction-number">
                        <span class="number-circle">${i + 1}</span>
                    </div>
                    <div class="instruction-content">
            `;

            if (instruction.Content && Array.isArray(instruction.Content)) {
                for (const content of instruction.Content) {
                    if (content.Text) {
                        const resolvedText = this.resolveTextReference(content.Text, localization);
                        if (content.heading === 2) {
                            html += `<h4 class="content-heading">${resolvedText}</h4>`;
                        } else {
                            html += `<div class="instruction-text">${resolvedText}</div>`;
                        }
                    }
                }
            }

            // Handle image references
            if (instruction.Image) {
                html += `
                    <div class="instruction-image">
                        <img src="content/images/${engineCode}/${instruction.Image}.png" 
                             alt="${instruction.Image}" 
                             onerror="this.style.display='none';" />
                    </div>
                `;
            }

            html += '</div></div>';
        }

        return html;
    }

    /**
     * Generate HTML for rules
     */
    generateRulesHTML(rules, localization) {
        if (!rules || !Array.isArray(rules)) {
            return '';
        }

        let html = '<div class="test-rules"><div class="rules-content">';
        
        for (const rule of rules) {
            if (rule.text) {
                const resolvedText = this.resolveTextReference(rule.text, localization);
                if (rule.heading === 2) {
                    html += `<div class="rule-heading">${resolvedText}</div>`;
                } else {
                    html += `<div class="rule-text">${resolvedText}</div>`;
                }
            }
        }
        
        html += '</div></div>';
        return html;
    }

    /**
     * Generate HTML for parameters
     */
    generateParametersHTML(parameters) {
        if (!parameters || typeof parameters !== 'object') {
            return '';
        }

        let html = '<div class="test-parameters"><table class="parameters-table">';
        
        for (const [key, value] of Object.entries(parameters)) {
            html += `
                <tr>
                    <td class="param-name">${key}</td>
                    <td class="param-value">${this.formatParameterValue(value)}</td>
                </tr>
            `;
        }
        
        html += '</table></div>';
        return html;
    }

    /**
     * Format parameter values for display
     */
    formatParameterValue(value) {
        if (value === null || value === undefined) {
            return '<em>null</em>';
        }
        if (typeof value === 'object') {
            return `<pre>${JSON.stringify(value, null, 2)}</pre>`;
        }
        return String(value);
    }

    /**
     * Get engine display name
     */
    getEngineName(engineCode) {
        const names = {
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
            'PC': 'Polygon Comparison'
        };
        return names[engineCode] || engineCode;
    }

    /**
     * Show inheritance modal dialog
     */
    showInheritanceModal(detailsDiv, button) {
        // Create modal overlay
        const modal = document.createElement('div');
        modal.className = 'inheritance-modal-overlay';
        modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center; z-index: 1000;';

        // Create modal content
        const modalContent = document.createElement('div');
        modalContent.className = 'inheritance-modal-content';
        modalContent.style.cssText = 'background: white; border-radius: 8px; max-width: 80%; max-height: 80%; overflow-y: auto; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); position: relative;';

        // Create close button
        const closeButton = document.createElement('button');
        closeButton.textContent = '×';
        closeButton.className = 'inheritance-modal-close';
        closeButton.style.cssText = 'position: absolute; top: 10px; right: 15px; background: none; border: none; font-size: 24px; cursor: pointer; color: #666;';

        // Create title
        const title = document.createElement('h3');
        title.textContent = 'Parameter Inheritance Chain';
        title.style.cssText = 'margin-top: 0; margin-bottom: 20px; color: #333;';

        // Clone the details content
        const detailsClone = detailsDiv.cloneNode(true);
        detailsClone.style.display = 'block';
        detailsClone.style.margin = '0';

        // Assemble modal
        modalContent.appendChild(closeButton);
        modalContent.appendChild(title);
        modalContent.appendChild(detailsClone);
        modal.appendChild(modalContent);

        // Add to page
        document.body.appendChild(modal);

        // Close handlers
        const closeModal = () => {
            document.body.removeChild(modal);
        };

        closeButton.addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });

        // ESC key handler
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }

    /**
     * Setup collapsible sections functionality
     */
    setupCollapsibleSections() {
        // Add global toggle function
        window.timelineToggleSection = (sectionId) => {
            const section = document.getElementById(sectionId);
            const content = document.getElementById('content-' + sectionId);
            const icon = document.getElementById('icon-' + sectionId);
            
            if (!section || !content || !icon) {
                return;
            }
            
            if (section.classList.contains('expanded')) {
                section.classList.remove('expanded');
            } else {
                section.classList.add('expanded');
            }
        };

        // Add global toggleInheritanceDetails function
        window.toggleInheritanceDetails = (detailsId, button) => {
            const detailsDiv = document.getElementById(detailsId);

            if (detailsDiv) {
                // Create and show modal dialog
                this.showInheritanceModal(detailsDiv, button);
            } else {
                console.error('Could not find element with ID:', detailsId);
            }
        };

        // Initialize all sections as collapsed
        document.addEventListener('DOMContentLoaded', function() {
            const sections = document.querySelectorAll('.collapsible-section');
            sections.forEach(function(section) {
                // Icons are now handled by CSS pseudo-elements
            });
        });
    }

    /**
     * Get CSS styles for timeline display
     */
    getTimelineCSS() {
        return `
            <style>
                .timeline-content {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    line-height: 1.4;
                    color: #333;
                }

                .timeline-header {
                    border-bottom: 2px solid #dee2e6;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }

                .timeline-header h2 {
                    font-size: 28px;
                    font-weight: 600;
                    margin: 0 0 10px 0;
                    color: #212529;
                }

                .timeline-meta {
                    color: #6c757d;
                    font-size: 14px;
                }

                .main-section {
                    margin-bottom: 25px;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                }

                .main-section-header {
                    background: #f8f9fa;
                    padding: 12px 15px;
                    border-bottom: 2px solid #dee2e6;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    cursor: pointer;
                    user-select: none;
                }

                .main-section-header h3 {
                    font-size: 18px;
                    font-weight: 600;
                    color: #212529;
                    margin: 0;
                }

                .main-section-number {
                    font-weight: 700;
                    color: #495057;
                    font-size: 18px;
                }

                .main-section-content {
                    padding: 15px;
                }

                .subsection {
                    margin-bottom: 15px;
                    border: 1px solid #e9ecef;
                    border-radius: 4px;
                    background: #fdfdfd;
                }

                .subsection-header {
                    background: #f1f3f4;
                    padding: 8px 12px;
                    border-bottom: 1px solid #e9ecef;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    cursor: pointer;
                    user-select: none;
                }

                .subsection-header h4 {
                    font-size: 16px;
                    font-weight: 500;
                    color: #495057;
                    margin: 0;
                }

                .subsection-number {
                    font-weight: 600;
                    color: #6c757d;
                    font-size: 14px;
                }

                .subsection-content {
                    padding: 12px;
                }

                .instruction-item {
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #f1f3f4;
                    display: flex;
                    align-items: flex-start;
                    gap: 10px;
                }

                .instruction-item:last-child {
                    border-bottom: none;
                    margin-bottom: 0;
                }

                .instruction-number {
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

                .content-heading {
                    font-size: 16px;
                    font-weight: 600;
                    color: #212529;
                    margin-bottom: 10px;
                }

                .instruction-text {
                    color: #495057;
                    margin-bottom: 10px;
                    line-height: 1.5;
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

                .collapse-icon {
                    margin-right: 8px;
                    transition: none;
                    min-width: 20px;
                    text-align: center;
                    color: #999;
                    background: none;
                    font-size: 18px;
                    font-weight: bold;
                }

                .circle-closed {
                    font-size: 16px;
                    font-weight: bold;
                }

                .circle-open {
                    font-size: 20px;
                    font-weight: 900;
                }

                .collapsible-section.collapsed .collapsible-content {
                    display: none;
                }

                .test-rules {
                    margin-bottom: 20px;
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
                    line-height: 1.5;
                }

                .test-parameters {
                    margin-bottom: 20px;
                }

                .parameters-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 0;
                }

                .parameters-table tr {
                    border: none;
                }

                .parameters-table td {
                    padding: 0.75rem;
                    vertical-align: baseline;
                    font-size: 0.875rem;
                    line-height: 1.4;
                    border: none;
                }

                .param-name {
                    font-weight: 600;
                    color: #6c757d;
                    width: 20%;
                    text-align: right;
                    padding-right: 1rem;
                    vertical-align: baseline;
                }

                .param-value {
                    color: #666;
                    width: 80%;
                    vertical-align: baseline;
                }

                .param-value pre {
                    background: #f9fafb;
                    padding: 0.75rem;
                    border-radius: 4px;
                    font-size: 0.75rem;
                    margin: 0.5rem 0 0 0;
                    color: #4b5563;
                    border: 1px solid #e5e7eb;
                }

                /* Nested parameter dictionary styling */
                .param-dict {
                    margin: 0.25rem 0;
                }

                .param-dict-item {
                    display: flex;
                    align-items: flex-start;
                    gap: 0.5rem;
                    margin: 0.25rem 0;
                    font-size: 0.875rem;
                    line-height: 1.4;
                }

                .param-dict-item.indent-0 { margin-left: 0; }
                .param-dict-item.indent-1 { margin-left: 1rem; }
                .param-dict-item.indent-2 { margin-left: 2rem; }
                .param-dict-item.indent-3 { margin-left: 3rem; }
                .param-dict-item.indent-4 { margin-left: 4rem; }

                .param-key {
                    font-weight: 600;
                    color: #6c757d;
                    min-width: fit-content;
                    flex-shrink: 0;
                }

                .param-list {
                    margin: 0.25rem 0;
                }

                .param-list-item {
                    display: flex;
                    align-items: flex-start;
                    gap: 0.5rem;
                    margin: 0.125rem 0;
                    font-size: 0.875rem;
                    line-height: 1.4;
                }

                .param-index {
                    font-weight: 500;
                    color: #6c757d;
                    min-width: fit-content;
                    flex-shrink: 0;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    font-size: 0.75rem;
                }

                .param-val {
                    color: #666;
                }

                @media (max-width: 768px) {
                    .timeline-content {
                        padding: 10px;
                    }
                    
                    .timeline-header h2 {
                        font-size: 24px;
                    }
                    
                    .instruction-item {
                        flex-direction: column;
                        gap: 8px;
                    }
                    
                    .instruction-number {
                        width: auto;
                        align-self: flex-start;
                    }
                }
            </style>
        `;
    }

    /**
     * Get JavaScript for timeline functionality
     */
    getTimelineJS() {
        return `
            <script>
                // Initialize all sections as expanded
                document.addEventListener('DOMContentLoaded', function() {
                    const sections = document.querySelectorAll('.collapsible-section');
                    sections.forEach(function(section) {
                        const content = section.querySelector('.collapsible-content');
                        const icon = section.querySelector('.collapse-icon');
                        if (content) content.style.display = '';
                        if (icon) icon.innerHTML = '<span class="circle-open">○</span>';
                    });
                });

                // toggleInheritanceDetails function is defined in individual timeline pages
            </script>
        `;
    }
}

// Initialize TimelineManager on page load
document.addEventListener('DOMContentLoaded', function() {
    const timelineManager = new TimelineManager();
    timelineManager.setupCollapsibleSections();
});

/**
 * Test Timeline Function
 * Placeholder function for testing timeline functionality
 */
function testTimeline(timelineId) {
    alert(`Testing timeline: ${timelineId}\n\nThis is a placeholder function. In the future, this will launch the actual timeline test.`);
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TimelineManager;
}