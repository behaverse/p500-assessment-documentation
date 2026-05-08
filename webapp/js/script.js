// Behaverse Assessment Documentation - Main Application Script

// Application data - HOME content hardcoded, engines loaded from JSON
let engineData = {
    "HOME": {
        "name": "HOME",
        "isHomePage": true,
        "content": {
            "title": "Behaverse Assessment Documentation",
            "body": `<h2>Welcome to Behaverse Assessment Documentation</h2>
<p>This platform provides comprehensive documentation for cognitive assessment engines.</p>
<h3>Available Assessment Tasks</h3>
<p>Explore cognitive assessment engines, each designed for specific research needs:</p>
<ul>
<li><strong>BCS</strong> - Belval Card Sorting (set-shifting)</li>
<li><strong>DS</strong> - Digit Span (working memory)</li>
<li><strong>NB</strong> - N-back (working memory)</li>
<li><strong>WO</strong> - Which-One (attention & flanker tasks)</li>
<li><strong>UFOV</strong> - Useful Field of View (visual attention)</li>
<li><strong>TH</strong> - Target Hit (reaction time)</li>
<li><strong>SRM</strong> - Stimulus Response Mapping (reaction time)</li>
<li><strong>SOS</strong> - Self-Ordered Search (spatial working memory)</li>
<li><strong>SMC</strong> - Symbol Matrix Comparison (pattern matching)</li>
<li><strong>RE</strong> - Regular Expression (sustained attention)</li>
<li><strong>BM</strong> - Belval Matrices (fluid intelligence)</li>
<li><strong>BSAC</strong> - Spatial Attention Cueing (spatial attention)</li>
<li><strong>MOT</strong> - Multiple Object Tracking (visual attention)</li>
<li><strong>OC</strong> - Ordered Clicks (spatial working memory)</li>
<li><strong>OOO</strong> - Odd One Out (reasoning)</li>
<li><strong>PC</strong> - Polygon Comparison (visual perception)</li>
</ul>
<h3>Features</h3>
<p>• Complete task descriptions and scientific background</p>
<p>• Detailed parameter specifications</p>
<p>• Academic references and glossaries</p>
<p>• Implementation notes and considerations</p>`
        }
    }
};

// Application state
let currentEngine = 'HOME';
let currentCategory = 'description';
let currentSubItem = null;

// DOM elements
let engineItems;
let categoryItems;
let subNavigation;
let subItemsList;
let pageTitle;
let mainContent;

// Timeline manager
let timelineManager;

// Load engines data from JSON file
async function loadEnginesData() {
    try {
        const response = await fetch('content/engines.json');
        const data = await response.json();
        
        // Merge with existing HOME data
        engineData = { ...engineData, ...data };
        return true;
    } catch (error) {
        console.error('Failed to load content/engines.json:', error);
        return false;
    }
}

// Initialize the application
async function init() {
    await loadEnginesData();


    // Initialize timeline manager
    timelineManager = new TimelineManager();
    await timelineManager.init();
    
    // Initialize DOM elements
    engineItems = document.querySelectorAll('.engine-item');
    categoryItems = document.querySelectorAll('.category-item');
    subNavigation = document.getElementById('sub-navigation');
    subItemsList = document.getElementById('sub-items');
    pageTitle = document.getElementById('page-title');
    mainContent = document.getElementById('main-content');
    
    setupEventListeners();
    setupCollapseControls();
    setupContentActionHandler();
    setupSearch();
    setupHashRouter();
}

// Delegated click handler for action links rendered into mainContent
function setupContentActionHandler() {
    mainContent.addEventListener('click', async (event) => {
        const target = event.target.closest('[data-action]');
        if (!target) return;
        event.preventDefault();
        if (target.dataset.action === 'back-to-description') {
            await selectCategory('description');
        }
    });
}

// Set up event listeners
function setupEventListeners() {
    engineItems.forEach(item => {
        bindNavItem(item, async () => await selectEngine(item.dataset.engine));
    });
    categoryItems.forEach(item => {
        bindNavItem(item, async () => await selectCategory(item.dataset.category));
    });
}

