from __future__ import annotations

from adapt.agents.blue_team.yara_rule_generator import generate_yara_rule


def test_generate_yara_rule(mock_ollama_client):
    breach = {"event": "malicious_process", "pid": 1337}
    
    mock_ollama_client.generate.return_value = "rule MaliciousProcess { strings: $a = \"malicious\" condition: $a }"
    
    yara_rule = generate_yara_rule(breach, model_client=mock_ollama_client)
    
    assert "rule MaliciousProcess" in yara_rule
    mock_ollama_client.generate.assert_called_once()
