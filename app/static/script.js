// State
let capabilities = {}; // e.g. { ".pdf": ["docx", "png"], ... }
let currentSourceExt = null;
let currentTargetExt = null;

// DOM Elements
const grid = document.getElementById('tools-grid');
const searchInput = document.getElementById('tool-search');
const noResults = document.getElementById('no-results');
const modal = document.getElementById('conversion-modal');
const modalTitle = document.getElementById('modal-title');
const targetGrid = document.getElementById('target-formats-grid');
const closeModalBtn = document.getElementById('close-modal');
const fileInput = document.getElementById('file-input');
const uploadStatus = document.getElementById('upload-status');
const progressBar = document.getElementById('progress-bar');
const statusText = document.getElementById('status-text');
const downloadLink = document.getElementById('download-link');

// Lifecycle
document.addEventListener('DOMContentLoaded', async () => {
    await fetchCapabilities();
    renderGrid(capabilities); // Initial render
});

// 1. Fetch Capabilities
async function fetchCapabilities() {
    try {
        const res = await fetch('/api/v1/capabilities');
        const data = await res.json();
        // Backend returns: { "conversions": { ".jpg": [".png"], ".pdf": [".docx"] } } or similar
        // Adjust based on verified tests from previous turn (Plan C assumption)
        // If backend returns root object as the map, use data directly.
        // Let's assume standardized response format, but if it is straight dict, handled here.
        if (data.conversions) {
            capabilities = data.conversions;
        } else {
            capabilities = data;
        }
        console.log('Loaded capabilities:', capabilities);
    } catch (err) {
        console.error('Failed to load capabilities:', err);
        grid.innerHTML = '<p class="error">Error loading tools. Please try again later.</p>';
    }
}

// 2. Render Grid
function renderGrid(caps, filterQuery = '') {
    grid.innerHTML = '';
    let matches = 0;

    // caps structure: { ".pdf": [".target1", ".target2"] }
    // We want to create cards like "PDF Tools"

    Object.keys(caps).forEach(sourceExt => {
        // Clean extension for display (e.g. .pdf -> PDF)
        const displaySource = sourceExt.replace('.', '').toUpperCase();
        const targets = caps[sourceExt];

        // Search Logic: Match 'PDF', 'Word', '.docx' etc.
        // If filter is empty, show all.
        // If filter exists, check if source OR any target matches.
        const query = filterQuery.toLowerCase();
        const targetsString = targets.join(' ').toLowerCase();
        const sourceString = displaySource.toLowerCase();

        // Check if this card is relevant
        const isMatch = !filterQuery ||
            sourceString.includes(query) ||
            targetsString.includes(query);

        if (isMatch) {
            matches++;
            const card = document.createElement('div');
            card.className = 'tool-card';
            card.innerHTML = `
                <div class="card-icon">📄</div>
                <div class="card-title">${displaySource} Tools</div>
                <div class="card-desc">Convert ${displaySource} to ${targets.length} formats</div>
            `;
            card.onclick = () => openModal(sourceExt, targets);
            grid.appendChild(card);
        }
    });

    if (matches === 0) {
        noResults.classList.remove('hidden');
    } else {
        noResults.classList.add('hidden');
    }
}

// 3. Search Handler
searchInput.addEventListener('input', (e) => {
    const query = e.target.value.trim();
    renderGrid(capabilities, query);
});

// 4. Modal Logic
function openModal(sourceExt, targets) {
    currentSourceExt = sourceExt;

    // Set UI
    const displaySource = sourceExt.replace('.', '').toUpperCase();
    modalTitle.textContent = `Convert ${displaySource} File`;
    targetGrid.innerHTML = ''; // Clear previous

    // Reset status area
    uploadStatus.classList.add('hidden');
    progressBar.style.width = '0%';
    downloadLink.classList.add('hidden');

    // Create target buttons
    targets.forEach(targetExt => {
        const displayTarget = targetExt.replace('.', '').toUpperCase();
        const btn = document.createElement('button');
        btn.className = 'target-btn';
        btn.textContent = `to ${displayTarget}`;
        btn.onclick = () => selectTarget(targetExt);
        targetGrid.appendChild(btn);
    });

    modal.classList.remove('hidden');
}

closeModalBtn.onclick = () => {
    modal.classList.add('hidden');
    // Clear selection state
    currentSourceExt = null;
    currentTargetExt = null;
};

// Start selection flow
function selectTarget(targetExt) {
    currentTargetExt = targetExt;
    console.log(`Selected conversion: ${currentSourceExt} -> ${currentTargetExt}`);
    // Trigger file input
    fileInput.click();
}

// 5. File Upload & Conversion
fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Show Progress
    uploadStatus.classList.remove('hidden');
    statusText.textContent = `Converting ${file.name}...`;
    progressBar.style.width = '30%';

    // Prepare Payload
    const formData = new FormData();
    formData.append('file', file);
    formData.append('target_format', currentTargetExt); // IMPORTANT: Backend needs this

    try {
        progressBar.style.width = '60%';
        const response = await fetch('/api/v1/convert', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Conversion failed');
        }

        // Handle Download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        // Suggest filename
        const contentDisp = response.headers.get('content-disposition');
        let filename = 'converted-file' + currentTargetExt; // Fallback
        if (contentDisp && contentDisp.includes('filename=')) {
            filename = contentDisp.split('filename=')[1].replace(/"/g, '');
        }

        // Update UI Success
        progressBar.style.width = '100%';
        statusText.textContent = "Done!";
        downloadLink.href = url;
        downloadLink.download = filename;
        downloadLink.classList.remove('hidden');

    } catch (error) {
        console.error(error);
        statusText.textContent = `Error: ${error.message}`;
        progressBar.style.backgroundColor = '#ef4444'; // Red
    } finally {
        // Clear input so same file can be selected again
        fileInput.value = '';
    }
});

// Close modal on click outside content
window.onclick = (event) => {
    if (event.target == modal) {
        closeModalBtn.click();
    }
};
