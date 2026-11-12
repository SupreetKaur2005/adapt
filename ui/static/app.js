/**
 * A.D.A.P.T. // Front-End Orchestration & Nano-Texture Visual Engine
 * Minimalist Experimental Technology Architecture
 */

let pollInterval = null;
let stopwatchInterval = null;
let simulationStartTime = null;
let currentSimId = null;
let resultsChartInstance = null;
let displayedLogs = 0;

// ==========================================
// 1. NANO-TEXTURE COMPUTATIONAL ARCHITECTURE
// ==========================================
class NanoTextureEngine {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.mouse = { x: 0.5, y: 0.5, targetX: 0.5, targetY: 0.5 };
        this.width = 0;
        this.height = 0;
        this.dpr = window.devicePixelRatio || 1;
        this.time = 0;
        this.isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        this.isRunning = true;

        this.init();
    }

    init() {
        this.resize();
        window.addEventListener('resize', () => this.resize());
        window.addEventListener('mousemove', (e) => {
            this.mouse.targetX = e.clientX / window.innerWidth;
            this.mouse.targetY = e.clientY / window.innerHeight;
        });

        document.addEventListener('visibilitychange', () => {
            this.isRunning = !document.hidden;
            if (this.isRunning) this.render();
        });

        // Initialize grid lattice structures
        this.generateLattice();
        this.render();
    }

    resize() {
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.canvas.width = this.width * this.dpr;
        this.canvas.height = this.height * this.dpr;
        this.ctx.scale(this.dpr, this.dpr);
    }

    generateLattice() {
        // Computational semiconductor blocks & rectilinear interconnects
        this.blocks = [];
        const cols = 8;
        const rows = 5;
        const cellW = 180;
        const cellH = 140;

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                if (Math.random() > 0.35) {
                    this.blocks.push({
                        col: c,
                        row: r,
                        baseX: c * cellW + (c % 2 === 0 ? 20 : 60),
                        baseY: r * cellH + 30,
                        w: cellW * (0.45 + Math.random() * 0.45),
                        h: cellH * (0.4 + Math.random() * 0.4),
                        depth: 1 + Math.random() * 1.5,
                        hasVias: Math.random() > 0.5,
                        id: `0x${((c * 17 + r * 31) % 255).toString(16).toUpperCase().padStart(2, '0')}`
                    });
                }
            }
        }
    }

    render() {
        if (!this.isRunning) return;

        // Smooth mouse dampening
        this.mouse.x += (this.mouse.targetX - this.mouse.x) * 0.04;
        this.mouse.y += (this.mouse.targetY - this.mouse.y) * 0.04;

        if (!this.isReducedMotion) {
            this.time += 0.005;
        }

        const ctx = this.ctx;
        ctx.clearRect(0, 0, this.width, this.height);

        // Dark monolithic base
        ctx.fillStyle = '#08090B';
        ctx.fillRect(0, 0, this.width, this.height);

        // 1. Layer: Fine Silicon Nanoscale Coordinate Grid
        const gridSize = 40;
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.022)';
        ctx.lineWidth = 0.5;

        ctx.beginPath();
        for (let x = 0; x < this.width; x += gridSize) {
            ctx.moveTo(x, 0);
            ctx.lineTo(x, this.height);
        }
        for (let y = 0; y < this.height; y += gridSize) {
            ctx.moveTo(0, y);
            ctx.lineTo(this.width, y);
        }
        ctx.stroke();

        // 2. Layer: Sub-micron Semiconductor Strata & Silicon Blocks
        const parallaxX = (this.mouse.x - 0.5) * 20;
        const parallaxY = (this.mouse.y - 0.5) * 20;

        for (const block of this.blocks) {
            const bx = block.baseX + parallaxX * block.depth;
            const by = block.baseY + parallaxY * block.depth;

            // Block surface
            ctx.fillStyle = 'rgba(17, 19, 23, 0.7)';
            ctx.fillRect(bx, by, block.w, block.h);

            // Subtle beveled edge
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
            ctx.lineWidth = 1;
            ctx.strokeRect(bx, by, block.w, block.h);

            // Internal micro-texture grooves
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.02)';
            ctx.beginPath();
            ctx.moveTo(bx + 10, by + block.h / 2);
            ctx.lineTo(bx + block.w - 10, by + block.h / 2);
            ctx.stroke();

            // Precision micro-via pads
            if (block.hasVias && block.w > 60) {
                ctx.fillStyle = 'rgba(255, 255, 255, 0.08)';
                ctx.fillRect(bx + 8, by + 8, 4, 4);
                ctx.fillRect(bx + block.w - 12, by + 8, 4, 4);
                ctx.fillRect(bx + 8, by + block.h - 12, 4, 4);
                ctx.fillRect(bx + block.w - 12, by + block.h - 12, 4, 4);
            }
        }

        // 3. Layer: Microscopic Circuit Pathways (Rectilinear Traces)
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (let i = 0; i < 6; i++) {
            const startY = 120 + i * 160 + parallaxY * 0.5;
            ctx.moveTo(0, startY);
            ctx.lineTo(this.width * 0.35, startY);
            ctx.lineTo(this.width * 0.42, startY + 40);
            ctx.lineTo(this.width * 0.75, startY + 40);
            ctx.lineTo(this.width * 0.82, startY);
            ctx.lineTo(this.width, startY);
        }
        ctx.stroke();

        // 4. Subtle Specular Highlight Beam (simulating macro lens angle)
        const lightX = this.mouse.x * this.width;
        const lightY = this.mouse.y * this.height;
        const grad = ctx.createRadialGradient(lightX, lightY, 40, lightX, lightY, 500);
        grad.addColorStop(0, 'rgba(67, 137, 232, 0.035)');
        grad.addColorStop(0.5, 'rgba(255, 255, 255, 0.015)');
        grad.addColorStop(1, 'rgba(0, 0, 0, 0)');

        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, this.width, this.height);

        // 5. Scientific Fiducial Markers (+)
        ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.font = '9px "IBM Plex Mono", monospace';
        const fiducials = [
            { x: 40, y: 40, label: 'FINFET [STRATUM_01]' },
            { x: this.width - 180, y: 40, label: 'SUB-MICRON 0.7nm' },
            { x: 40, y: this.height - 40, label: 'LATTICE 0x8F' },
            { x: this.width - 180, y: this.height - 40, label: 'INTERCONNECT: NOMINAL' }
        ];

        for (const fid of fiducials) {
            ctx.fillText(`+ ${fid.label}`, fid.x, fid.y);
        }

        requestAnimationFrame(() => this.render());
    }
}

