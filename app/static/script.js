// DOM Elements
const searchInput = document.getElementById('searchInput');
const toolsGrid = document.getElementById('toolsGrid');
const uploadModal = document.getElementById('uploadModal');
const closeModalBtn = document.getElementById('closeModal');
const modalTitle = document.getElementById('modalTitle');
const modalFormatInfo = document.getElementById('modalFormatInfo');

// Modal Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileSelectBtn = document.getElementById('fileSelectBtn');
const progressSection = document.getElementById('progressSection');
const progressBar = document.getElementById('progressBar');
const statusText = document.getElementById('statusText');
const fileNameDisplay = document.getElementById('fileName');
const resultSection = document.getElementById('resultSection');
const downloadBtn = document.getElementById('downloadBtn');
const resetBtn = document.getElementById('resetBtn');
const errorMessage = document.getElementById('errorMessage');

// State
let capabilities = {}; // { ".pdf": [".docx", ".png"], ... }
let currentConversion = { source: null, target: null }; // { source: ".pdf", target: ".docx" }
let currentBlob = null;
let currentFilename = "";

// Initialization
document.addEventListener('DOMContentLoaded', async () => {
    await fetchCapabilities();
    renderGrid();
    setupEventListeners();
});

// 1. Fetch Capabilities
async function fetchCapabilities() {
    try {
        const res = await fetch('/api/v1/capabilities');
        if (!res.ok) throw new Error('Failed to fetch tools');
        capabilities = await res.json();
    } catch (err) {
        console.error(err);
        toolsGrid.innerHTML = `<div class="error-message">Failed to load tools. Please refresh.</div>`;
    }
}

// 2. Render Grid
function renderGrid(filterText = "") {
    toolsGrid.innerHTML = "";
    filterText = filterText.toLowerCase();

    Object.keys(capabilities).forEach(sourceExt => {
        const targets = capabilities[sourceExt];
        // Filter logic: Check if source or any target matches filter
        const sourceName = sourceExt.replace('.', '').toUpperCase();
        const matchesSource = sourceName.toLowerCase().includes(filterText);

        const matchingTargets = targets.filter(t => {
            const targetName = t.replace('.', '').toUpperCase();
            return matchesSource || targetName.toLowerCase().includes(filterText);
        });

        if (matchingTargets.length > 0) {
            const card = createToolCard(sourceExt, matchingTargets);
            toolsGrid.appendChild(card);
        }
    });

    if (toolsGrid.innerHTML === "") {
        toolsGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">No tools found matching "${filterText}"</div>`;
    }
}

function createToolCard(sourceExt, targets) {
    const sourceName = sourceExt.replace('.', '').toUpperCase();

    // Icon mapping (simple)
    let icon = "📄";
    if (['.jpg', '.png', '.jpeg', '.webp'].includes(sourceExt)) icon = "🖼️";
    if (sourceExt === '.pdf') icon = "📕";
    if (sourceExt === '.json') icon = "💻";

    const div = document.createElement('div');
    div.className = 'tool-card';
    div.innerHTML = `
        <div class="tool-header">
            <div class="tool-icon">${icon}</div>
            <div class="tool-title">${sourceName} Converter</div>
        </div>
        <div class="target-list">
            ${targets.map(t => {
        const targetName = t.replace('.', '').toUpperCase();
        return `<button class="target-btn" data-source="${sourceExt}" data-target="${t}">to ${targetName}</button>`;
    }).join('')}
        </div>
    `;

    // Add click handlers for buttons
    div.querySelectorAll('.target-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation(); // prevent card click if we add one
            const s = btn.dataset.source;
            const t = btn.dataset.target;
            openModal(s, t);
        });
    });

    return div;
}

// 3. Search Listener
searchInput.addEventListener('input', (e) => {
    renderGrid(e.target.value);
});


// 4. Modal Logic
function openModal(source, target) {
    currentConversion = { source, target };

    // UI Updates
    modalTitle.textContent = `${source.toUpperCase()} to ${target.toUpperCase()}`;
    modalFormatInfo.textContent = `Supports: ${source} -> ${target}`;

    resetUI(); // Reset upload state
    uploadModal.classList.remove('hidden');
}

closeModalBtn.addEventListener('click', () => {
    uploadModal.classList.add('hidden');
});

// Close click outside
window.addEventListener('click', (e) => {
    if (e.target === uploadModal) {
        uploadModal.classList.add('hidden');
    }
});


// 5. Upload Handling (Reused logic)
function setupEventListeners() {
    fileSelectBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length) handleFile(files[0]);
    });

    resetBtn.addEventListener('click', resetUI);
    downloadBtn.addEventListener('click', () => {
        if (currentBlob) {
            const url = window.URL.createObjectURL(currentBlob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = currentFilename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        }
    });
}

function handleFileSelect(e) {
    if (e.target.files.length) handleFile(e.target.files[0]);
}

function handleFile(file) {
    // Validate Extension?? Backend does it, but we could too.
    // For now, let's just upload.

    // Reset state
    errorMessage.classList.add('hidden');
    resultSection.classList.add('hidden');

    // Show progress
    dropZone.classList.add('hidden');
    progressSection.classList.remove('hidden');
    fileNameDisplay.textContent = file.name;
    statusText.textContent = "Uploading & Converting...";
    progressBar.style.width = '30%';

    uploadFile(file);
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    // CRITICAL: Append target format
    formData.append('target_format', currentConversion.target);

    try {
        const response = await fetch('/api/v1/convert', {
            method: 'POST',
            body: formData
        });

        progressBar.style.width = '80%';

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Conversion failed');
        }

        // Get filename
        const disposition = response.headers.get('content-disposition');
        let filename = 'converted-file';
        if (disposition && disposition.indexOf('attachment') !== -1) {
            const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
            const matches = filenameRegex.exec(disposition);
            if (matches != null && matches[1]) {
                filename = matches[1].replace(/['"]/g, '');
            }
        }
        currentFilename = filename;

        currentBlob = await response.blob();

        // Complete
        progressBar.style.width = '100%';
        setTimeout(() => {
            progressSection.classList.add('hidden');
            resultSection.classList.remove('hidden');
        }, 500);

    } catch (error) {
        showError(error.message);
    }
}

function showError(msg) {
    progressSection.classList.add('hidden');
    dropZone.classList.remove('hidden');
    errorMessage.textContent = msg;
    errorMessage.classList.remove('hidden');
}

function resetUI() {
    resultSection.classList.add('hidden');
    progressSection.classList.add('hidden');
    errorMessage.classList.add('hidden');
    dropZone.classList.remove('hidden');
    fileInput.value = '';
    currentBlob = null;
    progressBar.style.width = '0%';
}
