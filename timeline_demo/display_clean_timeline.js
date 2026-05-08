/**
 * Timeline display adapter using clean_timeline_demo structure
 * This file adapts timeline content to use the clean timeline demo structure
 */

// Function to adapt and render timeline with clean_timeline_demo.html structure
function adaptTimelineToCleanStructure() {
    console.log('Adapting timeline to clean structure...');
    
    // Get the timeline container from the current page
    const timelineDetailContainer = document.querySelector('.timeline-detail-container');
    if (!timelineDetailContainer) {
        console.error('❌ No timeline detail container found');
        return false;
    }
    
    // Clear the current timeline content, preserving the header
    const timelineHeader = timelineDetailContainer.querySelector('.timeline-header');
    const timelineTitle = timelineHeader ? timelineHeader.querySelector('h2').textContent : 'Timeline';
    
    // Create a container div for the clean timeline structure
    const cleanContainer = document.createElement('div');
    cleanContainer.className = 'clean-timeline-container';
    
    // Create header similar to clean_timeline_demo.html
    const header = document.createElement('header');
    header.className = 'page-header';
    header.innerHTML = `
        <h1>${timelineTitle}</h1>
        <div class="subtitle">Timeline Content</div>
    `;
    cleanContainer.appendChild(header);
    
    // Create main timeline content container
    const timelineContent = document.createElement('div');
    timelineContent.className = 'timeline-content';
    
    // Get all existing timeline sections
    const existingSections = document.querySelectorAll('.timeline-subitem');
    if (!existingSections || existingSections.length === 0) {
        console.error('❌ No timeline sections found');
        return false;
    }
    
    // Process each section into the clean structure
    let sectionCounter = 1;
    existingSections.forEach(section => {
        // Get the section title
        const sectionTitle = section.querySelector('.timeline-subitem-title').textContent;
        
        // Create main section element
        const mainSection = document.createElement('section');
        mainSection.className = 'main-section collapsible-section';
        mainSection.id = `main-section-${sectionCounter}`;
        
        // Create section header
        const sectionHeader = document.createElement('div');
        sectionHeader.className = 'main-section-header collapsible-header';
        sectionHeader.setAttribute('onclick', `toggleSection('main-section-${sectionCounter}')`);
        sectionHeader.innerHTML = `
            <span class="collapse-icon" id="icon-main-section-${sectionCounter}"><span class="circle-open">○</span></span>
            <span class="main-section-number">${sectionCounter}.</span>
            <h2>${sectionTitle}</h2>
        `;
        
        // Create section content
        const sectionContent = document.createElement('div');
        sectionContent.className = 'main-section-content collapsible-content';
        sectionContent.id = `content-main-section-${sectionCounter}`;
        
        // Process inner content - could be subsections or direct content
        const innerContent = section.querySelector('.timeline-subitem-content');
        if (innerContent) {
            const contentHTML = innerContent.innerHTML;
            
            // Check if there are subsections in the content
            if (contentHTML.includes('instruction-item') || contentHTML.includes('subsection-header')) {
                // Already has proper structure, just ensure correct nesting
                sectionContent.innerHTML = contentHTML;
            } else {
                // Create a default subsection structure
                const subsection = document.createElement('div');
                subsection.className = 'subsection collapsible-section';
                subsection.id = `subsection-${sectionCounter}-1`;
                
                const subsectionHeader = document.createElement('div');
                subsectionHeader.className = 'subsection-header collapsible-header';
                subsectionHeader.setAttribute('onclick', `toggleSection('subsection-${sectionCounter}-1')`);
                subsectionHeader.innerHTML = `
                    <span class="collapse-icon" id="icon-subsection-${sectionCounter}-1"><span class="circle-open">○</span></span>
                    <span class="subsection-number">1.</span>
                    <h3>Content</h3>
                `;
                
                const subsectionContent = document.createElement('div');
                subsectionContent.className = 'subsection-content collapsible-content';
                subsectionContent.id = `content-subsection-${sectionCounter}-1`;
                subsectionContent.innerHTML = contentHTML;
                
                subsection.appendChild(subsectionHeader);
                subsection.appendChild(subsectionContent);
                sectionContent.appendChild(subsection);
            }
        }
        
        // Assemble the section
        mainSection.appendChild(sectionHeader);
        mainSection.appendChild(sectionContent);
        
        // Add to timeline content
        timelineContent.appendChild(mainSection);
        
        sectionCounter++;
    });
    
    // Add timeline content to container
    cleanContainer.appendChild(timelineContent);
    
    // Replace the existing content with our clean structure
    timelineDetailContainer.innerHTML = '';
    timelineDetailContainer.appendChild(cleanContainer);
    
    // Add toggle script functionality
    const toggleScript = document.createElement('script');
    toggleScript.textContent = `
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
    `;
    document.head.appendChild(toggleScript);
    
    // Add CSS for clean timeline structure
    const cleanTimelineCSS = document.createElement('style');
    cleanTimelineCSS.textContent = `
        /* Clean Timeline Demo Styles */
        .clean-timeline-container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 10px;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .page-header {
            border-bottom: 1px solid #e9ecef;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        
        .page-header h1 {
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 3px;
            color: #212529;
        }
        
        .subtitle {
            color: #6c757d;
            font-size: 14px;
        }
        
        .timeline-section {
            margin-bottom: 20px;
            border: 1px solid #dee2e6;
            border-radius: 4px;
        }
        
        .main-section {
            margin-bottom: 25px;
            border: 1px solid #dee2e6;
            border-radius: 6px;
        }
        
        .main-section-number {
            font-weight: 700;
            color: #495057;
            font-size: 20px;
        }
        
        .main-section-header h2 {
            font-size: 20px !important;
            font-weight: 600 !important;
            color: #212529 !important;
            margin: 0 !important;
            display: inline-block !important;
        }
        
        .main-section-content {
            padding: 15px;
        }
        
        .subsection {
            margin-bottom: 15px;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            background: #fdfdfd;
            width: 100%;
            display: block !important;
        }
        
        .subsection:last-child {
            margin-bottom: 0;
        }
        
        .subsection-header {
            background: #f1f3f4;
            padding: 10px 15px;
            border-bottom: 1px solid #e9ecef;
            display: flex !important;
            align-items: center !important;
            gap: 8px;
            cursor: pointer;
            user-select: none;
        }
        
        .subsection-number {
            font-weight: 600;
            color: #6c757d;
            font-size: 16px;
        }
        
        .subsection-header h3 {
            font-size: 16px !important;
            font-weight: 500 !important;
            color: #495057 !important;
            margin: 0 !important;
            display: inline-block !important;
        }
        
        .subsection-content {
            padding: 12px;
            width: 100%;
        }
        
        .instruction-item {
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #f1f3f4;
            display: flex !important;
            align-items: flex-start !important;
            gap: 10px;
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
            display: flex !important;
            justify-content: center !important;
            align-items: flex-start !important;
            padding-top: 2px;
        }
        
        .number-circle {
            background: #adb5bd;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 12px;
            font-weight: 600;
        }
        
        .instruction-content {
            flex: 1;
            min-width: 0;
        }
        
        .main-section-header {
            background: #f8f9fa;
            padding: 12px 15px;
            border-bottom: 2px solid #dee2e6;
            display: flex !important;
            align-items: center !important;
            gap: 10px;
            cursor: pointer;
            user-select: none;
        }
        
        .collapse-icon {
            margin-right: 8px;
            transition: none;
            min-width: 20px;
            text-align: center;
            display: inline-block !important;
            vertical-align: middle !important;
        }
        
        /* Closed circle (filled) */
        .circle-closed {
            font-size: 16px;
            font-weight: bold;
            line-height: 1;
        }
        
        /* Open circle (empty) */
        .circle-open {
            font-size: 26px;
            font-weight: 900;
            text-stroke: 1px black;
            -webkit-text-stroke: 1px black;
            text-shadow: 0 0 2px black;
            line-height: 0.8;
        }
        
        .collapsible-section.collapsed .collapsible-content {
            display: none;
        }
    `;
    document.head.appendChild(cleanTimelineCSS);
    
    console.log('✅ Timeline adapted to clean structure successfully');
    return true;
}

// Add the adapter to global window object for script.js to use
window.TimelineAdapter = {
    adaptTimelineToCleanStructure
};