// Wire click + keyboard activation for a nav item. Enter/Space behave like click.
function bindNavItem(item, handler) {
    item.addEventListener('click', handler);
    item.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            await handler();
        }
    });
}

// Build a keyboard-accessible sub-nav <li> with the given label and activation handler.
function createSubItemElement(label, handler) {
    const li = document.createElement('li');
    li.className = 'sub-item';
    li.dataset.subitem = label;
    li.textContent = label;
    li.tabIndex = 0;
    li.setAttribute('role', 'tab');
    li.setAttribute('aria-selected', 'false');
    bindNavItem(li, handler);
    return li;
}

// Reflect .active state into aria-selected for any nav row.
function syncAriaSelected(items) {
    items.forEach(item => {
        item.setAttribute('aria-selected', item.classList.contains('active') ? 'true' : 'false');
    });
}

// Set up collapse controls
function setupCollapseControls() {
    const appContainer = document.querySelector('.app-container');
    const navToggle = document.getElementById('nav-toggle');
    
    if (!navToggle || !appContainer) {
        return;
    }
    
    let navCollapsed = false;
    
    navToggle.addEventListener('click', () => {
        navCollapsed = !navCollapsed;
        
        if (navCollapsed) {
            appContainer.classList.add('nav-collapsed');
            navToggle.innerHTML = '☰';
            navToggle.title = 'Show Navigation';
        } else {
            appContainer.classList.remove('nav-collapsed');
            navToggle.innerHTML = '✕';
            navToggle.title = 'Hide Navigation';
        }
    });
}

// Select an engine
async function selectEngine(engineId) {
    currentEngine = engineId;
    currentSubItem = null;
    
    // Update active state
    engineItems.forEach(item => {
        item.classList.toggle('active', item.dataset.engine === engineId);
    });
    syncAriaSelected(engineItems);
    
    const appContainer = document.querySelector('.app-container');
    const categoryNav = document.querySelector('.category-nav');
    
    if (engineId === 'HOME') {
        categoryNav.style.display = 'none';
        hideSubNavigation();
        await updateContent(engineData.HOME.content);
        appContainer.classList.remove('sub-nav-visible');
        appContainer.style.gridTemplateColumns = '150px 0px 0px 1fr';
    } else {
        categoryNav.style.display = 'flex';
        currentCategory = 'description';
        categoryItems.forEach(item => {
            item.classList.toggle('active', item.dataset.category === 'description');
        });
        syncAriaSelected(categoryItems);

        appContainer.classList.remove('sub-nav-visible');
        appContainer.style.gridTemplateColumns = '';

        await updateDisplay();
    }
    syncHashFromState();
}

// Select a category
async function selectCategory(category) {
    currentCategory = category;
    currentSubItem = null;
    
    categoryItems.forEach(item => {
        item.classList.toggle('active', item.dataset.category === category);
    });
    syncAriaSelected(categoryItems);

    await updateDisplay();
    syncHashFromState();
}

// Select a sub-item
async function selectSubItem(subItem) {
    currentSubItem = subItem;

    const subItems = document.querySelectorAll('.sub-item');
    subItems.forEach(item => {
        item.classList.toggle('active', item.dataset.subitem === subItem);
    });
    syncAriaSelected(subItems);

    await updateDisplay();
    syncHashFromState();
}

// Update display
async function updateDisplay() {
    if (currentEngine === 'HOME') {
        return;
    }
    
    const engine = engineData[currentEngine];
    if (!engine) {
        console.error('Engine not found:', currentEngine);
        return;
    }

    // Special handling for timeline category
    if (currentCategory === 'timelines') {
        await handleTimelineDisplay();
        return;
    }
    
    const category = engine.categories[currentCategory];
    if (!category) {
        console.error('Category not found:', currentCategory, 'in engine:', currentEngine);
        return;
    }
    
    if (category.hasSubItems) {
        await showSubNavigation(category);
    } else {
        hideSubNavigation();
        await updateContent(category.content);
    }
}

