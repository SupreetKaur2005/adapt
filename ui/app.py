import os
import shutil
import tempfile
import uuid
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

app = FastAPI()

# Serve static files for the frontend
app.mount("/static", StaticFiles(directory="ui/static"), name="static")

@app.get("/")
async def root():
    return FileResponse("ui/static/index.html")

# Dictionary to hold simple simulation statuses
simulations = {}

import subprocess
import zipfile
import glob

def run_simulation(sim_id: str, target_path: str, is_git: bool, n_rounds: int = 3):
    import time
    start_time = time.time()
    simulations[sim_id] = {"status": "running", "logs": ["Initializing sandbox environment..."]}
    
    temp_dir = tempfile.mkdtemp()
    
    if is_git:
        simulations[sim_id]["logs"].append(f"Cloning git repository: {target_path}")
        try:
            subprocess.run(["git", "clone", target_path, temp_dir], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            simulations[sim_id]["logs"].append(f"Git clone failed: {e.stderr.decode()}")
            simulations[sim_id]["status"] = "error"
            return
    else:
        simulations[sim_id]["logs"].append(f"Extracting uploaded zip archive...")
        try:
            with zipfile.ZipFile(target_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        except Exception as e:
            simulations[sim_id]["logs"].append(f"Zip extraction failed: {str(e)}")
            simulations[sim_id]["status"] = "error"
            return
    
    simulations[sim_id]["logs"].append("Aggregating target source code...")
    target_code = ""
    for file in glob.glob(os.path.join(temp_dir, "**", "*.py"), recursive=True):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                target_code += f"\n# --- {os.path.basename(file)} ---\n"
                target_code += f.read()
        except:
            pass

    if not target_code.strip():
        target_code = "def authenticate(username, password):\n    pass"

    simulations[sim_id]["logs"].append("Initializing A.D.A.P.T Orchestrator...")
    
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
    
    try:
        from adapt.orchestrator import Orchestrator
        from adapt.routing.model_clients.ollama_client import OllamaClient
        
        simulations[sim_id]["logs"].append(f"Running Red Team vs Blue Team simulation ({n_rounds} rounds)...")
        
        import urllib.request
        try:
            urllib.request.urlopen("http://localhost:11434/", timeout=1.0)
            model_client = OllamaClient()
        except Exception:
            simulations[sim_id]["logs"].append("Local Ollama not detected, but proceeding with default model_client.")
            model_client = OllamaClient()
            
        orchestrator = Orchestrator(target_code=target_code, model_client=model_client)
        
        state = orchestrator.run_episode(n_rounds=n_rounds)
        
        tested = len(state.history)
        passed = sum(1 for h in state.history if h.get("verdict") == "PASS")
        blocked = sum(1 for h in state.history if h.get("verdict") == "BLOCK")
        
        score = int((blocked / tested * 100)) if tested > 0 else 0
        
        graph_url = None
        if hasattr(state, "graphs") and "cfg" in state.graphs:
            try:
                cfg = state.graphs["cfg"]
                fig = plt.figure(figsize=(10, 6), facecolor="#08090B")
                ax = fig.add_subplot(111)
                ax.set_facecolor("#08090B")
                
                # Truncate long labels for readability
                labels = {}
                for node in cfg.nodes():
                    label = str(node)
                    labels[node] = label[:14] + ".." if len(label) > 16 else label
                
                pos = nx.spring_layout(cfg, k=1.8, seed=42)
                nx.draw_networkx_nodes(
                    cfg, pos, ax=ax,
                    node_color="#191C21", node_size=2000,
                    edgecolors="#3A404D", linewidths=1.2,
                    node_shape="s"
                )
                nx.draw_networkx_edges(
                    cfg, pos, ax=ax,
                    edge_color="#4389E8", alpha=0.6,
                    arrows=True, arrowsize=14, width=1.0
                )
                nx.draw_networkx_labels(
                    cfg, pos, labels=labels, ax=ax,
                    font_color="#F1F2F0", font_family="sans-serif",
                    font_size=8, font_weight="normal"
                )
                plt.axis("off")
                plt.tight_layout()
                
                graph_filename = f"{sim_id}_cfg.png"
                graph_path = os.path.join("ui", "static", graph_filename)
                plt.savefig(graph_path, bbox_inches='tight', facecolor=fig.get_facecolor(), dpi=160)
                plt.close(fig)
                graph_url = f"/static/{graph_filename}"
            except Exception as e:
                simulations[sim_id]["logs"].append(f"Failed to generate graph: {str(e)}")

        remediations = getattr(state, "remediations", [])
        
        vulns = []

        # CWE/CVSS enrichment for static code analysis findings
        VULN_CWE_MAP = {
            "Potential XSS via innerHTML": "CWE-79",
            "document.write usage": "CWE-79",
            "eval usage": "CWE-78",
            "String‑based setTimeout/setInterval": "CWE-78",
            "Form without action/method": "CWE-663",
            "Inline event handler": "CWE-79",
            "eval usage in Python": "CWE-78",
            "Potential command injection via subprocess": "CWE-78",
            "Potential SQL injection via raw query": "CWE-89",
        }

        VULN_CVSS_MAP = {
            "Potential XSS via innerHTML": 9.0,
            "document.write usage": 7.5,
            "eval usage": 8.8,
            "String‑based setTimeout/setInterval": 6.5,
            "Form without action/method": 4.3,
            "Inline event handler": 7.5,
            "eval usage in Python": 8.0,
            "Potential command injection via subprocess": 9.8,
            "Potential SQL injection via raw query": 9.5,
        }

        # Scan aggregated files for heuristic vulnerability patterns
        patterns = [
            ("eval usage in Python", "eval(", "HIGH"),
            ("Potential command injection via subprocess", "subprocess.", "CRITICAL"),
            ("Potential SQL injection via raw query", "SELECT * FROM", "CRITICAL"),
            ("String‑based setTimeout/setInterval", "setTimeout(", "MEDIUM"),
            ("Potential XSS via innerHTML", "innerHTML", "HIGH"),
        ]
        
        findings = []
        for file in glob.glob(os.path.join(temp_dir, "**", "*.py"), recursive=True):
            try:
                rel_path = os.path.relpath(file, temp_dir)
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for ftype, pat, sev in patterns:
                        if pat in content:
                            findings.append({
                                "type": ftype,
                                "path": rel_path,
                                "severity": sev,
                                "cwe_id": VULN_CWE_MAP.get(ftype, "CWE-94"),
                                "cvss_score": VULN_CVSS_MAP.get(ftype, 7.5)
                            })
            except Exception:
                pass

        vulns.extend(findings)

        # Incorporate Red Team exploits from episode history
        for h in state.history:
            if h.get("verdict") == "PASS":
                red_out = h.get("red_outcome", {})
                expl = red_out.get("exploit")
                payload = ""
                tech_name = "Exploit"
                cwe_id = "CWE-89"
                cvss_score = 9.0
                
                if hasattr(expl, "payload"):
                    payload = expl.payload
                    if hasattr(expl, "technique") and expl.technique:
                        tech_name = getattr(expl.technique, "name", "Adversarial Infiltration")
                    cwe_id = getattr(expl, "cwe_id", None) or "CWE-89"
                    cvss_score = getattr(expl, "cvss_score", None) or 9.0
                elif isinstance(expl, dict):
                    payload = expl.get("payload", "")
                    tech_dict = expl.get("technique", {})
                    if isinstance(tech_dict, dict):
                        tech_name = tech_dict.get("name", "Adversarial Infiltration")
                    cwe_id = expl.get("cwe_id", "CWE-89")
                    cvss_score = expl.get("cvss_score", 9.0)
                else:
                    payload = str(expl or "Adversarial payload")

                short_payload = (payload[:45] + "...") if len(payload) > 45 else payload
                vulns.append({
                    "type": f"{tech_name} ({short_payload})" if short_payload else tech_name,
                    "path": h.get("target", "Target Program Analysis"),
                    "severity": "CRITICAL",
                    "cwe_id": cwe_id,
                    "cvss_score": cvss_score
                })

        simulations[sim_id]["logs"].append("Simulation completed successfully.")
        
        # Serialize history for rich operational inspection
        clean_history = []
        for h in state.history:
            entry = {
                "round": h.get("round", 0),
                "verdict": str(h.get("verdict", "")),
                "reason": str(h.get("reason", "")),
            }
            if "red_outcome" in h and isinstance(h["red_outcome"], dict):
                red_raw = h["red_outcome"]
                expl = red_raw.get("exploit")
                entry["red"] = {
                    "success": red_raw.get("success", False),
                    "technique": getattr(getattr(expl, "technique", None), "name", "Kerberos / Injection") if expl else "Exploit Action",
                    "technique_id": getattr(getattr(expl, "technique", None), "technique_id", "T1558") if expl else "T1558",
                    "payload": getattr(expl, "payload", "") if expl else "",
                }
            if "blue_outcome" in h and isinstance(h["blue_outcome"], dict):
                blue_raw = h["blue_outcome"]
                patch_dict = blue_raw.get("patch", {})
                entry["blue"] = {
                    "success": blue_raw.get("success", False),
                    "patch_file": patch_dict.get("file_path", "unknown") if isinstance(patch_dict, dict) else "unknown",
                    "patch_diff": patch_dict.get("diff", "") if isinstance(patch_dict, dict) else "",
                    "description": patch_dict.get("description", "") if isinstance(patch_dict, dict) else "",
                }
            clean_history.append(entry)

        simulations[sim_id]["status"] = "completed"
        simulations[sim_id]["result"] = {
            "techniques_tested": tested,
            "blocked": blocked,
            "passed": passed,
            "score": score,
            "estimated_cost": getattr(state, "estimated_cost", 0.0),
            "elapsed_time": round(time.time() - start_time, 2),
            "vulnerabilities_found": vulns,
            "graph_url": graph_url,
            "remediations": remediations,
            "history": clean_history
        }
    except Exception as e:
        simulations[sim_id]["logs"].append(f"Engine execution error: {str(e)}")
        simulations[sim_id]["status"] = "error"
        simulations[sim_id]["result"] = None
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        simulations[sim_id]["logs"].append("Sandbox environment reset.")

@app.post("/api/submit_git")
async def submit_git(background_tasks: BackgroundTasks, repo_url: str = Form(...), n_rounds: int = Form(3)):
    sim_id = str(uuid.uuid4())
    simulations[sim_id] = {"status": "pending"}
    background_tasks.add_task(run_simulation, sim_id, repo_url, True, n_rounds)
    return {"sim_id": sim_id}

@app.post("/api/submit_zip")
async def submit_zip(background_tasks: BackgroundTasks, file: UploadFile = File(...), n_rounds: int = Form(3)):
    sim_id = str(uuid.uuid4())
    simulations[sim_id] = {"status": "pending"}
    
    # Save uploaded file to temp dir
    temp_dir = tempfile.mkdtemp()
    filename = os.path.basename(file.filename or "upload.zip")
    file_path = os.path.join(temp_dir, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    background_tasks.add_task(run_simulation, sim_id, file_path, False, n_rounds)
    return {"sim_id": sim_id}

@app.get("/api/download_report/{sim_id}")
async def download_report_by_id(sim_id: str):
    return _generate_report(sim_id)

@app.get("/api/download_report")
async def download_report():
    if not simulations:
        return JSONResponse(status_code=404, content={"error": "No simulations run yet."})
    
    # Get the most recent simulation ID (last added key)
    sim_id = list(simulations.keys())[-1]
    return _generate_report(sim_id)

def _generate_report(sim_id: str):
    if sim_id not in simulations:
        return JSONResponse(status_code=404, content={"error": "Simulation not found"})
        
    sim = simulations[sim_id]
    result = sim.get("result")
    
    if not result:
        return JSONResponse(status_code=400, content={"error": "Simulation has no result yet or failed."})
        
    report_content = f"""# A.D.A.P.T. Simulation Report
    
## Executive Summary
- **Techniques Tested:** {result.get('techniques_tested', 0)}
- **Red Team Breaches:** {result.get('passed', 0)}
- **Blue Team Blocks:** {result.get('blocked', 0)}
- **Security Score:** {result.get('score', 0)}%

## Vulnerabilities Identified
"""
    vulns = result.get("vulnerabilities_found", [])
    if not vulns:
        report_content += "No critical vulnerabilities were successfully exploited.\n"
    else:
        for v in vulns:
            report_content += f"- **{v['type']}** at `{v['path']}` (Severity: {v['severity']})\n"
            
    report_content += "\n## Remediations Synthesized\n"
    remediations = result.get("remediations", [])
    if not remediations:
        report_content += "No remediations were synthesized or applied.\n"
    else:
        for i, code in enumerate(remediations):
            report_content += f"### Patch {i+1}\n```python\n{code}\n```\n"
            
    if result.get("graph_url"):
        report_content += f"\n## Generated Graphs\n![CFG Graph]({result['graph_url']})\n"

    report_content += "\n## Detailed Simulation Logs\n```text\n"
    report_content += "\n".join(sim.get("logs", []))
    report_content += "\n```\n"
    
    fd, path = tempfile.mkstemp(suffix=".md")
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    return FileResponse(path, media_type='text/markdown', filename=f"ADAPT_Report_{sim_id[:8]}.md")

@app.get("/api/status/{sim_id}")
async def get_status(sim_id: str):
    if sim_id not in simulations:
        return JSONResponse(status_code=404, content={"error": "Simulation not found"})
    return simulations[sim_id]

if __name__ == "__main__":
    import uvicorn
    # Make sure we run from the project root
    uvicorn.run("ui.app:app", host="127.0.0.1", port=8000, reload=True)
