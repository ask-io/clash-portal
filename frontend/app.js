const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const browseBtn = document.getElementById('browse-btn');
const fileDetails = document.getElementById('file-details');
const fileNameSpan = document.getElementById('file-name');
const processBtn = document.getElementById('process-btn');
const statusMessage = document.getElementById('status-message');
const resultsCard = document.getElementById('results-card');
const downloadBtn = document.getElementById('download-btn');

let selectedFile = null;
let serverClashData = null; // Stashes our parsed data array safely in memory

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
        if (resultsCard) resultsCard.classList.add('hidden');
        serverClashData = null;
    }
}

if (processBtn) {
    processBtn.addEventListener('click', async (event) => {
        event.preventDefault();

        if (!selectedFile) return;

        showStatus('Processing your BIM matrix file... Please wait.', 'info');
        processBtn.disabled = true;
        if (resultsCard) resultsCard.classList.add('hidden');

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            // NOTE: Swap 127.0.0.1 for your network IP address when hitting the link from other devices!
            const response = await fetch('http://127.0.0.1:8000/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server returned error status code: ${response.status}`);
            }

            const reply = await response.json();
            console.log("Captured backend response payload:", reply);

            // Handle both structural wrapped variations or raw array arrivals
            let finalData = null;
            if (reply && reply.status === 'success' && reply.data) {
                finalData = reply.data;
            } else if (Array.isArray(reply)) {
                finalData = reply;
            } else if (reply && Array.isArray(reply.data)) {
                finalData = reply.data;
            }

            if (finalData && finalData.length > 0) {
                serverClashData = finalData; // Lock the array into the global scope variable
                showStatus('Matrix processed successfully! Your download link is ready below.', 'success');
                if (resultsCard) resultsCard.classList.remove('hidden'); // Show the green button card
            } else {
                showStatus('Matrix parsed successfully, but zero high-priority conflicts matched tiers 1, 2, or 3.', 'info');
            }

        } catch (error) {
            console.error('Network Parsing Error:', error);
            showStatus(`Processing failed: ${error.message}`, 'error');
        } finally {
            processBtn.disabled = false;
        }
    });
}

// Convert JSON array directly to an Excel-readable spreadsheet layout and download
if (downloadBtn) {
    downloadBtn.addEventListener('click', (event) => {
        event.preventDefault();
        if (!serverClashData || serverClashData.length === 0) return;

        // Create CSV file columns headers string line
        const headers = ["Row Discipline", "Row Element", "Column Discipline", "Column Element", "Priority"];
        
        const csvRows = [headers.join(",")];

        serverClashData.forEach(item => {
            const rowDiscipline = `"${(item['Row Discipline'] || item['row_discipline'] || '').replace(/"/g, '""')}"`;
            const rowElement = `"${(item['Row Element'] || item['row_element'] || '').replace(/"/g, '""')}"`;
            const colDiscipline = `"${(item['Column Discipline'] || item['column_discipline'] || '').replace(/"/g, '""')}"`;
            const colElement = `"${(item['Column Element'] || item['column_element'] || '').replace(/"/g, '""')}"`;
            const priority = `"${item['Priority'] || item['priority'] || ''}"`;

            csvRows.push([rowDiscipline, rowElement, colDiscipline, colElement, priority].join(","));
        });

        const csvContent = csvRows.join("\n");
        
        // Add Excel Byte Order Mark (BOM) to ensure clean cell character encoding rendering
        const blob = new Blob(["\ufeff" + csvContent], { type: 'text/csv;charset=utf-8;' });
        const downloadUrl = window.URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = 'Priority_Clash_Report.csv'; // Directly opens cleanly inside Microsoft Excel
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);
    });
}

function showStatus(message, type) {
    if (!statusMessage) return;
    
    statusMessage.textContent = message;
    statusMessage.className = 'status-message';
    
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