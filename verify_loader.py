import sys
sys.path.insert(0, r"d:\adapt\src")
from datasets.atomic_redteam_loader import load_playbooks
print("T1558:", load_playbooks("T1558"))
print("T1003:", load_playbooks("T1003"))