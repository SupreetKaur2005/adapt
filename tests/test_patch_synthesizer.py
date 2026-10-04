from __future__ import annotations

from adapt.agents.blue_team.patch_synthesizer import synthesize_patch

def test_synthesize_patch(mock_ollama_client):
    breach = {"event": "buffer_overflow", "process": "vulnerable_app"}
    class DummyGraph:
        nodes = [1, 2, 3]

    graphs = {"CFG": DummyGraph()}
    
    mock_ollama_client.generate.return_value = "--- a/test\n+++ b/test\n@@ -1 +1 @@\n-vuln\n+fixed"
    
    patch = synthesize_patch(breach, graphs, model_client=mock_ollama_client)
    
    assert patch.file_path == "unknown"
    assert patch.description == "Auto-generated patch"
    assert "fixed" in patch.diff
    mock_ollama_client.generate.assert_called_once()


def test_synthesize_patch_structured(mock_ollama_client):
    breach = {"event": "sqli", "target": "auth.py"}
    mock_ollama_client.generate.return_value = (
        "File: src/auth.py\n"
        "Description: Sanitize user input in SQL query\n"
        "```diff\n"
        "--- a/src/auth.py\n"
        "+++ b/src/auth.py\n"
        "@@ -10,3 +10,3 @@\n"
        "-query = f'SELECT * FROM users WHERE user={u}'\n"
        "+query = 'SELECT * FROM users WHERE user=?'\n"
        "```"
    )

    patch = synthesize_patch(breach, {}, model_client=mock_ollama_client)

    assert patch.file_path == "src/auth.py"
    assert patch.description == "Sanitize user input in SQL query"
    assert "SELECT * FROM users WHERE user=?" in patch.diff