// Handle timeline display
async function handleTimelineDisplay() {
    const timelines = timelineManager.getEngineTimelines(currentEngine);
    
    if (timelines.length === 0) {
        hideSubNavigation();
        await updateContent({
            title: `${currentEngine} Timelines`,
            body: `<p>No timeline configurations found for ${currentEngine}.</p>`
        });
        return;
    }

    // Show timeline sub-navigation
    subNavigation.classList.add('visible');
    document.querySelector('.app-container').classList.add('sub-nav-visible');
    
    subItemsList.innerHTML = '';
    
    // Add timeline items to sub-navigation
    timelines.forEach((timelineName, index) => {
        const li = createSubItemElement(timelineName, async () => await selectTimelineItem(timelineName));
        subItemsList.appendChild(li);
    });
    
    // Load default timeline or current selection
    const target = currentSubItem && timelines.includes(currentSubItem) ? currentSubItem : timelines[0];
    currentSubItem = target;
    await loadTimelineContent(target);
    const subItems = document.querySelectorAll('.sub-item');
    subItems.forEach(item => {
        item.classList.toggle('active', item.dataset.subitem === target);
    });
    syncAriaSelected(subItems);
}

// Select a timeline item
async function selectTimelineItem(timelineName) {
    currentSubItem = timelineName;

    const subItems = document.querySelectorAll('.sub-item');
    subItems.forEach(item => {
        item.classList.toggle('active', item.dataset.subitem === timelineName);
    });
    syncAriaSelected(subItems);

    await loadTimelineContent(timelineName);
    syncHashFromState();
}

// Load timeline content
async function loadTimelineContent(timelineName) {
    const title = `${currentEngine} - ${timelineName}`;
    try {
        const response = await fetch(`pages/timelines/${currentEngine.toLowerCase()}/${timelineName.toLowerCase()}.html`);
        if (response.ok) {
            await updateContent({ title, body: await response.text() });
            return;
        }
        if (response.status === 404) {
            await updateContent({ title, body: renderTimelineMissing(timelineName, 'not yet generated') });
            return;
        }
        await updateContent({ title, body: renderTimelineMissing(timelineName, `server returned HTTP ${response.status}`) });
    } catch (error) {
        console.error('Error loading timeline content:', error);
        await updateContent({ title, body: renderTimelineMissing(timelineName, 'network error — see console') });
    }
}

function renderTimelineMissing(timelineName, reason) {
    return `<div class="timeline-missing">
        <h2>Timeline page unavailable</h2>
        <p>The timeline <code>${timelineName}</code> is listed in the configuration for <strong>${currentEngine}</strong>, but its rendered page could not be loaded (${reason}).</p>
        <p>This usually means <code>scripts/generation/generate_timelines.py</code> has not been run since the timeline was added to <code>content/timeline_configs/${currentEngine}.json</code>.</p>
        <p><a href="#" data-action="back-to-description">Back to ${currentEngine} description</a></p>
    </div>`;
}

// Show sub-navigation
async function showSubNavigation(category) {
    subNavigation.classList.add('visible');
    document.querySelector('.app-container').classList.add('sub-nav-visible');
    
    subItemsList.innerHTML = '';
    
    Object.keys(category.subItems).forEach(subItemKey => {
        const li = createSubItemElement(subItemKey, async () => await selectSubItem(subItemKey));
        subItemsList.appendChild(li);
    });
    
    const target = currentSubItem && category.subItems[currentSubItem]
        ? currentSubItem
        : Object.keys(category.subItems)[0];
    if (target) {
        currentSubItem = target;
        await updateContent(category.subItems[target]);
        const subItems = document.querySelectorAll('.sub-item');
        subItems.forEach(item => {
            item.classList.toggle('active', item.dataset.subitem === target);
        });
        syncAriaSelected(subItems);
    }
}

// Hide sub-navigation
function hideSubNavigation() {
    subNavigation.classList.remove('visible');
    document.querySelector('.app-container').classList.remove('sub-nav-visible');
    currentSubItem = null;
}

// Load parameter HTML file for a specific engine
async function loadParameterHTML(engineConfig) {
    try {
        const response = await fetch(`pages/parameters/${engineConfig}_parameters.html`);
        if (!response.ok) {
            throw new Error(`Failed to load ${engineConfig} parameters`);
        }
        const htmlContent = await response.text();
        
        // Extract just the body content (remove html, head, body tags)
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlContent, 'text/html');
        return doc.body.innerHTML;
    } catch (error) {
        console.error('Error loading parameter HTML:', error);
        return '<p>Error loading parameter content.</p>';
    }
}