// Initialize Nano-Texture Engine on load
window.addEventListener('DOMContentLoaded', () => {
    new NanoTextureEngine('nano-substrate');
});

// ==========================================
// VIEW SWITCHER (OVERVIEW vs RANGE CONSOLE)
// ==========================================
function setAppView(view) {
    const landing = document.getElementById('landing-section');
    const rangeConsole = document.getElementById('console-section');
    const btnOverview = document.getElementById('btn-view-overview');
    const btnConsole = document.getElementById('btn-view-console');

    if (view === 'console') {
        landing.classList.add('hidden');
        rangeConsole.classList.remove('hidden');
        btnOverview.classList.remove('active');
        btnConsole.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
        landing.classList.remove('hidden');
        rangeConsole.classList.add('hidden');
        btnOverview.classList.add('active');
        btnConsole.classList.remove('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function scrollToElement(id) {
    const el = document.getElementById(id);
    if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
    }
}

// ==========================================
// INTERACTIVE ARCHITECTURE DIAGRAM
// ==========================================
const ARCH_NODES = {
    ingest: {
        title: "01 // Target Code Analysis (AST / CFG / DFG / PDG)",
        phase: "STAGE 01 // STATIC & SEMANTIC ANALYSIS",
        desc: "Aggregates source code from the target repository or uploaded archive. Analyzes program semantics by building four interconnected graph representations: Abstract Syntax Tree (AST), Control Flow Graph (CFG), Data Flow Graph (DFG), and Program Dependence Graph (PDG) to isolate exact control paths and data flow vulnerabilities.",
        inputs: "Raw Python source files, Git repository URI, or ZIP archive",
        outputs: "Graph Bundle { ast, cfg, dfg, pdg, source_code }",
        pathId: "path-1"
    },
    router: {
        title: "02 // TOPAZ Dynamic Model Router",
        phase: "STAGE 02 // CUV COST-UTILITY OPTIMIZATION",
        desc: "Evaluates the active subtask and ATT&CK technique against candidate local models (lightweight, mid, heavy) via the CUV equation: CUV = (P(success) × Stealth) / (Cost × Time). Warm-started from previous rounds using CSIM episodic memory.",
        inputs: "Current subtask description, mapped MITRE ATT&CK technique, CSIM history",
        outputs: "Selected ModelHandle (tier + model name, e.g. qwen2.5:0.5b via Ollama)",
        pathId: "path-2"
    },
    red: {
        title: "03 // Red Team Offensive Agent",
        phase: "STAGE 03 // ADVERSARIAL EXPLOITATION & MUTATION",
        desc: "Executes autonomous attack iterations using ReAct loops. On initial attempts, generates candidate exploits directly from code graph representations. If a previous attempt produced a PIVOT verdict, payloads are dynamically mutated using Atomic Red Team playbooks.",
        inputs: "Program dependence graphs, MITRE technique ID, active model handle",
        outputs: "Candidate ExploitAttempt (payload, target host, technique metadata)",
        pathId: "path-3"
    },
    roe: {
        title: "04 // Rules-of-Engagement (RoE) Contract Gate",
        phase: "STAGE 04 // MATHEMATICAL SAFETY ENFORCEMENT",
        desc: "The single, zero-bypass gatekeeper check(action, contract). Enforces type-level immutable FrozenConstraints (prohibited subnets, max execution time, absolute banned tools). Any violation triggers immediate BLOCK and writes to data/audit/audit_log.jsonl.",
        inputs: "Proposed agent action dictionary, active RoEContract K_t",
        outputs: "EnforcementResult (allowed: bool, reason: str)",
        pathId: "path-4"
    },
    sandbox: {
        title: "05 // Isolated Target Sandbox",
        phase: "STAGE 05 // SEALED EXECUTION ENVIRONMENT",
        desc: "Hosts real target applications and an Active Directory / Kerberos domain controller within Mininet network namespaces. Network isolation is enforced via iptables forward-drop rules, preventing any traffic from escaping to the host network.",
        inputs: "Validated exploit execution actions, target host network interfaces",
        outputs: "Target runtime reactions, socket state transitions, execution responses",
        pathId: "path-5"
    },
    telemetry: {
        title: "06 // Live Kernel Observability (eBPF + Sysmon)",
        phase: "STAGE 06 // CONTINUOUS TELEMETRY PROBES",
        desc: "Observes target behavior at the kernel level. Kernel eBPF probes intercept socket connects and process spawns, while Sysmon-for-Linux captures raw event logs. All telemetry is streamed directly to Blue Team ingestion without polling.",
        inputs: "Kernel socket events, syscall triggers, process execution trees",
        outputs: "Stream of TelemetryEvent models (event_id, source, host, raw metrics)",
        pathId: "path-6"
    },
    blue: {
        title: "07 // Blue Team Defensive Remediation Agent",
        phase: "STAGE 07 // AUTONOMOUS DEFENSIVE SYNTHESIS",
        desc: "Consumes telemetry event streams and target code graphs. Calls the routed defensive LLM tier to synthesize clean, unified code diffs that remediate the flaw, and automatically generates YARA detection signatures for threat monitoring.",
        inputs: "Telemetry event batch, target source code graph, breach context",
        outputs: "Code Patch (file_path, diff, description) and YARA detection rules",
        pathId: "path-7"
    },
    triage: {
        title: "08 // Triage Gateway Arbitration",
        phase: "STAGE 08 // CONFLICT ARBITRATION GATEWAY",
        desc: "Arbitrates the round outcome between Red Team infiltration success and Blue Team remediation efficacy: PASS (breach verified & successfully patched), BLOCK (RoE violated or remediation failed), or PIVOT (exploit failed, triggers payload mutation).",
        inputs: "Red outcome, Blue outcome, RoE contract verification criteria",
        outputs: "TriageOutcome (verdict: PASS | BLOCK | PIVOT, arbitration rationale)",
        pathId: "path-8"
    },
    csim: {
        title: "09 // CSIM Episodic Memory (\"Vaccine Registry\")",
        phase: "STAGE 09 // EPISODIC VECTOR LEARNING",
        desc: "Upon receiving a PASS verdict, the exploit/patch pair is vectorized and committed to the local CSIM Chroma vector registry. In subsequent rounds, task_estimator performs cosine similarity queries to warm-start predictions and improve routing.",
        inputs: "Verified exploit/patch pair from PASS verdicts, text embeddings",
        outputs: "Persistent vector registry entry, warm-start data for future rounds",
        pathId: "path-9"
    }
};

let autoTraceInterval = null;
let currentArchStepIdx = 0;
const ARCH_STEP_KEYS = ['ingest', 'router', 'red', 'roe', 'sandbox', 'telemetry', 'blue', 'triage', 'csim'];

function selectArchNode(nodeKey) {
    const data = ARCH_NODES[nodeKey];
    if (!data) return;

    // Update active SVG node
    document.querySelectorAll('.svg-node-group').forEach(el => el.classList.remove('active'));
    const targetNode = document.getElementById(`node-${nodeKey}`);
    if (targetNode) targetNode.classList.add('active');

    // Update active toolbar chip
    document.querySelectorAll('.step-chip').forEach(el => el.classList.remove('active'));
    const targetChip = document.getElementById(`chip-${nodeKey}`);
    if (targetChip) targetChip.classList.add('active');

    // Update SVG flow paths
    document.querySelectorAll('.svg-flow-path').forEach(el => el.classList.remove('active'));
    if (data.pathId) {
        const pathEl = document.getElementById(data.pathId);
        if (pathEl) pathEl.classList.add('active');
    }

    // Update Inspector Card
    const titleEl = document.getElementById('inspector-title');
    const phaseEl = document.getElementById('inspector-phase');
    const descEl = document.getElementById('inspector-desc');
    const inputsEl = document.getElementById('inspector-inputs');
    const outputsEl = document.getElementById('inspector-outputs');

    if (titleEl) titleEl.textContent = data.title;
    if (phaseEl) phaseEl.textContent = data.phase;
    if (descEl) descEl.textContent = data.desc;
    if (inputsEl) inputsEl.textContent = data.inputs;
    if (outputsEl) outputsEl.textContent = data.outputs;

    currentArchStepIdx = ARCH_STEP_KEYS.indexOf(nodeKey);
}

function toggleAutoTrace() {
    const btn = document.getElementById('btn-autotrace');
    const textSpan = document.getElementById('autotrace-text');

    if (autoTraceInterval) {
        clearInterval(autoTraceInterval);
        autoTraceInterval = null;
        if (textSpan) textSpan.textContent = 'AUTO-TRACE FLOW';
        if (btn) btn.innerHTML = '<span>AUTO-TRACE FLOW</span> ▶';
    } else {
        if (textSpan) textSpan.textContent = 'PAUSE TRACE';
        if (btn) btn.innerHTML = '<span>PAUSE TRACE</span> ⏸';

        autoTraceInterval = setInterval(() => {
            currentArchStepIdx = (currentArchStepIdx + 1) % ARCH_STEP_KEYS.length;
            selectArchNode(ARCH_STEP_KEYS[currentArchStepIdx]);
        }, 3200);
    }
}

// ==========================================
// 2. TAB & INGESTION HANDLING
// ==========================================
function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

    const activeBtn = document.querySelector(`.tab-btn[onclick="switchTab('${tabId}')"]`);
    if (activeBtn) activeBtn.classList.add('active');

    const activePane = document.getElementById(`tab-${tabId}`);
    if (activePane) activePane.classList.add('active');
}

