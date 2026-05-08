/**
 * Timeline processing and display functionality
 */

// Function to parse and organize timeline data
function processTimelineData(rawTimeline) {
    // Convert string to array if needed
    let timelineData = typeof rawTimeline === 'string' ? JSON.parse(rawTimeline) : rawTimeline;
    
    // Group by participant ID
    const groupedByParticipant = {};
    
    timelineData.forEach(event => {
        // Extract participantId, use 'unknown' if not available
        const participantId = event.participantId || 'unknown';
        
        // Initialize participant group if it doesn't exist
        if (!groupedByParticipant[participantId]) {
            groupedByParticipant[participantId] = [];
        }
        
        // Add event to participant group
        groupedByParticipant[participantId].push(event);
    });
    
    // Sort events within each participant group by timestamp
    for (const participantId in groupedByParticipant) {
        groupedByParticipant[participantId].sort((a, b) => {
            return new Date(a.timestamp) - new Date(b.timestamp);
        });
    }
    
    return groupedByParticipant;
}

// Function to render timeline in the content area
function renderTimeline(timelineData, containerId) {
    const container = document.getElementById(containerId);
    
    // Clear existing content
    container.innerHTML = '';
    
    // Create main timeline container
    const timelineContainer = document.createElement('div');
    timelineContainer.className = 'timeline-container';
    
    // Check if this is raw timeline data (with participants) or config timeline data
    const isConfigTimeline = container.closest('.timeline-detail-container') !== null;
    
    if (isConfigTimeline) {
        // Config timelines already have their structure in the HTML
        // Just make sure they display correctly
        return;
    }
    
    // For experiment data timelines with participant grouping
    for (const participantId in timelineData) {
        const participantEvents = timelineData[participantId];
        
        // Create group container
        const groupContainer = document.createElement('div');
        groupContainer.className = 'timeline-group';
        
        // Create group title
        const groupTitle = document.createElement('h2');
        groupTitle.className = 'timeline-group-title';
        groupTitle.textContent = `Participant: ${participantId}`;
        groupContainer.appendChild(groupTitle);
        
        // For demo purposes, let's organize events by type
        const eventsByType = {};
        participantEvents.forEach(event => {
            const type = event.type || 'unknown';
            if (!eventsByType[type]) {
                eventsByType[type] = [];
            }
            eventsByType[type].push(event);
        });
        
        // For each event type
        for (const eventType in eventsByType) {
            const events = eventsByType[eventType];
            
            // Create subitem for event type
            const subItem = document.createElement('div');
            subItem.className = 'timeline-subitem';
            
            const subItemTitle = document.createElement('h3');
            subItemTitle.className = 'timeline-subitem-title';
            subItemTitle.textContent = `Event Type: ${eventType}`;
            subItem.appendChild(subItemTitle);
            
            const subItemContent = document.createElement('div');
            subItemContent.className = 'timeline-subitem-content';
            
            // Add each event
            events.forEach(event => {
                const eventElement = document.createElement('div');
                eventElement.className = 'timeline-event';
                
                // Format timestamp
                const timestamp = new Date(event.timestamp).toLocaleString();
                
                // Create event header with timestamp
                const eventHeader = document.createElement('div');
                eventHeader.className = 'timeline-event-type';
                eventHeader.textContent = `${timestamp}`;
                eventElement.appendChild(eventHeader);
                
                // Add event details
                const eventDetails = document.createElement('div');
                eventDetails.className = 'timeline-event-details';
                
                // Create details text based on event properties
                const detailsList = [];
                for (const key in event) {
                    if (key !== 'type' && key !== 'timestamp' && key !== 'participantId') {
                        detailsList.push(`${key}: ${JSON.stringify(event[key])}`);
                    }
                }
                
                eventDetails.textContent = detailsList.join(' | ');
                eventElement.appendChild(eventDetails);
                
                subItemContent.appendChild(eventElement);
            });
            
            subItem.appendChild(subItemContent);
            groupContainer.appendChild(subItem);
        }
        
        timelineContainer.appendChild(groupContainer);
    }
    
    container.appendChild(timelineContainer);
}

// Function to load timeline data from a JSON file
function loadTimelineData(url) {
    return fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load timeline data');
            }
            return response.json();
        });
}

// Export functions for use in main script
window.TimelineTools = {
    processTimelineData,
    renderTimeline,
    loadTimelineData
};