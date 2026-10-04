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
                plt.figure(figsize=(12, 8))
                
                # Truncate long labels for readability
                labels = {}
                for node in cfg.nodes():
                    label = str(node)
                    labels[node] = label[:12] + ".." if len(label) > 14 else label
                
                pos = nx.spring_layout(cfg, k=2.0, seed=42)
                nx.draw(
                    cfg, pos, labels=labels, with_labels=True, 
                    node_color="#d90000", node_size=2500, 
                    font_color="white", font_weight="bold", font_size=9, 
                    edge_color="#555555", arrows=True, node_shape="o"
                )
                plt.margins(0.15)
                
                graph_filename = f"{sim_id}_cfg.png"
                graph_path = os.path.join("ui", "static", graph_filename)
                plt.savefig(graph_path, bbox_inches='tight', dpi=150)
                plt.close()
                graph_url = f"/static/{graph_filename}"
            except Exception as e:
                simulations[sim_id]["logs"].append(f"Failed to generate graph: {str(e)}")

        remediations = getattr(state, "remediations", [])
        
        vulns = []
        for h in state.history:
            if h.get("verdict") == "PASS":
                payload = h.get("exploit", "Unknown exploit payload")
                # Truncate payload for display
                short_payload = (payload[:50] + "...") if len(payload) > 50 else payload
                vulns.append({
                    "type": f"Red Team Exploit ({short_payload})",
                    "path": h.get("target", "Target Code"),
                    "severity": "Critical"
                })

        simulations[sim_id]["logs"].append("Simulation completed successfully.")
        
        simulations[sim_id]["status"] = "completed"
        simulations[sim_id]["result"] = {
            "techniques_tested": tested,
            "blocked": blocked,
            "passed": passed,
            "score": score,
            "estimated_cost": getattr(state, "estimated_cost", 0.0),
            "vulnerabilities_found": vulns,
            "graph_url": graph_url,
            "remediations": remediations
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
    file_path = os.path.join(temp_dir, file.filename)
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