function updateFileLabel(input) {
    const label = document.getElementById('file-label');
    if (input.files && input.files.length > 0) {
        label.innerHTML = `
            <span style="color: var(--text-primary); font-weight: 600;">SELECTED: ${input.files[0].name.toUpperCase()}</span>
            <span class="sub-text">[READY FOR SANDBOX ISOLATION & AGGREGATION]</span>
        `;
    }
}

function updateTimeEstimate(val) {
    const rounds = Math.max(parseInt(val, 10) || 1, 1);
    const minSec = Math.max(rounds * 10, 5);
    const maxSec = Math.max(rounds * 16, 15);
    const html = `EST. RUNTIME: <strong>~${minSec}–${maxSec}s</strong> (${rounds > 1 ? '~10-15s/round' : 'single round'})`;
    const gitEst = document.getElementById('time-est-git');
    const zipEst = document.getElementById('time-est-zip');
    if (gitEst) gitEst.innerHTML = html;
    if (zipEst) zipEst.innerHTML = html;
}

// ==========================================
// 3. SIMULATION SUBMISSION & ORCHESTRATION
// ==========================================
async function submitGit() {
    const url = document.getElementById('git-url').value.trim();
    if (!url) {
        alert('Please specify a valid Git repository URI');
        return;
    }

    const rounds = document.getElementById('n-rounds-git').value || 3;
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
    if (!fileInput.files || !fileInput.files[0]) {
        alert('Please select or deposit a ZIP archive');
        return;
    }

    const rounds = document.getElementById('n-rounds-zip').value || 3;
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('n_rounds', rounds);

    startSimulation(fetch('/api/submit_zip', {
        method: 'POST',
        body: formData
    }));
}

