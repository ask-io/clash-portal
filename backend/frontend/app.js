const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const browseBtn = document.getElementById('browse-btn');
const fileDetails = document.getElementById('file-details');
const fileNameSpan = document.getElementById('file-name');
const processBtn = document.getElementById('process-btn');
const statusMessage = document.getElementById('status-message');

let selectedFile = null;

if (browseBtn && fileInput) {
    browseBtn.addEventListener('click', (e) => {
        e.preventDefault();
        fileInput.click();
    });
}

if (fileInput) {
    fileInput.addEventListener('change', (event) => {
        if (event.target.files.length > 0) {
            selectedFile = event.target.files[0];
            displaySelectedFile();
        }
    });
}

if (dropZone) {
    dropZone.addEventListener('dragover', (event) => {
        event.preventDefault();
        dropZone.style.backgroundColor = "#f0f4ff";
        dropZone.style.borderColor = "#3b82f6";
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.backgroundColor = "";
        dropZone.style.borderColor = "";
    });

    dropZone.addEventListener('drop', (event) => {
        event.preventDefault();
        dropZone.style.backgroundColor = "";
        dropZone.style.borderColor = "";

        if (event.dataTransfer.files.length > 0) {
            selectedFile = event.dataTransfer.files[0];
            displaySelectedFile();
        }
    });
}

function displaySelectedFile() {
    if (selectedFile && fileNameSpan && fileDetails) {
        fileNameSpan.textContent = selectedFile.name;
        fileDetails.classList.remove('hidden');
        if (statusMessage) statusMessage.classList.add('hidden');
    }
}

if (processBtn) {
    processBtn.addEventListener('click', async (event) => {
        event.preventDefault();

        if (!selectedFile) return;

        showStatus('Processing your BIM matrix file... Please wait.', 'info');
        processBtn.disabled = true;

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) throw new Error(`Server returned error: ${response.status}`);
    
    const t1_count = response.headers.get('X-Tier1-Count') || '0';
    const t2_count = response.headers.get('X-Tier2-Count') || '0';
    const t3_count = response.headers.get('X-Tier3-Count') || '0';
    const to_count = response.headers.get('X-TierO-Count') || '0';
    const tna_count = response.headers.get('X-TierNA-Count') || '0';
    const total_count = response.headers.get('X-Total-Count') || '0';

    const blob = await response.blob();
    
    // Create a temporary anchor element and force a browser click
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Priority_Clash_Report.xlsx'; // Force file name
    document.body.appendChild(a);
    a.click(); // Trigger the save dialog
    a.remove(); // Clean up
    
    const dynamicSummary = `
🎉 Priority Clash Report Generated!
---------------------------------------------
• Tier 1 (Critical): ${t1_count} clashes
• Tier 2 (High): ${t2_count} clashes
• Tier 3 (Medium): ${t3_count} clashes
• Tier O (Optional): ${to_count} clashes
• Tier N/A: ${tna_count} entries
---------------------------------------------
Total Filtered Clash Matrix Rows: ${total_count}
    `.trim();
    showStatus(dynamicSummary, 'success');
} catch (error) {
    showStatus('Error: ' + error.message, 'error');
        } finally {
            processBtn.disabled = false;
        }
    });
}

function showStatus(message, type) {
    if (!statusMessage) return;
    
    statusMessage.textContent = message;
    statusMessage.className = 'status-message';
    
    statusMessage.style.whiteSpace = 'pre-wrap';
    statusMessage.style.fontFamily = 'monospace';
    
    if (type === 'success') {
        statusMessage.style.backgroundColor = '#dcfce7';
        statusMessage.style.color = '#15803d';
        statusMessage.style.border = '1px solid #bbf7d0';
    } else if (type === 'error') {
        statusMessage.style.backgroundColor = '#fee2e2';
        statusMessage.style.color = '#b91c1c';
        statusMessage.style.border = '1px solid #fca5a5';
    } else {
        statusMessage.style.backgroundColor = '#eff6ff';
        statusMessage.style.color = '#1d4ed8';
        statusMessage.style.border = '1px solid #bfdbfe';
    }
    
    statusMessage.classList.remove('hidden');
}
// Dynamic Background Mouse Tracker
window.addEventListener('mousemove', (event) => {
    // Calculate cursor positions relative to the visible window viewport area
    const xPosition = event.clientX;
    const yPosition = event.clientY;
    
    // Pass the raw pixel coordinates straight up into our CSS Custom Properties
    document.body.style.setProperty('--mouse-x', `${xPosition}px`);
    document.body.style.setProperty('--mouse-y', `${yPosition}px`);
});