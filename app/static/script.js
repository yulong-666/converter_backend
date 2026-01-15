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

let currentBlob = null;
let currentFilename = "";

// Event Listeners
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

function handleFileSelect(e) {
    if (e.target.files.length) handleFile(e.target.files[0]);
}

function handleFile(file) {
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

        // Get filename from header
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
    dropZone.classList.remove('hidden');
    fileInput.value = '';
    currentBlob = null;
    progressBar.style.width = '0%';
}