async function startSimulation(fetchPromise) {
    setAppView('console');
    document.getElementById('input-section').classList.add('hidden');
    document.getElementById('dashboard-section').classList.remove('hidden');
    document.getElementById('loading-bar-container').classList.remove('hidden');
    
    // Reset state & start live stopwatch
    document.getElementById('log-output').innerHTML = '';
    document.getElementById('vuln-section').classList.add('hidden');
    document.getElementById('remediation-section').classList.add('hidden');
    document.getElementById('round-history-section').classList.add('hidden');
    
    const statusBadge = document.getElementById('sim-status-badge');
    statusBadge.textContent = 'EXECUTING EPISODE';
    statusBadge.className = 'badge badge-high';

    simulationStartTime = Date.now();
    const roundsVal = parseInt(document.getElementById('n-rounds-git').value || document.getElementById('n-rounds-zip').value || 3, 10);
    const estSec = Math.max(roundsVal * 14, 15);
    const estElem = document.getElementById('est-total-time');
    if (estElem) estElem.textContent = `~${estSec}s`;

    if (stopwatchInterval) clearInterval(stopwatchInterval);
    const timerElem = document.getElementById('elapsed-timer');
    if (timerElem) timerElem.textContent = '00:00';
    stopwatchInterval = setInterval(() => {
        const diffMs = Date.now() - simulationStartTime;
        const totalSec = Math.floor(diffMs / 1000);
        const mins = Math.floor(totalSec / 60).toString().padStart(2, '0');
        const secs = (totalSec % 60).toString().padStart(2, '0');
        if (timerElem) timerElem.textContent = `${mins}:${secs}`;
    }, 1000);

    displayedLogs = 0;

    try {
        const res = await fetchPromise;
        const data = await res.json();
        currentSimId = data.sim_id;
        pollStatus();
    } catch (err) {
        console.error('Simulation invocation error:', err);
        alert('Failed to initialize A.D.A.P.T. simulation episode.');
        resetUI();
    }
}

