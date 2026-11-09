import sys
sys.path.insert(0, r"d:\adapt\src")
from adapt.memory.csim_store import commit, query_similar
from adapt.mitre.attack_mapper import map_to_technique
from adapt.routing.task_estimator import estimate, COLD_START_TABLE
from adapt.schemas import AttackTechnique, ExploitAttempt
from adapt.agents.blue_team.patch_synthesizer import Patch

# 1) mapper
tech = map_to_technique("try kerberoast against DC01")
print("Mapper returned", len(tech), "technique(s)")

# 2) estimator (cold-start, no CSIM history)
subtask = "execute a command on the host"
tech = AttackTechnique(technique_id="T1059", name="Command-Line Interface", tactic="execution", description="")
sr, st = estimate(subtask, tech)
print("Cold-start success/stealth =", sr, st)

# 3) CSIM commit / query (in-memory)
commit(
    ExploitAttempt(subtask="test", technique=tech, payload="echo hello", model_used="qwen2.5:0.5b"),
    Patch(file_path="test.py", diff="@@ -1,3 +1,3 @@\n+echo hello", description="test"),
)
records = query_similar("test")
print("CSIM records after commit:", len(records))