// Update content
async function updateContent(content) {
    let breadcrumbPath = '';
    let engineName = '';
    let engineConfig = '';
    let showImage = false;
    
    if (currentEngine === 'HOME') {
        breadcrumbPath = 'Home';
    } else {
        const engine = engineData[currentEngine];
        if (engine) {
            engineName = engine.name || currentEngine;
            engineConfig = engine.config || currentEngine;
            showImage = (currentCategory === 'description');
            
            breadcrumbPath = engineConfig;
            
            if (currentCategory) {
                const categoryDisplay = currentCategory.charAt(0).toUpperCase() + currentCategory.slice(1);
                breadcrumbPath += ` > ${categoryDisplay}`;
                
                if (currentSubItem) {
                    const category = engine.categories[currentCategory];
                    if (category && category.subItems && category.subItems[currentSubItem]) {
                        const subItemTitle = category.subItems[currentSubItem].title;
                        const shortTitle = subItemTitle.replace(engineName, '').replace(/^\s*-\s*/, '').trim();
                        breadcrumbPath += ` > ${shortTitle}`;
                    }
                }
            }
        }
    }
    
    pageTitle.textContent = breadcrumbPath;
    
    let contentHTML = '';
    
    if (showImage && engineName && engineConfig) {
        contentHTML += `
            <div class="engine-header">
                <h1 class="engine-name">${engineName}</h1>
                <video src="assets/engines/${engineConfig}/video.mp4" 
                       class="engine-video"
                       controls
                       preload="metadata"
                       muted
                       playsinline
                       poster="assets/engines/${engineConfig}/thumbnail.jpg">
                    <p>Your browser doesn't support video. <a href="assets/engines/${engineConfig}/video.mp4">Download the video</a> instead.</p>
                </video>
            </div>
        `;
    }
    
    // Check if we need to load parameter HTML file instead of using JSON content
    if (currentCategory === 'parameters' && currentEngine !== 'HOME') {
        const parameterHTML = await loadParameterHTML(engineConfig);
        contentHTML += parameterHTML;
    } else {
        contentHTML += content.body;
    }
    
    mainContent.innerHTML = contentHTML;
    mainContent.classList.add('fade-in');
    
    setTimeout(() => {
        mainContent.classList.remove('fade-in');
    }, 300);
}

// ---------- Hash router ----------
// Hash format: #ENGINE[/category[/subitem]]. Empty hash → HOME.

let suppressHashSync = false; // set while applying a hash to avoid feedback loops

function setupHashRouter() {
    window.addEventListener('hashchange', applyHashToState);
    applyHashToState(); // boot from current hash (may be empty)
}

async function applyHashToState() {
    suppressHashSync = true;
    try {
        const parsed = parseHash(window.location.hash);
        if (!parsed.engine || parsed.engine === 'HOME' || !engineData[parsed.engine]) {
            await selectEngine('HOME');
            return;
        }
        await selectEngine(parsed.engine);
        if (parsed.category && ['description','parameters','timelines'].includes(parsed.category)) {
            await selectCategory(parsed.category);
        }
        if (parsed.subitem) {
            if (parsed.category === 'timelines') {
                await selectTimelineItem(parsed.subitem);
            } else {
                await selectSubItem(parsed.subitem);
            }
        }
    } finally {
        suppressHashSync = false;
    }
}