// ==========================================
// 4. TELEMETRY POLLING & LOG STREAMING
// ==========================================
function pollStatus() {
    if (pollInterval) clearInterval(pollInterval);

    pollInterval = setInterval(async () => {
        if (!currentSimId) return;

        try {
            const res = await fetch(`/api/status/${currentSimId}`);
            if (!res.ok) return;

            const data = await res.json();
            updateTelemetryLogs(data.logs || []);

            if (data.status === 'completed' || data.status === 'error') {
                clearInterval(pollInterval);
                if (stopwatchInterval) clearInterval(stopwatchInterval);
                document.getElementById('loading-bar-container').classList.add('hidden');

                const statusBadge = document.getElementById('sim-status-badge');
                if (data.status === 'completed') {
                    statusBadge.textContent = 'EPISODE ARBITRATED';
                    statusBadge.className = 'badge badge-success';
                } else {
                    statusBadge.textContent = 'ENGINE FAULT';
                    statusBadge.className = 'badge badge-critical';
                }

                if (data.result) {
                    displayResults(data.result);
                }
            }
        } catch (err) {
            console.error('Telemetry polling exception:', err);
        }
    }, 1000);
}

function updateTelemetryLogs(logs) {
    const container = document.getElementById('log-output');
    const countBadge = document.getElementById('log-count');

    for (let i = displayedLogs; i < logs.length; i++) {
        const text = logs[i];
        const line = document.createElement('div');
        line.className = 'log-entry';

        // Scientific ISO-like micro timestamp
        const now = new Date();
        const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}.${Math.floor(now.getMilliseconds() / 10).toString().padStart(2, '0')}`;

        let highlighted = text.includes('PASS') || text.includes('BLOCK') || text.includes('PIVOT') || text.includes('completed') || text.includes('synthesizing');

        line.innerHTML = `
            <span class="log-prefix">[${timeStr}]</span>
            <span class="log-content ${highlighted ? 'highlight' : ''}">${escapeHtml(text)}</span>
        `;
        container.appendChild(line);
    }

    displayedLogs = logs.length;
    countBadge.textContent = `${displayedLogs} EVENTS`;
    container.scrollTop = container.scrollHeight;
}

// ==========================================
// 5. RESULTS PRESENTATION & CHARTS
// ==========================================
function displayResults(result) {
    // 1. Metric values
    document.getElementById('stat-tested').textContent = result.techniques_tested || 0;
    document.getElementById('stat-passed').textContent = result.passed || 0;
    document.getElementById('stat-blocked').textContent = result.blocked || 0;

    const timeElem = document.getElementById('stat-time');
    const timeSub = document.getElementById('stat-time-sub');
    const execTime = result.elapsed_time ? Number(result.elapsed_time).toFixed(1) : ((Date.now() - (simulationStartTime || Date.now())) / 1000).toFixed(1);
    if (timeElem) timeElem.textContent = `${execTime}s`;
    if (timeSub) {
        const perRound = (Number(execTime) / Math.max(result.techniques_tested || 1, 1)).toFixed(1);
        timeSub.textContent = `~${perRound}s / Round`;
    }

    if (result.estimated_cost !== undefined) {
        document.getElementById('stat-cost').textContent = '$' + Number(result.estimated_cost).toFixed(4);
    }

    // 2. Control Flow Graph Display
    const cfgImg = document.getElementById('cfg-graph-img');
    const chartContainer = document.getElementById('chart-container');
    const vizMeta = document.getElementById('viz-meta');

    if (result.graph_url) {
        cfgImg.src = result.graph_url + '?t=' + Date.now();
        cfgImg.classList.remove('hidden');
        chartContainer.classList.add('hidden');
        vizMeta.textContent = 'CONTROL FLOW GRAPH (AST/CFG)';
    } else {
        cfgImg.classList.add('hidden');
        chartContainer.classList.remove('hidden');
        vizMeta.textContent = 'ARBITRATION OUTCOME RATIO';
        renderMonochromeChart(result.passed || 0, result.blocked || 0);
    }

    // 3. Vulnerability Ledger
    const vulns = result.vulnerabilities_found || [];
    const vulnSection = document.getElementById('vuln-section');
    const vulnTableBody = document.getElementById('vuln-table-body');
    const vulnCounter = document.getElementById('vuln-count-tag');

    vulnTableBody.innerHTML = '';
    if (vulns.length > 0) {
        vulnSection.classList.remove('hidden');
        vulnCounter.textContent = `${vulns.length} VULNERABILITIES IDENTIFIED`;

        vulns.forEach(v => {
            const tr = document.createElement('tr');
            const sev = (v.severity || 'HIGH').toUpperCase();
            const badgeClass = sev === 'CRITICAL' ? 'badge-critical' : (sev === 'HIGH' ? 'badge-high' : 'badge-medium');
            const cvss = v.cvss_score ? Number(v.cvss_score).toFixed(1) : '7.5';

            tr.innerHTML = `
                <td style="font-family: var(--font-mono); font-weight: 500;">${escapeHtml(v.type)}</td>
                <td style="font-family: var(--font-mono); color: var(--text-secondary); font-size: 0.78rem;">${escapeHtml(v.path || 'Target Program')}</td>
                <td><span class="badge badge-medium">${escapeHtml(v.cwe_id || 'CWE-89')}</span></td>
                <td><span class="badge ${badgeClass}">${cvss}</span></td>
                <td><span class="badge ${badgeClass}">${sev}</span></td>
            `;
            vulnTableBody.appendChild(tr);
        });
    } else {
        vulnSection.classList.remove('hidden');
        vulnCounter.textContent = `0 VULNERABILITIES EXPLOITED`;
        vulnTableBody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 2rem;">
                    Substrate verified resilient. No adversarial penetration attempts succeeded within RoE constraints.
                </td>
            </tr>
        `;
    }

    // 4. Synthesized Defensive Patches
    const remediations = result.remediations || [];
    const remSection = document.getElementById('remediation-section');
    const remContainer = document.getElementById('remediation-container');

    remContainer.innerHTML = '';
    if (remediations.length > 0) {
        remSection.classList.remove('hidden');
        remediations.forEach((diff, idx) => {
            const diffBlock = document.createElement('div');
            diffBlock.className = 'diff-container';

            let formattedDiff = '';
            const lines = diff.split('\n');
            formattedDiff += `<span class="diff-line-header">// PATCH MANIFEST #${idx + 1} — AUTONOMOUS REMEDIATION DIFF</span>`;

            lines.forEach(line => {
                if (line.startsWith('+') && !line.startsWith('+++')) {
                    formattedDiff += `<span class="diff-line-add">${escapeHtml(line)}</span>`;
                } else if (line.startsWith('-') && !line.startsWith('---')) {
                    formattedDiff += `<span class="diff-line-del">${escapeHtml(line)}</span>`;
                } else {
                    formattedDiff += `<span>${escapeHtml(line)}</span><br>`;
                }
            });

            diffBlock.innerHTML = formattedDiff;
            remContainer.appendChild(diffBlock);
        });
    }

    // 5. Round History Trace
    const history = result.history || [];
    const histSection = document.getElementById('round-history-section');
    const histTableBody = document.getElementById('round-table-body');

    if (history.length > 0) {
        histSection.classList.remove('hidden');
        histTableBody.innerHTML = '';

        history.forEach(h => {
            const tr = document.createElement('tr');
            const verd = h.verdict || 'PASS';
            const verdBadge = verd === 'PASS' ? 'badge-success' : (verd === 'BLOCK' ? 'badge-critical' : 'badge-high');
            const redDesc = h.red ? `${h.red.technique_id} - ${h.red.technique}` : 'Adversarial Scan';
            const blueDesc = h.blue ? (h.blue.patch_file !== 'unknown' ? `Patch: ${h.blue.patch_file}` : 'Telemetry Capture') : 'Defensive Analysis';

            tr.innerHTML = `
                <td style="font-family: var(--font-mono); font-weight: 600;">ROUND ${h.round}</td>
                <td style="font-family: var(--font-mono); font-size: 0.78rem;">${escapeHtml(redDesc)}</td>
                <td style="font-family: var(--font-mono); font-size: 0.78rem;">${escapeHtml(blueDesc)}</td>
                <td><span class="badge ${verdBadge}">${verd}</span></td>
                <td style="color: var(--text-secondary); font-size: 0.75rem;">${escapeHtml(h.reason || 'RoE Constraint arbitration complete')}</td>
            `;
            histTableBody.appendChild(tr);
        });
    }
}

