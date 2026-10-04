from __future__ import annotations

import subprocess
from unittest.mock import patch

from adapt.agents.blue_team.tools.patch_deploy_tool import patch_deploy


@patch("subprocess.run")
def test_patch_deploy(mock_run):
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "patching file test.txt"
    mock_run.return_value.stderr = ""
    
    result = patch_deploy("test_container", "patch diff content")
    
    assert result["target_host"] == "test_container"
    assert result["exit_code"] == 0
    assert result["stdout"] == "patching file test.txt"
    
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0] == ["docker", "exec", "-i", "test_container", "patch", "-p1"]
    assert kwargs["input"] == "patch diff content"


@patch("subprocess.run")
def test_patch_deploy_failure(mock_run):
    mock_run.side_effect = Exception("Docker not found")
    
    result = patch_deploy("test_container", "patch diff content")
    
    assert result["exit_code"] == -1
    assert "Docker not found" in result["stderr"]