function parseHash(hash) {
    const raw = (hash || '').replace(/^#/, '');
    if (!raw) return {};
    const [engine, category, subitem] = raw.split('/').map(decodeURIComponent);
    return { engine, category, subitem };
}

function syncHashFromState() {
    if (suppressHashSync) return;
    let next = '';
    if (currentEngine && currentEngine !== 'HOME') {
        next = '#' + encodeURIComponent(currentEngine);
        if (currentCategory) next += '/' + encodeURIComponent(currentCategory);
        if (currentSubItem) next += '/' + encodeURIComponent(currentSubItem);
    }
    if (window.location.hash !== next) {
        // Use replaceState so we don't pollute back-history with every nav click
        history.replaceState(null, '', next || window.location.pathname + window.location.search);
    }
}

// ---------- Search ----------

function setupSearch() {
    const modal = document.getElementById('search-modal');
    const toggleBtn = document.getElementById('search-toggle');
    const closeBtn = document.getElementById('close-search');
    const submitBtn = document.getElementById('search-btn');
    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');

    if (!modal || !toggleBtn || !submitBtn || !input || !results) return;

    const open = () => {
        modal.classList.add('active');
        setTimeout(() => input.focus(), 0);
    };
    const close = () => {
        modal.classList.remove('active');
        results.innerHTML = '';
    };

    toggleBtn.addEventListener('click', open);
    closeBtn?.addEventListener('click', close);
    modal.addEventListener('click', (e) => { if (e.target === modal) close(); });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) close();
    });

    const run = () => {
        const query = input.value.trim();
        const scope = document.querySelector('input[name="searchScope"]:checked')?.value || 'all';
        if (!query) { results.innerHTML = '<p class="search-empty">Enter a search term.</p>'; return; }
        const matches = runSearch(query, scope);
        renderSearchResults(results, query, matches, close);
    };
    submitBtn.addEventListener('click', run);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); run(); }
    });
}

function runSearch(query, scope) {
    const needle = query.toLowerCase();
    const engines = scope === 'all'
        ? Object.keys(engineData).filter(k => k !== 'HOME')
        : [currentEngine].filter(k => k && k !== 'HOME' && engineData[k]);

    const matches = [];
    for (const engineId of engines) {
        const engine = engineData[engineId];
        if (!engine?.categories) continue;
        const cats = scope === 'page' && currentCategory
            ? [currentCategory].filter(c => engine.categories[c])
            : Object.keys(engine.categories);
        for (const cat of cats) {
            const body = engine.categories[cat]?.content?.body || '';
            const text = stripHtml(body);
            const lower = text.toLowerCase();
            const idx = lower.indexOf(needle);
            if (idx === -1) continue;
            const start = Math.max(0, idx - 60);
            const end = Math.min(text.length, idx + needle.length + 100);
            const before = (start > 0 ? '…' : '') + text.slice(start, idx);
            const hit = text.slice(idx, idx + needle.length);
            const after = text.slice(idx + needle.length, end) + (end < text.length ? '…' : '');
            matches.push({ engineId, category: cat, before, hit, after });
            if (matches.length >= 50) return matches;
        }
    }
    return matches;
}

function stripHtml(html) {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return (tmp.textContent || '').replace(/\s+/g, ' ').trim();
}

function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function renderSearchResults(container, query, matches, closeModal) {
    if (matches.length === 0) {
        container.innerHTML = `<div class="no-results">No matches for <strong>${escapeHtml(query)}</strong>.</div>`;
        return;
    }
    const items = matches.map((m, i) => `
        <div class="search-result-item" data-result-index="${i}" tabindex="0" role="link">
            <div class="search-result-title">${m.engineId} &rsaquo; ${m.category}</div>
            <div class="search-result-excerpt">${escapeHtml(m.before)}<mark>${escapeHtml(m.hit)}</mark>${escapeHtml(m.after)}</div>
        </div>`).join('');
    container.innerHTML = `<div class="search-result-summary">${matches.length} match${matches.length === 1 ? '' : 'es'} for <strong>${escapeHtml(query)}</strong></div>${items}`;

    const navigateTo = async (m) => {
        closeModal();
        await selectEngine(m.engineId);
        if (m.category !== 'description') await selectCategory(m.category);
    };
    container.querySelectorAll('.search-result-item').forEach(item => {
        const m = matches[Number(item.dataset.resultIndex)];
        item.addEventListener('click', () => navigateTo(m));
        item.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); navigateTo(m); }
        });
    });
}

// ---------- Boot ----------

document.addEventListener('DOMContentLoaded', async () => {
    await init();
    // setupHashRouter() inside init() already routed to the URL's hash (or HOME if empty/invalid).
});
