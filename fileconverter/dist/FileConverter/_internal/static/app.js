const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const controls = document.getElementById('controls');
const targetFormat = document.getElementById('targetFormat');
const convertBtn = document.getElementById('convertBtn');
const statusContainer = document.getElementById('statusContainer');
const statusMsg = document.getElementById('statusMsg');
const loader = document.getElementById('loader');
const themeToggle = document.getElementById('themeToggle');

let currentFile = null;

const FORMAT_MAP = {
    'png':  { type: 'image', targets: ['jpg', 'webp'] },
    'jpg':  { type: 'image', targets: ['png', 'webp'] },
    'jpeg': { type: 'image', targets: ['png', 'webp'] },
    'webp': { type: 'image', targets: ['jpg', 'png'] },
    'bmp':  { type: 'image', targets: ['jpg', 'png'] },
    'docx': { type: 'document', targets: ['pdf'] },
    'pptx': { type: 'document', targets: ['pdf'] },
    'xlsx': { type: 'spreadsheet', targets: ['pdf', 'csv'] },
    'pdf':  { type: 'pdf', targets: ['docx', 'png', 'jpg', 'pptx'] },
    'csv':  { type: 'spreadsheet', targets: ['xlsx'] }
};

// Theme management
const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");

function setTheme(isDark) {
    if (isDark) {
        document.body.classList.add("dark-mode");
    } else {
        document.body.classList.remove("dark-mode");
    }
}

setTheme(prefersDarkScheme.matches);

themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
});

prefersDarkScheme.addEventListener("change", (e) => {
    setTheme(e.matches);
});

// Drag and drop handlers
dropZone.addEventListener('click', () => fileInput.click());

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
    dropZone.addEventListener(evt, e => {
        e.preventDefault();
        e.stopPropagation();
    });
});

['dragenter', 'dragover'].forEach(evt => {
    dropZone.addEventListener(evt, () => dropZone.classList.add('dragover'));
});

['dragleave', 'drop'].forEach(evt => {
    dropZone.addEventListener(evt, () => dropZone.classList.remove('dragover'));
});

dropZone.addEventListener('drop', e => {
    if (e.dataTransfer.files.length) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', e => {
    if (e.target.files.length) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    currentFile = file;
    const ext = file.name.split('.').pop().toLowerCase();
    
    fileInfo.textContent = `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
    
    if (FORMAT_MAP[ext]) {
        populateFormats(FORMAT_MAP[ext].targets);
        controls.style.display = 'block';
        hideStatus();
    } else {
        controls.style.display = 'none';
        showStatus('Unsupported file format.', 'error');
    }
}

function populateFormats(targets) {
    targetFormat.innerHTML = '';
    targets.forEach(fmt => {
        const opt = document.createElement('option');
        opt.value = fmt;
        opt.textContent = fmt.toUpperCase();
        targetFormat.appendChild(opt);
    });
}

function showStatus(msg, type = '') {
    statusContainer.style.display = 'block';
    statusMsg.textContent = msg;
    statusMsg.className = 'status-msg ' + type;
    loader.style.display = type === 'error' || type === 'success' ? 'none' : 'block';
}

function hideStatus() {
    statusContainer.style.display = 'none';
}

convertBtn.addEventListener('click', async () => {
    if (!currentFile) return;
    
    const ext = currentFile.name.split('.').pop().toLowerCase();
    const routeInfo = FORMAT_MAP[ext];
    const target = targetFormat.value;
    
    showStatus(`Converting to ${target.toUpperCase()}...`);
    
    if (routeInfo.type === 'image') {
        try {
            await convertImageBrowserSide(currentFile, target);
            showStatus('Conversion complete!', 'success');
        } catch (e) {
            console.error(e);
            showStatus('Failed to convert image in browser. Trying server...', '');
            await convertServerSide(currentFile, routeInfo.type, target);
        }
    } else {
        await convertServerSide(currentFile, routeInfo.type, target);
    }
});

function convertImageBrowserSide(file, targetFmt) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = e => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.getElementById('hiddenCanvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const ctx = canvas.getContext('2d');
                
                if (targetFmt === 'jpg' || targetFmt === 'jpeg') {
                    ctx.fillStyle = "#FFFFFF";
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                }
                
                ctx.drawImage(img, 0, 0);
                
                let mimeType = `image/${targetFmt === 'jpg' ? 'jpeg' : targetFmt}`;
                
                canvas.toBlob(blob => {
                    if (!blob) return reject(new Error('Canvas toBlob failed'));
                    triggerDownload(blob, file.name.replace(/\.[^/.]+$/, "") + '.' + targetFmt);
                    resolve();
                }, mimeType, 0.95);
            };
            img.onerror = reject;
            img.src = e.target.result;
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

async function convertServerSide(file, converterType, targetFmt) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('converter_type', converterType);
    formData.append('target_format', targetFmt);
    
    try {
        const res = await fetch('/convert', {
            method: 'POST',
            body: formData
        });
        
        if (!res.ok) {
            let errorMsg = 'Server error during conversion';
            try {
                const errData = await res.json();
                if (errData.error) errorMsg = errData.error;
            } catch(e) {}
            throw new Error(errorMsg);
        }
        
        const blob = await res.blob();
        let filename = file.name.replace(/\.[^/.]+$/, "") + '.' + targetFmt;
        const disposition = res.headers.get('content-disposition');
        if (disposition && disposition.indexOf('attachment') !== -1) {
            var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
            var matches = filenameRegex.exec(disposition);
            if (matches != null && matches[1]) { 
                filename = matches[1].replace(/['"]/g, '');
            }
        }
        
        triggerDownload(blob, filename);
        showStatus('Conversion complete!', 'success');
        
    } catch (err) {
        console.error(err);
        showStatus(err.message, 'error');
    }
}

function triggerDownload(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