// Minimalist Monochromatic Chart Render
function renderMonochromeChart(passed, blocked) {
    const ctx = document.getElementById('resultChart').getContext('2d');

    if (resultsChartInstance) {
        resultsChartInstance.destroy();
    }

    resultsChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Red Breaches', 'Blue Remediations'],
            datasets: [{
                data: [passed, Math.max(blocked, 1)],
                backgroundColor: [
                    '#E34D52', // Restrained Red
                    '#48B982'  // Restrained Verified Green
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '76%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#969CA4',
                        boxWidth: 10,
                        padding: 15,
                        font: {
                            family: '"IBM Plex Mono", monospace',
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

// ==========================================
// 6. UTILITY FUNCTIONS
// ==========================================
function resetUI() {
    if (pollInterval) clearInterval(pollInterval);
    if (stopwatchInterval) clearInterval(stopwatchInterval);
    const timerElem = document.getElementById('elapsed-timer');
    if (timerElem) timerElem.textContent = '00:00';
    currentSimId = null;
    displayedLogs = 0;

    if (resultsChartInstance) {
        resultsChartInstance.destroy();
        resultsChartInstance = null;
    }

    document.getElementById('dashboard-section').classList.add('hidden');
    document.getElementById('input-section').classList.remove('hidden');
    document.getElementById('git-url').value = '';
    document.getElementById('zip-file').value = '';

    const label = document.getElementById('file-label');
    label.innerHTML = `
        <span>CLICK TO SELECT OR DEPOSIT TARGET ARCHIVE (.ZIP)</span>
        <span class="sub-text">[MAX SIZE: 100MB // AUTOMATIC PYTHON RECONNAISSANCE]</span>
    `;
}

function downloadReport() {
    if (currentSimId) {
        window.location.href = `/api/download_report/${currentSimId}`;
    } else {
        alert('No simulated episode has been completed.');
    }
}

function escapeHtml(string) {
    if (!string) return '';
    return String(string)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
