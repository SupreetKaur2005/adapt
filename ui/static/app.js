let pollInterval;
let currentSimId = null;
let resultsChartInstance = null;

function switchTab(tabId) {
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    
    document.querySelector(`.tab[onclick="switchTab('${tabId}')"]`).classList.add('active');
    document.getElementById(`tab-${tabId}`).classList.add('active');
}

function updateFileLabel(input) {
    const label = document.getElementById('file-label');
    if (input.files.length > 0) {
        label.textContent = `SELECTED: ${input.files[0].name.toUpperCase()}`;
        label.style.background = '#f0f0f0';
        label.style.color = '#111';
    }
}

async function submitGit() {
    const url = document.getElementById('git-url').value;
    if(!url) return alert('Please enter a Git URL');
    
    const rounds = document.getElementById('n-rounds').value || 3;
    
    const formData = new FormData();
    formData.append('repo_url', url);
    formData.append('n_rounds', rounds);
    
    startSimulation(fetch('/api/submit_git', {
        method: 'POST',
        body: formData
    }));
}

async function submitZip() {
    const fileInput = document.getElementById('zip-file');
    if(!fileInput.files[0]) return alert('Please select a ZIP archive');
    
    const rounds = document.getElementById('n-rounds').value || 3;
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('n_rounds', rounds);
    
    startSimulation(fetch('/api/submit_zip', {
        method: 'POST',
        body: formData
    }));
}

async function startSimulation(fetchPromise) {
    document.getElementById('input-section').classList.add('hidden');
    document.getElementById('dashboard-section').classList.remove('hidden');
    document.getElementById('results-section').classList.add('hidden');
    document.getElementById('loading-bar-container').classList.remove('hidden');
    document.getElementById('log-output').innerHTML = '';
    
    try {
        const res = await fetchPromise;
        const data = await res.json();
        currentSimId = data.sim_id;
        pollStatus();
    } catch(err) {
        console.error(err);
        alert('Failed to start analysis');
        resetUI();
    }
}

function pollStatus() {
    pollInterval = setInterval(async () => {
        if(!currentSimId) return;
        
        const res = await fetch(`/api/status/${currentSimId}`);
        const data = await res.json();
        
        updateLogs(data.logs || []);
        
        if (data.status === 'completed' || data.status === 'error') {
            clearInterval(pollInterval);
            document.getElementById('sim-status').textContent = data.status.toUpperCase();
            document.getElementById('sim-status').className = data.status === 'error' ? 'red-text' : 'green-text';
            document.getElementById('loading-bar-container').classList.add('hidden');
            if (data.result) {
                showResults(data.result);
            }
        }
    }, 1000);
}

let displayedLogs = 0;
function updateLogs(logs) {
    const container = document.getElementById('log-output');
    for(let i = displayedLogs; i < logs.length; i++) {
        const line = document.createElement('div');
        line.className = 'log-line';
        line.textContent = `> ${logs[i]}`;
        container.appendChild(line);
        container.scrollTop = container.scrollHeight;
    }
    displayedLogs = logs.length;
}

function showResults(result) {
    document.getElementById('results-section').classList.remove('hidden');
    
    document.getElementById('stat-tested').textContent = result.techniques_tested;
    document.getElementById('stat-passed').textContent = result.passed;
    document.getElementById('stat-blocked').textContent = result.blocked;
    
    if (result.estimated_cost !== undefined) {
        document.getElementById('stat-cost').textContent = '$' + result.estimated_cost.toFixed(3);
    }
    
    const vulnList = document.getElementById('vuln-list');
    vulnList.innerHTML = '';
    if (result.vulnerabilities_found && result.vulnerabilities_found.length > 0) {
        result.vulnerabilities_found.forEach(v => {
            const li = document.createElement('li');
            li.className = 'vuln-item';
            li.innerHTML = `
                <span><strong>${v.type}</strong><br><span style="color:#666; font-size:0.85rem;">Target: ${v.path}</span></span>
                <span class="red-text" style="font-weight:700;">${v.severity}</span>
            `;
            vulnList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'vuln-item';
        li.innerHTML = `<span>No critical vulnerabilities found or exploited.</span>`;
        vulnList.appendChild(li);
    }

    if (result.graph_url) {
        document.getElementById('graph-container').classList.remove('hidden');
        document.getElementById('cfg-graph-img').src = result.graph_url;
    } else {
        document.getElementById('graph-container').classList.add('hidden');
    }

    renderChart(result.passed, result.blocked);
}

function renderChart(passed, blocked) {
    const ctx = document.getElementById('resultChart').getContext('2d');
    
    if (resultsChartInstance) {
        resultsChartInstance.destroy();
    }
    
    resultsChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Breaches', 'Blocks'],
            datasets: [{
                data: [passed, blocked],
                backgroundColor: [
                    '#d90000', // Swiss Red
                    '#111111'  // Black
                ],
                borderColor: [
                    '#d90000',
                    '#111111'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#f0f0f5',
                        font: {
                            family: '"Inter", -apple-system, sans-serif',
                            weight: 'bold'
                        }
                    }
                }
            }
        }
    });
}

function resetUI() {
    clearInterval(pollInterval);
    currentSimId = null;
    displayedLogs = 0;
    
    if (resultsChartInstance) {
        resultsChartInstance.destroy();
        resultsChartInstance = null;
    }
    
    document.getElementById('sim-status').textContent = 'INITIALIZING';
    document.getElementById('sim-status').className = 'status-running';
    document.getElementById('loading-bar-container').classList.add('hidden');
    
    document.getElementById('dashboard-section').classList.add('hidden');
    document.getElementById('input-section').classList.remove('hidden');
    document.getElementById('git-url').value = '';
    document.getElementById('zip-file').value = '';
}

async function downloadReport() {
    if (currentSimId) {
        window.location.href = `/api/download_report/${currentSimId}`;
    } else {
        alert("No simulation currently loaded.");
    }
}
